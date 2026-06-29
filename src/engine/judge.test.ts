import { describe, it, expect, beforeEach, vi } from 'vitest';
import { judgeSubmission, type JudgeOptions } from './index';
import { runPython } from './pyodide';
import { runJs } from './js';
import { runJudge0 } from './judge0';
import type { ProblemData, TestCase } from '../problems';

// The three line-engines are replaced by a tiny deterministic interpreter so we
// can exercise the orchestrator's real logic (rotation -> engine dispatch ->
// stdout piping -> per-case verdict -> overall verdict + early stop) without
// Pyodide/Workers/Judge0. A "code" line is a command:
//   echo        -> stdout = stdin (unchanged)
//   add1        -> stdout = Number(stdin)+1   (lets us prove piping)
//   out:TEXT    -> stdout = TEXT (literal)
//   fail        -> exit code 1   (-> RE)
//   tle         -> timed out     (-> TLE)
const { fakeRun } = vi.hoisted(() => {
  function fakeRun(code: string, input: string) {
    const c = code.trim();
    const base = { stdout: '', stderr: '', exitCode: 0 as number | null, timedOut: false, durationMs: 1 };
    if (c === 'fail') return { ...base, exitCode: 1, stderr: 'boom' };
    if (c === 'tle') return { ...base, exitCode: null, timedOut: true, stderr: 'TLE' };
    if (c.startsWith('out:')) return { ...base, stdout: c.slice(4) };
    if (c === 'add1') return { ...base, stdout: String(Number(input.trim()) + 1) };
    return { ...base, stdout: input }; // echo
  }
  return { fakeRun };
});

vi.mock('./pyodide', () => ({ runPython: vi.fn((code: string, input: string) => Promise.resolve(fakeRun(code, input))) }));
vi.mock('./js', () => ({ runJs: vi.fn((code: string, input: string) => Promise.resolve(fakeRun(code, input))) }));
vi.mock('./judge0', () => ({ runJudge0: vi.fn((_id: number, code: string, input: string) => Promise.resolve(fakeRun(code, input))) }));

const tc = (name: string, input: string, output: string, hidden = false): TestCase => ({ name, input, output, hidden });

function problem(tests: TestCase[]): ProblemData {
  return { id: 'p', title: 'P', topic: 'math', difficulty: 1, tags: [], statement: '', samples: [], tests };
}

const OPTS: JudgeOptions = { mode: 'browser', judge0: { url: '', key: '', host: '' } };

describe('judgeSubmission (browser orchestrator)', () => {
  beforeEach(() => vi.clearAllMocks());

  it('returns AC when the piped output matches every case', async () => {
    // 5 --add1(py)--> 6 --add1(js)--> 7
    const res = await judgeSubmission(problem([tc('sample1', '5', '7')]), 'add1\nadd1', ['python', 'javascript'], OPTS);
    expect(res.overall).toBe('AC');
    expect(res.passed).toBe(1);
    expect(res.total).toBe(1);
    // rotation dispatched line 1 to Pyodide, line 2 to the JS worker...
    expect(runPython).toHaveBeenCalledWith('add1', '5');
    expect(runJs).toHaveBeenCalledWith('add1', '6'); // ...with line 1's stdout piped in
  });

  it('reports WA when the final output differs from expected', async () => {
    const res = await judgeSubmission(problem([tc('s', '5', '999')]), 'add1\nadd1', ['python', 'javascript'], OPTS);
    expect(res.overall).toBe('WA');
    expect(res.passed).toBe(0);
    expect(res.cases[0].finalOutput).toBe('7');
    expect(res.cases[0].expected).toBe('999');
  });

  it('reports RE on a non-zero exit code and stops the pipeline', async () => {
    const res = await judgeSubmission(problem([tc('s', '1', 'x')]), 'fail\nadd1', ['python', 'javascript'], OPTS);
    expect(res.overall).toBe('RE');
    expect(res.cases[0].steps).toHaveLength(1); // pipeline stopped after the failing line
    expect(runJs).not.toHaveBeenCalled();
  });

  it('reports TLE when a line times out', async () => {
    const res = await judgeSubmission(problem([tc('s', '1', 'x')]), 'tle', ['python'], OPTS);
    expect(res.overall).toBe('TLE');
    expect(res.cases[0].verdict).toBe('TLE');
  });

  it('skips blank lines without consuming a rotation slot', async () => {
    // line1 -> python(add1), blank skipped, line3 -> javascript(add1)
    const res = await judgeSubmission(problem([tc('s', '5', '7')]), 'add1\n\nadd1', ['python', 'javascript'], OPTS);
    expect(res.overall).toBe('AC');
    expect(runPython).toHaveBeenCalledTimes(1);
    expect(runJs).toHaveBeenCalledTimes(1);
    expect(res.cases[0].steps.map((s) => s.lineNo)).toEqual([1, 3]);
  });

  it('judges visible samples only when samplesOnly is set', async () => {
    const p = problem([tc('sample1', '5', '6', false), tc('test1', '9', '10', true)]);
    const res = await judgeSubmission(p, 'add1', ['python'], { ...OPTS, samplesOnly: true });
    expect(res.total).toBe(1);
    expect(res.cases.every((c) => !c.hidden)).toBe(true);
  });

  it('stops at the first failing case but still reports total over all cases', async () => {
    // case 1 expects wrong value -> WA, so case 2 must never run
    const p = problem([tc('c1', '5', '999'), tc('c2', '5', '6')]);
    const res = await judgeSubmission(p, 'add1', ['python'], OPTS);
    expect(res.overall).toBe('WA');
    expect(res.passed).toBe(0);
    expect(res.total).toBe(2);
    expect(res.cases).toHaveLength(1); // only the first case was executed
  });

  it('dispatches judge0-client languages to the Judge0 engine', async () => {
    const res = await judgeSubmission(problem([tc('s', 'hi', 'hi')]), 'echo', ['ruby'], OPTS);
    expect(res.overall).toBe('AC');
    expect(runJudge0).toHaveBeenCalledTimes(1);
    expect(runPython).not.toHaveBeenCalled();
  });

  it('defaults to python when no languages are selected', async () => {
    const res = await judgeSubmission(problem([tc('s', '5', '6')]), 'add1', [], OPTS);
    expect(res.overall).toBe('AC');
    expect(runPython).toHaveBeenCalledTimes(1);
  });

  it('labels the browser engine in the result', async () => {
    const res = await judgeSubmission(problem([tc('s', '1', '1')]), 'echo', ['python'], OPTS);
    expect(res.engineLabel).toMatch(/browser/i);
  });
});
