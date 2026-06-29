import { LANGS } from '../engine/langs';

export function LangBadge({ lang }: { lang: string }) {
  const info = LANGS[lang];
  return (
    <span className="lang-badge" style={{ background: info?.color ?? '#555' }} title={lang}>
      {info?.label ?? lang.slice(0, 2).toUpperCase()}
    </span>
  );
}
