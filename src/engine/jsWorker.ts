// Web Worker that runs one JavaScript line-program in isolation. Running in a
// worker (not the main thread) lets us hard-kill it on timeout for a real TLE
// verdict and keeps a buggy submission from freezing the UI.
//
// stdin convention (browser JS engine): a submission reads the whole input via
//   require('fs').readFileSync(0, 'utf8')   // 0 or '/dev/stdin'
// and writes the answer with console.log / process.stdout.write.

interface Msg {
  code: string;
  input: string;
}

self.onmessage = (e: MessageEvent<Msg>) => {
  const { code, input } = e.data;
  let out = '';
  let err = '';
  const toStr = (a: unknown[]) => a.map((x) => (typeof x === 'string' ? x : String(x))).join(' ');

  const consoleShim = {
    log: (...a: unknown[]) => (out += toStr(a) + '\n'),
    error: (...a: unknown[]) => (err += toStr(a) + '\n'),
    warn: (...a: unknown[]) => (err += toStr(a) + '\n'),
    info: (...a: unknown[]) => (out += toStr(a) + '\n'),
  };
  const requireShim = (m: string) => {
    if (m === 'fs') {
      return {
        readFileSync: (fd: number | string) => (fd === 0 || fd === '/dev/stdin' ? input : ''),
      };
    }
    throw new Error(`require("${m}") はブラウザ JS エンジンでは未対応です`);
  };
  const processShim = {
    stdout: { write: (s: string) => (out += s) },
    stderr: { write: (s: string) => (err += s) },
    argv: ['node', 'main.js'],
    exit: () => {},
  };

  let exitCode = 0;
  try {
    // eslint-disable-next-line no-new-func
    const fn = new Function('require', 'console', 'process', '__stdin', code);
    fn(requireShim, consoleShim, processShim, input);
  } catch (ex) {
    err += String((ex as Error)?.stack ?? ex) + '\n';
    exitCode = 1;
  }
  (self as unknown as Worker).postMessage({ stdout: out, stderr: err, exitCode });
};
