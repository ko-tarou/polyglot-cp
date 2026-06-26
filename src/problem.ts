export interface Problem {
  id: string;
  title: string;
  statement: string;
  input: string;
  expected: string;
}

// One bundled sample problem for the PoC.
export const SAMPLE_PROBLEM: Problem = {
  id: 'double',
  title: 'Double N',
  statement: '整数 N が 1 行で与えられる。N を 2 倍した値を出力せよ。',
  input: '5\n',
  expected: '10',
};

// Default rotation cycle. Extend this list to add more languages to the cycle.
export const DEFAULT_LANGUAGES = ['python', 'javascript'];

export const SUPPORTED_LANGUAGES = ['python', 'javascript'];

// Default solution: 3 lines that demonstrate the rotation cycling back to Python.
//   line 1 (python)     : read N, echo it through
//   line 2 (javascript) : read N, output N * 2
//   line 3 (python)     : read the value, echo it as the final answer
export const DEFAULT_CODE = [
  'print(input())',
  "const n = Number(require('fs').readFileSync(0, 'utf8').trim()); console.log(n * 2);",
  'print(input())',
].join('\n');
