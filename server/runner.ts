// Dev-server execution engine for Polyglot CP.
//
// Each *physical line* of a submission is a complete standalone program in its
// assigned language. Lines are executed as an independent pipeline: the stdout
// of line N becomes the stdin of line N+1. The first stdin is the problem input,
// the last stdout is the answer that gets judged.
//
// Two engines:
//   - local  (keyless, default): runs each line as a short-lived process on THIS
//            machine (python3/node/ruby/perl/bash/swift/dart/go/zig + compiled
//            c/c++/rust/java), one per line, with a hard 5s timeout each
//            (compiled langs get a separate 5s budget for the compile step).
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
  file?: string; // source filename override (e.g. Java needs Main.java)
  // run: how to execute the source/binary. Omit = no local runtime (Judge0 only).
  run?: (src: string, dir: string) => [string, string[]];
  // compile: optional build step that must succeed before run (a.out etc.).
  compile?: (src: string, dir: string) => [string, string[]];
  // Judge0 CE language_id. Omit when Judge0 CE has no runtime (e.g. Zig = local only).
  judge0Id?: number;
}

const bin = (dir: string) => join(dir, 'a.out');

// Language table. `run` present => runnable by the local keyless engine (the
// command is detected on this machine). `run` absent => Judge0-only (the runtime
// is not installed locally; enable USE_JUDGE0 to execute it). judge0Id maps to a
// Judge0 CE language_id; entries without one are local-only (no Judge0 CE runtime).
const LANGS: Record<string, LangSpec> = {
  // --- interpreted / single-command (compile happens inside the run command) ---
  python: { ext: 'py', run: (f) => ['python3', [f]], judge0Id: 71 },
  javascript: { ext: 'js', run: (f) => ['node', [f]], judge0Id: 63 },
  ruby: { ext: 'rb', run: (f) => ['ruby', [f]], judge0Id: 72 },
  perl: { ext: 'pl', run: (f) => ['perl', [f]], judge0Id: 85 },
  bash: { ext: 'sh', run: (f) => ['bash', [f]], judge0Id: 46 },
  swift: { ext: 'swift', run: (f) => ['swift', [f]], judge0Id: 83 },
  dart: { ext: 'dart', run: (f) => ['dart', [f]], judge0Id: 90 },
  go: { ext: 'go', run: (f) => ['go', ['run', f]], judge0Id: 60 },
  // zig compiles+runs in one command (like `go run`); Judge0 CE has no Zig, so local only.
  zig: { ext: 'zig', run: (f) => ['zig', ['run', f]] },
  // --- compiled: build to a.out (or .class), then run the artifact ---
  c: { ext: 'c', compile: (f, d) => ['gcc', [f, '-O2', '-w', '-o', bin(d)]], run: (_f, d) => [bin(d), []], judge0Id: 50 },
  cpp: { ext: 'cpp', compile: (f, d) => ['g++', [f, '-O2', '-w', '-std=c++17', '-o', bin(d)]], run: (_f, d) => [bin(d), []], judge0Id: 54 },
  rust: { ext: 'rs', compile: (f, d) => ['rustc', [f, '-O', '-o', bin(d)]], run: (_f, d) => [bin(d), []], judge0Id: 73 },
  java: { ext: 'java', file: 'Main.java', compile: (f, d) => ['javac', ['-d', d, f]], run: (_f, d) => ['java', ['-cp', d, 'Main']], judge0Id: 62 },
  // --- Judge0-only: runtime not installed locally (set USE_JUDGE0=true) ---
  php: { ext: 'php', judge0Id: 68 },
  typescript: { ext: 'ts', judge0Id: 74 },
  kotlin: { ext: 'kt', judge0Id: 78 },
  scala: { ext: 'scala', judge0Id: 81 },
  lua: { ext: 'lua', judge0Id: 64 },
  csharp: { ext: 'cs', judge0Id: 51 },
};

const TIMEOUT_MS = 5000;

interface ExecResult {
  stdout: string;
  stderr: string;
  exitCode: number | null;
  timedOut: boolean;
  durationMs: number;
}

// Spawn one short-lived process with a hard timeout. input=null => no stdin.
function spawnOnce(cmd: string, args: string[], input: string | null): Promise<ExecResult> {
  return new Promise((resolve) => {
    const start = Date.now();
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
      resolve({ stdout: '', stderr: String(e), exitCode: null, timedOut: false, durationMs: Date.now() - start });
    });
    child.on('close', (exitCode) => {
      clearTimeout(timer);
      resolve({ stdout, stderr, exitCode, timedOut, durationMs: Date.now() - start });
    });

    if (input !== null) child.stdin.write(input);
    child.stdin.end();
  });
}

// Run one line locally: write the source, optionally compile (own 5s budget),
// then execute (own 5s budget) with `input` piped to stdin. Temp dir always cleaned.
async function runOneLocal(language: string, code: string, input: string): Promise<ExecResult> {
  const spec = LANGS[language];
  if (!spec) {
    return { stdout: '', stderr: `Unsupported language: ${language}`, exitCode: null, timedOut: false, durationMs: 0 };
  }
  if (!spec.run) {
    return { stdout: '', stderr: `No local runtime for "${language}". Set USE_JUDGE0=true to run it via Judge0.`, exitCode: null, timedOut: false, durationMs: 0 };
  }
  const dir = mkdtempSync(join(tmpdir(), 'pcp-'));
  try {
    const src = join(dir, spec.file ?? `main.${spec.ext}`);
    writeFileSync(src, code);
    if (spec.compile) {
      const [cc, cargs] = spec.compile(src, dir);
      const comp = await spawnOnce(cc, cargs, null);
      if (comp.timedOut) {
        return { ...comp, stderr: `Compilation timed out:\n${comp.stderr}` };
      }
      if (comp.exitCode !== 0) {
        return { stdout: '', stderr: comp.stderr || 'Compilation failed', exitCode: comp.exitCode ?? 1, timedOut: false, durationMs: comp.durationMs };
      }
    }
    const [rc, rargs] = spec.run(src, dir);
    return await spawnOnce(rc, rargs, input);
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
}

const b64 = (s: string) => Buffer.from(s, 'utf8').toString('base64');
const deb64 = (s: string) => Buffer.from(s, 'base64').toString('utf8');

async function runOneJudge0(language: string, code: string, input: string, config: RunnerConfig): Promise<ExecResult> {
  const spec = LANGS[language];
  const start = Date.now();
  if (!spec) {
    return { stdout: '', stderr: `Unsupported language: ${language}`, exitCode: null, timedOut: false, durationMs: 0 };
  }
  if (spec.judge0Id == null) {
    return { stdout: '', stderr: `"${language}" is not available on Judge0 CE; run it locally (USE_JUDGE0=false).`, exitCode: null, timedOut: false, durationMs: 0 };
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
