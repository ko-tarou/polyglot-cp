import { useState } from 'react';
import { judge0Configured, saveJudge0Config, type Judge0Config } from '../engine/judge0';

interface Props {
  config: Judge0Config;
  onChange: (cfg: Judge0Config) => void;
}

// Collapsible Judge0 connection settings. Values persist to localStorage only
// (never bundled/committed) so non-WASM languages can run via an external API.
export function Judge0Settings({ config, onChange }: Props) {
  const [open, setOpen] = useState(false);
  const [draft, setDraft] = useState(config);
  const configured = judge0Configured(config);

  function save() {
    saveJudge0Config(draft);
    onChange(draft);
    setOpen(false);
  }

  return (
    <div className="judge0">
      <button className="judge0-toggle" onClick={() => setOpen((o) => !o)}>
        Judge0 {configured ? '● 設定済み' : '○ 未設定'}
      </button>
      {open && (
        <div className="judge0-panel">
          <p className="muted small">
            Python/JS 以外の言語はブラウザで動かないため、外部 Judge0 API に委譲します（自前バックエンドではありません）。値は localStorage のみに保存されます。
          </p>
          <label>
            URL
            <input value={draft.url} placeholder="https://judge0-ce.p.rapidapi.com" onChange={(e) => setDraft({ ...draft, url: e.target.value })} />
          </label>
          <label>
            RapidAPI Key（任意）
            <input value={draft.key} type="password" placeholder="self-host なら空欄" onChange={(e) => setDraft({ ...draft, key: e.target.value })} />
          </label>
          <label>
            RapidAPI Host（任意）
            <input value={draft.host} placeholder="judge0-ce.p.rapidapi.com" onChange={(e) => setDraft({ ...draft, host: e.target.value })} />
          </label>
          <div className="judge0-actions">
            <button className="run-btn" onClick={save}>
              保存
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
