// Shared client types. The static frontend runs the judge entirely in the
// browser (Pyodide/JS/Judge0); the dev-server engine (server/runner.ts) reuses
// the same LineResult/Verdict shapes over /api/run.

export type Verdict = 'AC' | 'WA' | 'RE' | 'TLE' | 'CE' | 'ERR';

export type EngineKind = 'pyodide' | 'js' | 'judge0' | 'server';

export interface ExecResult {
  stdout: string;
  stderr: string;
  exitCode: number | null;
  timedOut: boolean;
  durationMs: number;
}

export interface LineResult extends ExecResult {
  lineNo: number;
  language: string;
  code: string;
  stdin: string;
  engine: EngineKind;
}

// One test case fully evaluated through the per-line pipeline.
export interface CaseResult {
  name: string;
  hidden: boolean;
  input: string;
  expected: string;
  finalOutput: string;
  verdict: Verdict;
  steps: LineResult[];
}

// Result of judging a submission against every test case of a problem.
export interface JudgeResult {
  overall: Verdict;
  cases: CaseResult[];
  passed: number;
  total: number;
  engineLabel: string;
}

// Per-line rotation: only non-empty lines consume a slot, so the badge a user
// sees lines up exactly with what the engine executes.
export function languageForLines(code: string, languages: string[]): (string | null)[] {
  const list = languages.length ? languages : ['python'];
  let visibleIdx = 0;
  return code.split('\n').map((line) => {
    if (line.trim() === '') return null;
    const lang = list[visibleIdx % list.length];
    visibleIdx++;
    return lang;
  });
}
