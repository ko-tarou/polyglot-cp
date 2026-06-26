import { useState } from 'react';
import { CodeEditor } from './components/CodeEditor';
import { ResultPanel } from './components/ResultPanel';
import { LangBadge } from './components/LangBadge';
import type { RunResponse } from './types';
import { DEFAULT_CODE, DEFAULT_LANGUAGES, SAMPLE_PROBLEM, SUPPORTED_LANGUAGES } from './problem';

export function App() {
  const [code, setCode] = useState(DEFAULT_CODE);
  const [languages, setLanguages] = useState<string[]>(DEFAULT_LANGUAGES);
  const [result, setResult] = useState<RunResponse | null>(null);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function run() {
    setRunning(true);
    setError(null);
    try {
      const res = await fetch('/api/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          code,
          languages,
          input: SAMPLE_PROBLEM.input,
          expected: SAMPLE_PROBLEM.expected,
        }),
      });
      const data = (await res.json()) as RunResponse & { error?: string };
      if (data.error) {
        setError(data.error);
        setResult(null);
      } else {
        setResult(data);
      }
    } catch (e) {
      setError(String(e));
    } finally {
      setRunning(false);
    }
  }

  function toggleLang(lang: string) {
    setLanguages((prev) => {
      if (prev.includes(lang)) {
        const next = prev.filter((l) => l !== lang);
        return next.length ? next : prev; // keep at least one
      }
      return [...prev, lang];
    });
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>Polyglot CP</h1>
        <p className="tagline">行ごとに言語が変わる競プロジャッジ — 各行は独立プロセス、stdout が次の行の stdin になります。</p>
      </header>

      <section className="problem">
        <h2>
          {SAMPLE_PROBLEM.title} <span className="muted">({SAMPLE_PROBLEM.id})</span>
        </h2>
        <p>{SAMPLE_PROBLEM.statement}</p>
        <p className="muted">
          input: <code>{JSON.stringify(SAMPLE_PROBLEM.input)}</code> → expected:{' '}
          <code>{SAMPLE_PROBLEM.expected}</code>
        </p>
      </section>

      <div className="rotation-bar">
        <span className="rotation-label">ローテーション:</span>
        {languages.map((l, i) => (
          <span className="rotation-item" key={l}>
            {i > 0 && <span className="arrow">→</span>}
            <LangBadge lang={l} />
          </span>
        ))}
        <span className="arrow">→ …</span>
        <span className="rotation-toggles">
          {SUPPORTED_LANGUAGES.map((l) => (
            <label key={l} className="toggle">
              <input type="checkbox" checked={languages.includes(l)} onChange={() => toggleLang(l)} />
              {l}
            </label>
          ))}
        </span>
      </div>

      <main className="panes">
        <div className="pane pane-left">
          <div className="pane-head">
            <span>コード（各行 = 1プログラム）</span>
            <button className="run-btn" onClick={run} disabled={running}>
              {running ? '実行中…' : '実行 ▶'}
            </button>
          </div>
          <CodeEditor code={code} languages={languages} onChange={setCode} />
        </div>

        <div className="pane pane-right">
          <div className="pane-head">結果</div>
          {error ? <div className="error-box">{error}</div> : <ResultPanel result={result} running={running} />}
        </div>
      </main>

      <footer className="app-footer">
        PoC · ローカル実行は自分のコードを自分の PC で動かす前提（各行 5 秒タイムアウト）。本番は Judge0 / サンドボックス必須。
      </footer>
    </div>
  );
}
