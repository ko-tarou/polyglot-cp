const COLORS: Record<string, string> = {
  python: '#3776ab',
  javascript: '#b8860b',
};

const LABELS: Record<string, string> = {
  python: 'PY',
  javascript: 'JS',
};

export function LangBadge({ lang }: { lang: string }) {
  return (
    <span className="lang-badge" style={{ background: COLORS[lang] ?? '#555' }} title={lang}>
      {LABELS[lang] ?? lang.slice(0, 2).toUpperCase()}
    </span>
  );
}
