// Judge0 engine for languages that cannot run in the browser (C#, Kotlin, Go,
// Rust, ...). The browser POSTs each line directly to a Judge0 instance the user
// configures in the UI (RapidAPI-hosted or self-hosted) - this is an external
// API, not a backend we ship. Credentials live in localStorage only and are
// never bundled or committed.
import type { ExecResult } from '../types';

export interface Judge0Config {
  url: string;
  key: string;
  host: string;
}

const STORAGE_KEY = 'pcp.judge0';

export function loadJudge0Config(): Judge0Config {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) return JSON.parse(raw) as Judge0Config;
  } catch {
    /* ignore */
  }
  return { url: '', key: '', host: 'judge0-ce.p.rapidapi.com' };
}

export function saveJudge0Config(cfg: Judge0Config): void {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(cfg));
}

export function judge0Configured(cfg: Judge0Config): boolean {
  return cfg.url.trim().length > 0;
}

const b64 = (s: string) => btoa(unescape(encodeURIComponent(s)));
const deb64 = (s: string) => decodeURIComponent(escape(atob(s)));

export async function runJudge0(langId: number, code: string, input: string, cfg: Judge0Config): Promise<ExecResult> {
  const start = Date.now();
  if (!judge0Configured(cfg)) {
    return { stdout: '', stderr: 'Judge0 が未設定です（右上の Judge0 設定で URL を入力してください）。', exitCode: null, timedOut: false, durationMs: 0 };
  }
  try {
    const headers: Record<string, string> = { 'Content-Type': 'application/json' };
    if (cfg.key) {
      headers['X-RapidAPI-Key'] = cfg.key;
      headers['X-RapidAPI-Host'] = cfg.host;
    }
    const url = `${cfg.url.replace(/\/$/, '')}/submissions?base64_encoded=true&wait=true`;
    const r = await fetch(url, {
      method: 'POST',
      headers,
      body: JSON.stringify({ source_code: b64(code), stdin: b64(input), language_id: langId }),
    });
    if (!r.ok) {
      return { stdout: '', stderr: `Judge0 HTTP ${r.status}`, exitCode: null, timedOut: false, durationMs: Date.now() - start };
    }
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const j: any = await r.json();
    const stdout = j.stdout ? deb64(j.stdout) : '';
    const stderr = (j.stderr ? deb64(j.stderr) : '') + (j.compile_output ? deb64(j.compile_output) : '');
    const statusId: number | undefined = j.status?.id;
    const timedOut = statusId === 5; // Time Limit Exceeded
    const exitCode = statusId === 3 ? 0 : timedOut ? null : 1; // 3 = Accepted
    return { stdout, stderr, exitCode, timedOut, durationMs: Date.now() - start };
  } catch (e) {
    return { stdout: '', stderr: `Judge0 リクエスト失敗: ${e}（CORS 未許可の可能性）`, exitCode: null, timedOut: false, durationMs: Date.now() - start };
  }
}
