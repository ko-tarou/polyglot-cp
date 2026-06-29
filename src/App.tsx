import { useEffect, useState } from 'react';
import { CodeEditor } from './components/CodeEditor';
import { ResultPanel } from './components/ResultPanel';
import { LangBadge } from './components/LangBadge';
import { ProblemPicker } from './components/ProblemPicker';
import { ProblemView } from './components/ProblemView';
import { Judge0Settings } from './components/Judge0Settings';
import type { JudgeResult } from './types';
import { DEFAULT_CODE, DEFAULT_LANGUAGES } from './problem';
import { loadIndex, loadProblem, type IndexEntry, type ProblemData } from './problems';
import { ALL_LANGUAGES, LANGS } from './engine/langs';
import { judgeSubmission } from './engine';
import { loadJudge0Config, type Judge0Config } from './engine/judge0';

type Mode = 'browser' | 'server';

export function App() {
  const [index, setIndex] = useState<IndexEntry[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [problem, setProblem] = useState<ProblemData | null>(null);

  const [code, setCode] = useState(DEFAULT_CODE);
  const [languages, setLanguages] = useState<string[]>(DEFAULT_LANGUAGES);
  const [result, setResult] = useState<JudgeResult | null>(null);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [mode, setMode] = useState<Mode>('browser');
  const [judge0, setJudge0] = useState<Judge0Config>(loadJudge0Config());

  // Load the catalog once; default to the first problem.
  useEffect(() => {
    loadIndex()
      .then((list) => {
        setIndex(list);
        if (list.length) setSelectedId(list[0].id);
      })
      .catch((e) => setError(String(e)));
  }, []);

  // Fetch the selected problem's full data (statement + all tests) on demand.
  useEffect(() => {
    if (!selectedId) return;
    setResult(null);
    loadProblem(selectedId).then(setProblem).catch((e) => setError(String(e)));
  }, [selectedId]);

  async function submit(samplesOnly: boolean) {
    if (!problem) return;
    setRunning(true);
    setError(null);
    try {
      const res = await judgeSubmission(problem, code, languages, { mode, judge0, samplesOnly });
      setResult(res);
    } catch (e) {
      setError(String(e));
      setResult(null);
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
        <div>
          <h1>Polyglot CP</h1>
          <p className="tagline">行ごとに言語が変わる競プロジャッジ — 各行は独立プロセス、stdout が次の行の stdin になります。</p>
        </div>
        <div className="header-controls">
          <select className="mode-select" value={mode} onChange={(e) => setMode(e.target.value as Mode)} title="実行エンジン">
            <option value="browser">ブラウザ実行（静的）</option>
            <option value="server">ローカル dev サーバー</option>
          </select>
          <Judge0Settings config={judge0} onChange={setJudge0} />
        </div>
      </header>

      <div className="layout">
        <aside className="sidebar">
          <ProblemPicker index={index} selectedId={selectedId} onSelect={setSelectedId} />
        </aside>

        <div className="workspace">
          <section className="problem">
            {problem ? <ProblemView problem={problem} /> : <div className="result-empty">問題を読み込み中…</div>}
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
              {ALL_LANGUAGES.map((l) => {
                const info = LANGS[l];
                const native = info.client === 'pyodide' || info.client === 'js';
                const title = native ? '完全ブラウザ実行' : info.client === 'judge0' ? 'Judge0 が必要' : 'dev サーバーのみ';
                return (
                  <label key={l} className="toggle" title={title}>
                    <input type="checkbox" checked={languages.includes(l)} onChange={() => toggleLang(l)} />
                    {l}
                    {native ? '' : info.client === 'judge0' ? '*' : '†'}
                  </label>
                );
              })}
            </span>
          </div>

          <main className="panes">
            <div className="pane pane-left">
              <div className="pane-head">
                <span>コード（各行 = 1プログラム）</span>
                <span className="pane-actions">
                  <button className="run-btn ghost" onClick={() => submit(true)} disabled={running || !problem}>
                    サンプルのみ
                  </button>
                  <button className="run-btn" onClick={() => submit(false)} disabled={running || !problem}>
                    {running ? '判定中…' : '提出 ▶'}
                  </button>
                </span>
              </div>
              <CodeEditor code={code} languages={languages} onChange={setCode} />
            </div>

            <div className="pane pane-right">
              <div className="pane-head">結果</div>
              {error ? <div className="error-box">{error}</div> : <ResultPanel result={result} running={running} />}
            </div>
          </main>
        </div>
      </div>

      <footer className="app-footer">
        静的サイト: 問題/テストは JSON 同梱、Python=Pyodide・JS=ブラウザで完全クライアント実行。
        <code>*</code>=Judge0 必要 / <code>†</code>=dev サーバーのみ（zig）。
      </footer>
    </div>
  );
}
