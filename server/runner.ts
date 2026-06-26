// Dev-server execution engine for Polyglot CP.
//
// Each *physical line* of a submission is a complete standalone program in its
// assigned language. Lines are executed as an independent pipeline: the stdout
// of line N becomes the stdin of line N+1. The first stdin is the problem input,
// the last stdout is the answer that gets judged.
//
// Two engines:
//   - local  (keyless, default): runs python3 / node as short-lived processes
//            on THIS machine, one per line, with a hard 5s timeout each.
//   - judge0 (opt-in via .env):  delegates each line to a Judge0 API instance.
//
// SECURITY: the local engine runs your own code on your own machine. It is a PoC
// convenience only. Never expose it to untrusted input. Production must use a
// sandbox (Judge0 / firejail / container).
import type { Plugin } from 'vite';
import { spawn } from 'node:child_process';
import { writeFileSync, mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

export interface RunnerConfig {
  useJudge0: boolean;
  judge0Url: string;
  judge0Key: string;
  judge0Host: string;
}

interface LangSpec {
  ext: string;
  cmd: (file: string) => [string, string[]];
  judge0Id: number;
}

// Only languages that are guaranteed present on this machine are wired for the
// local engine. Add more here (and map a judge0Id) to extend the rotation.
const LANGS: Record<string, LangSpec> = {
  python: { ext: 'py', cmd: (f) => ['python3', [f]], judge0Id: 71 },
  javascript: { ext: 'js', cmd: (f) => ['node', [f]], judge0Id: 63 },
};

const TIMEOUT_MS = 5000;

interface ExecResult {
  stdout: string;
  stderr: string;
  exitCode: number | null;
  timedOut: boolean;
  durationMs: number;
}

function runOneLocal(language: string, code: string, input: string): Promise<ExecResult> {
  return new Promise((resolve) => {
    const spec = LANGS[language];
    const start = Date.now();
    if (!spec) {
      resolve({ stdout: '', stderr: `Unsupported language: ${language}`, exitCode: null, timedOut: false, durationMs: 0 });
      return;
    }
    const dir = mkdtempSync(join(tmpdir(), 'pcp-'));
    const file = join(dir, `main.${spec.ext}`);
    writeFileSync(file, code);
    const [cmd, args] = spec.cmd(file);
    const child = spawn(cmd, args, { stdio: ['pipe', 'pipe', 'pipe'] });

    let stdout = '';
    let stderr = '';
    let timedOut = false;
    const timer = setTimeout(() => {
      timedOut = true;
      child.kill('SIGKILL');
    }, TIMEOUT_MS);

    child.stdout.on('data', (d) => (stdout += d));
    child.stderr.on('data', (d) => (stderr += d));
    child.stdin.on('error', () => {});
    child.on('error', (e) => {
      clearTimeout(timer);
      rmSync(dir, { recursive: true, force: true });
      resolve({ stdout: '', stderr: String(e), exitCode: null, timedOut: false, durationMs: Date.now() - start });
    });
    child.on('close', (exitCode) => {
      clearTimeout(timer);
      rmSync(dir, { recursive: true, force: true });
      resolve({ stdout, stderr, exitCode, timedOut, durationMs: Date.now() - start });
    });

    child.stdin.write(input);
    child.stdin.end();
  });
}

const b64 = (s: string) => Buffer.from(s, 'utf8').toString('base64');
const deb64 = (s: string) => Buffer.from(s, 'base64').toString('utf8');

async function runOneJudge0(language: string, code: string, input: string, config: RunnerConfig): Promise<ExecResult> {
  const spec = LANGS[language];
  const start = Date.now();
  if (!spec) {
    return { stdout: '', stderr: `Unsupported language: ${language}`, exitCode: null, timedOut: false, durationMs: 0 };
  }
  try {
    const headers: Record<string, string> = { 'Content-Type': 'application/json' };
    if (config.judge0Key) {
      headers['X-RapidAPI-Key'] = config.judge0Key;
      headers['X-RapidAPI-Host'] = config.judge0Host;
    }
    const url = `${config.judge0Url.replace(/\/$/, '')}/submissions?base64_encoded=true&wait=true`;
    const r = await fetch(url, {
      method: 'POST',
      headers,
      body: JSON.stringify({ source_code: b64(code), stdin: b64(input), language_id: spec.judge0Id }),
    });
    const j: any = await r.json();
    const stdout = j.stdout ? deb64(j.stdout) : '';
    const stderr = (j.stderr ? deb64(j.stderr) : '') + (j.compile_output ? deb64(j.compile_output) : '');
    const statusId: number | undefined = j.status?.id;
    const timedOut = statusId === 5; // Time Limit Exceeded
    const exitCode = statusId === 3 ? 0 : timedOut ? null : 1; // 3 = Accepted/Finished
    return { stdout, stderr, exitCode, timedOut, durationMs: Date.now() - start };
  } catch (e) {
    return { stdout: '', stderr: `Judge0 request failed: ${e}`, exitCode: null, timedOut: false, durationMs: Date.now() - start };
  }
}

export interface LineResult extends ExecResult {
  lineNo: number;
  language: string;
  code: string;
  stdin: string;
}

export interface RunResponse {
  steps: LineResult[];
  finalOutput: string;
  expected: string;
  verdict: 'AC' | 'WA' | 'RE' | 'TLE';
  engine: 'local' | 'judge0';
}

interface RunRequest {
  code: string;
  languages: string[];
  input: string;
  expected: string;
}

async function handleRun(body: RunRequest, config: RunnerConfig): Promise<RunResponse> {
  const languages = body.languages?.length ? body.languages : ['python'];
  const lines = (body.code ?? '').split('\n');
  const steps: LineResult[] = [];
  let current = body.input ?? '';
  let visibleIdx = 0;
  let verdict: RunResponse['verdict'] = 'AC';

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (line.trim() === '') continue; // empty lines do not consume a rotation slot
    const language = languages[visibleIdx % languages.length];
    visibleIdx++;
    const res = config.useJudge0
      ? await runOneJudge0(language, line, current, config)
      : await runOneLocal(language, line, current);
    steps.push({ lineNo: i + 1, language, code: line, stdin: current, ...res });
    if (res.timedOut) {
      verdict = 'TLE';
      break;
    }
    if (res.exitCode !== 0) {
      verdict = 'RE';
      break;
    }
    current = res.stdout;
  }

  const finalOutput = (current ?? '').trim();
  const expected = String(body.expected ?? '').trim();
  if (verdict === 'AC') verdict = finalOutput === expected ? 'AC' : 'WA';

  return { steps, finalOutput, expected, verdict, engine: config.useJudge0 ? 'judge0' : 'local' };
}

export function runnerPlugin(config: RunnerConfig): Plugin {
  return {
    name: 'polyglot-runner',
    configureServer(server) {
      server.middlewares.use('/api/run', (req, res, next) => {
        if (req.method !== 'POST') {
          next();
          return;
        }
        let raw = '';
        req.on('data', (c) => (raw += c));
        req.on('end', async () => {
          try {
            const body = JSON.parse(raw || '{}') as RunRequest;
            const result = await handleRun(body, config);
            res.setHeader('Content-Type', 'application/json');
            res.end(JSON.stringify(result));
          } catch (e) {
            res.statusCode = 500;
            res.setHeader('Content-Type', 'application/json');
            res.end(JSON.stringify({ error: String(e) }));
          }
        });
      });
    },
  };
}
