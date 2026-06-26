// Mirror of the server's response shape (kept in sync manually for the PoC).
export interface LineResult {
  lineNo: number;
  language: string;
  code: string;
  stdin: string;
  stdout: string;
  stderr: string;
  exitCode: number | null;
  timedOut: boolean;
  durationMs: number;
}

export interface RunResponse {
  steps: LineResult[];
  finalOutput: string;
  expected: string;
  verdict: 'AC' | 'WA' | 'RE' | 'TLE';
  engine: 'local' | 'judge0';
}

// Per-line rotation: only non-empty lines consume a slot, so the badge a user
// sees lines up exactly with what the server executes.
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
