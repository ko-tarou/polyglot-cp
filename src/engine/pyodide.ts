// Python execution, 100% in the browser via Pyodide (CPython compiled to WASM).
// Pyodide is loaded lazily from the jsDelivr CDN on first Python run, so the
// initial page load stays light and non-Python problems never pay the cost.
import type { ExecResult } from '../types';

const PYODIDE_VERSION = '0.26.4';
const CDN = `https://cdn.jsdelivr.net/pyodide/v${PYODIDE_VERSION}/full/`;

// eslint-disable-next-line @typescript-eslint/no-explicit-any
let pyodidePromise: Promise<any> | null = null;

export function pyodideLoading(): boolean {
  return pyodidePromise !== null;
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
async function getPyodide(): Promise<any> {
  if (!pyodidePromise) {
    pyodidePromise = (async () => {
      // @vite-ignore: resolved at runtime from the CDN, not bundled.
      const mod: any = await import(/* @vite-ignore */ `${CDN}pyodide.mjs`);
      return mod.loadPyodide({ indexURL: CDN });
    })();
  }
  return pyodidePromise;
}

// Run one line-program: redirect stdin/stdout/stderr inside CPython, exec the
// source in a fresh __main__ namespace, and return captured output + exit code.
export async function runPython(code: string, input: string): Promise<ExecResult> {
  const start = Date.now();
  let py;
  try {
    py = await getPyodide();
  } catch (e) {
    return { stdout: '', stderr: `Pyodide のロードに失敗しました: ${e}`, exitCode: null, timedOut: false, durationMs: Date.now() - start };
  }

  py.globals.set('__pcp_src', code);
  py.globals.set('__pcp_in', input);
  const wrapper = `
import sys, io, traceback
_old = (sys.stdin, sys.stdout, sys.stderr)
sys.stdin = io.StringIO(__pcp_in)
_out, _err = io.StringIO(), io.StringIO()
sys.stdout, sys.stderr = _out, _err
_rc = 0
try:
    exec(compile(__pcp_src, '<line>', 'exec'), {'__name__': '__main__'})
except SystemExit as _e:
    _rc = int(_e.code) if isinstance(_e.code, int) else (0 if _e.code is None else 1)
except BaseException:
    traceback.print_exc()
    _rc = 1
finally:
    sys.stdin, sys.stdout, sys.stderr = _old
[_out.getvalue(), _err.getvalue(), _rc]
`;
  try {
    const proxy = await py.runPythonAsync(wrapper);
    const [stdout, stderr, exitCode] = proxy.toJs();
    proxy.destroy?.();
    return { stdout, stderr, exitCode, timedOut: false, durationMs: Date.now() - start };
  } catch (e) {
    return { stdout: '', stderr: String(e), exitCode: 1, timedOut: false, durationMs: Date.now() - start };
  }
}
