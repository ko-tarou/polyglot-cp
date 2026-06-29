import { useEffect, useState } from 'react';
import type { CaseResult, JudgeResult, Verdict } from '../types';
import { LangBadge } from './LangBadge';

const VERDICT_COLORS: Record<Verdict, string> = {
  AC: '#1a7f37',
  WA: '#cf222e',
  RE: '#9a6700',
  TLE: '#8250df',
  CE: '#9a6700',
  ERR: '#6e7781',
};

function show(s: string) {
  if (s === '') return <span className="muted">(empty)</span>;
  return <pre className="io-block">{s}</pre>;
}

function VerdictTag({ v }: { v: Verdict }) {
  return (
    <span className="verdict" style={{ background: VERDICT_COLORS[v] ?? '#555' }}>
      {v}
    </span>
  );
}

export function ResultPanel({ result, running }: { result: JudgeResult | null; running: boolean }) {
  const [active, setActive] = useState(0);

  // Focus the first failing case automatically so the user sees what broke.
  useEffect(() => {
    if (!result) return;
    const fail = result.cases.findIndex((c) => c.verdict !== 'AC');
    setActive(fail >= 0 ? fail : 0);
  }, [result]);

  if (running) return <div className="result-empty">判定中…（初回は Pyodide のロードに数秒かかります）</div>;
  if (!result) return <div className="result-empty">問題を選び「提出」を押すと、全テストケースを各行別言語で判定します。</div>;

  const focused: CaseResult | undefined = result.cases[active];

  return (
    <div className="result">
      <div className="verdict-row">
        <VerdictTag v={result.overall} />
        <span className="score">
          {result.passed} / {result.total} ケース
        </span>
        <span className="engine-tag">engine: {result.engineLabel}</span>
      </div>

      <div className="case-chips">
        {result.cases.map((c, i) => (
          <button
            key={c.name}
            className={`case-chip${i === active ? ' active' : ''}`}
            style={{ borderColor: VERDICT_COLORS[c.verdict] }}
            onClick={() => setActive(i)}
            title={c.hidden ? '非公開ケース' : '公開サンプル'}
          >
            <span className="case-name">{c.hidden ? c.name : `▸ ${c.name}`}</span>
            <span className="case-verdict" style={{ color: VERDICT_COLORS[c.verdict] }}>
              {c.verdict}
            </span>
          </button>
        ))}
      </div>

      {focused && (
        <>
          <div className="final-row">
            <div>
              <div className="io-label">最終出力</div>
              {show(focused.finalOutput)}
            </div>
            <div>
              <div className="io-label">期待値</div>
              {show(focused.expected)}
            </div>
          </div>

          <h3 className="steps-title">パイプライン中間出力 — {focused.name}</h3>
          <ol className="steps">
            {focused.steps.map((s) => (
              <li className="step" key={s.lineNo}>
                <div className="step-head">
                  <span className="step-no">行 {s.lineNo}</span>
                  <LangBadge lang={s.language} />
                  <code className="step-code">{s.code}</code>
                  <span className="step-meta">
                    {s.durationMs}ms{s.timedOut ? ' · TLE' : ''}
                    {s.exitCode !== 0 && s.exitCode !== null ? ` · exit ${s.exitCode}` : ''}
                    {` · ${s.engine}`}
                  </span>
                </div>
                <div className="step-io">
                  <div>
                    <div className="io-label">stdin</div>
                    {show(s.stdin)}
                  </div>
                  <div>
                    <div className="io-label">stdout</div>
                    {show(s.stdout)}
                  </div>
                </div>
                {s.stderr ? (
                  <div className="step-stderr">
                    <div className="io-label">stderr</div>
                    <pre className="io-block err">{s.stderr}</pre>
                  </div>
                ) : null}
              </li>
            ))}
          </ol>
        </>
      )}
    </div>
  );
}
