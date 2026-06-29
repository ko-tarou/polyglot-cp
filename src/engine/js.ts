// Drives the JS Web Worker with a hard wall-clock timeout. A fresh worker per
// line keeps globals from leaking between line-programs and lets us terminate a
// runaway submission to produce a TLE verdict.
import type { ExecResult } from '../types';

const TIMEOUT_MS = 5000;

export function runJs(code: string, input: string): Promise<ExecResult> {
  const start = Date.now();
  return new Promise((resolve) => {
    const worker = new Worker(new URL('./jsWorker.ts', import.meta.url), { type: 'module' });
    const timer = setTimeout(() => {
      worker.terminate();
      resolve({ stdout: '', stderr: 'Time limit exceeded', exitCode: null, timedOut: true, durationMs: Date.now() - start });
    }, TIMEOUT_MS);

    worker.onmessage = (e: MessageEvent<{ stdout: string; stderr: string; exitCode: number }>) => {
      clearTimeout(timer);
      worker.terminate();
      resolve({ ...e.data, timedOut: false, durationMs: Date.now() - start });
    };
    worker.onerror = (e) => {
      clearTimeout(timer);
      worker.terminate();
      resolve({ stdout: '', stderr: e.message, exitCode: 1, timedOut: false, durationMs: Date.now() - start });
    };
    worker.postMessage({ code, input });
  });
}
