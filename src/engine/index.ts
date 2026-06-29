// Judge orchestrator. Splits a submission into line-programs, dispatches each
// line to the right engine by its rotation language, pipes stdout -> next stdin,
// and judges the final output against every test case (all must pass for AC).
import type { CaseResult, EngineKind, ExecResult, JudgeResult, LineResult, Verdict } from '../types';
import type { ProblemData, TestCase } from '../problems';
import { LANGS } from './langs';
import { runPython } from './pyodide';
import { runJs } from './js';
import { runJudge0, type Judge0Config } from './judge0';

export interface JudgeOptions {
  mode: 'browser' | 'server';
  judge0: Judge0Config;
  samplesOnly?: boolean; // judge visible samples only (quick check)
}

function engineForLang(lang: string): EngineKind | null {
  return LANGS[lang]?.client ?? null;
}

// Execute a single line-program in the browser via its assigned engine.
async function runLineBrowser(lang: string, code: string, input: string, cfg: Judge0Config): Promise<{ res: ExecResult; engine: EngineKind }> {
  const engine = engineForLang(lang);
  if (engine === 'pyodide') return { res: await runPython(code, input), engine };
  if (engine === 'js') return { res: await runJs(code, input), engine };
  if (engine === 'judge0') {
    const id = LANGS[lang]?.judge0Id;
    if (id == null) {
      return { res: { stdout: '', stderr: `"${lang}" は Judge0 にもブラウザにも実行系がありません。`, exitCode: null, timedOut: false, durationMs: 0 }, engine: 'judge0' };
    }
    return { res: await runJudge0(id, code, input, cfg), engine: 'judge0' };
  }
  return {
    res: { stdout: '', stderr: `"${lang}" は静的ビルドでは実行できません（dev サーバーengineでのみ可）。`, exitCode: null, timedOut: false, durationMs: 0 },
    engine: 'judge0',
  };
}

interface PipelineOutcome {
  steps: LineResult[];
  finalOutput: string;
  verdict: Verdict; // AC means "ran clean"; caller compares output for WA
}

// Run one test case through the full per-line pipeline in the browser.
async function runPipelineBrowser(code: string, languages: string[], input: string, cfg: Judge0Config): Promise<PipelineOutcome> {
  const langs = languages.length ? languages : ['python'];
  const lines = code.split('\n');
  const steps: LineResult[] = [];
  let current = input;
  let visibleIdx = 0;
  let verdict: Verdict = 'AC';

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (line.trim() === '') continue;
    const language = langs[visibleIdx % langs.length];
    visibleIdx++;
    const { res, engine } = await runLineBrowser(language, line, current, cfg);
    steps.push({ lineNo: i + 1, language, code: line, stdin: current, engine, ...res });
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
  return { steps, finalOutput: (current ?? '').trim(), verdict };
}

// Server (dev) engine: delegate a whole case to /api/run (server/runner.ts).
async function runCaseServer(code: string, languages: string[], tc: TestCase): Promise<CaseResult> {
  const res = await fetch('/api/run', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ code, languages, input: tc.input, expected: tc.output }),
  });
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const data: any = await res.json();
  if (data.error) throw new Error(data.error);
  const steps: LineResult[] = (data.steps ?? []).map((s: ExecResult & { lineNo: number; language: string; code: string; stdin: string }) => ({ ...s, engine: 'server' as EngineKind }));
  return {
    name: tc.name,
    hidden: tc.hidden,
    input: tc.input,
    expected: tc.output.trim(),
    finalOutput: data.finalOutput ?? '',
    verdict: data.verdict as Verdict,
    steps,
  };
}

async function runCaseBrowser(code: string, languages: string[], tc: TestCase, cfg: Judge0Config): Promise<CaseResult> {
  const { steps, finalOutput, verdict } = await runPipelineBrowser(code, languages, tc.input, cfg);
  const expected = tc.output.trim();
  const finalVerdict: Verdict = verdict === 'AC' ? (finalOutput === expected ? 'AC' : 'WA') : verdict;
  return { name: tc.name, hidden: tc.hidden, input: tc.input, expected, finalOutput, verdict: finalVerdict, steps };
}

const ENGINE_LABEL: Record<JudgeOptions['mode'], string> = {
  browser: 'browser (Pyodide / JS / Judge0)',
  server: 'local dev server',
};

// Judge a submission against every test case. Stops early on the first failure
// so a broken submission is reported fast (an AC requires all cases to pass).
export async function judgeSubmission(problem: ProblemData, code: string, languages: string[], opts: JudgeOptions): Promise<JudgeResult> {
  const all = problem.tests ?? [];
  const cases = opts.samplesOnly ? all.filter((t) => !t.hidden) : all;
  const results: CaseResult[] = [];
  let overall: Verdict = 'AC';

  for (const tc of cases) {
    const cr = opts.mode === 'server' ? await runCaseServer(code, languages, tc) : await runCaseBrowser(code, languages, tc, opts.judge0);
    results.push(cr);
    if (cr.verdict !== 'AC' && overall === 'AC') overall = cr.verdict;
    if (cr.verdict !== 'AC') break; // first failure decides the verdict
  }

  const passed = results.filter((r) => r.verdict === 'AC').length;
  return { overall, cases: results, passed, total: cases.length, engineLabel: ENGINE_LABEL[opts.mode] };
}
