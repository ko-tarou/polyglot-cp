import type { RunResponse } from '../types';
import { LangBadge } from './LangBadge';

const VERDICT_COLORS: Record<string, string> = {
  AC: '#1a7f37',
  WA: '#cf222e',
  RE: '#9a6700',
  TLE: '#8250df',
};

function show(s: string) {
  if (s === '') return <span className="muted">(empty)</span>;
  return <pre className="io-block">{s}</pre>;
}

export function ResultPanel({ result, running }: { result: RunResponse | null; running: boolean }) {
  if (running) return <div className="result-empty">実行中…</div>;
  if (!result) return <div className="result-empty">「実行」を押すと、各行が順に別言語で実行されます。</div>;

  return (
    <div className="result">
      <div className="verdict-row">
        <span className="verdict" style={{ background: VERDICT_COLORS[result.verdict] ?? '#555' }}>
          {result.verdict}
        </span>
        <span className="engine-tag">engine: {result.engine}</span>
      </div>

      <div className="final-row">
        <div>
          <div className="io-label">最終出力</div>
          {show(result.finalOutput)}
        </div>
        <div>
          <div className="io-label">期待値</div>
          {show(result.expected)}
        </div>
      </div>

      <h3 className="steps-title">パイプライン中間出力</h3>
      <ol className="steps">
        {result.steps.map((s) => (
          <li className="step" key={s.lineNo}>
            <div className="step-head">
              <span className="step-no">行 {s.lineNo}</span>
              <LangBadge lang={s.language} />
              <code className="step-code">{s.code}</code>
              <span className="step-meta">
                {s.durationMs}ms{s.timedOut ? ' · TLE' : ''}
                {s.exitCode !== 0 && s.exitCode !== null ? ` · exit ${s.exitCode}` : ''}
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
    </div>
  );
}
