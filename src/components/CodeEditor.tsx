import { useRef } from 'react';
import { languageForLines } from '../types';
import { LangBadge } from './LangBadge';

interface Props {
  code: string;
  languages: string[];
  onChange: (code: string) => void;
}

// A textarea with a synced gutter on the left that shows, per physical line,
// the line number and the language assigned by rotation. Line-height is shared
// between gutter and textarea so badges align with the code.
export function CodeEditor({ code, languages, onChange }: Props) {
  const gutterRef = useRef<HTMLDivElement>(null);
  const lineLangs = languageForLines(code, languages);

  return (
    <div className="editor">
      <div className="editor-gutter" ref={gutterRef}>
        {lineLangs.map((lang, i) => (
          <div className="gutter-row" key={i}>
            <span className="gutter-num">{i + 1}</span>
            {lang ? <LangBadge lang={lang} /> : <span className="gutter-empty">—</span>}
          </div>
        ))}
      </div>
      <textarea
        className="editor-textarea"
        value={code}
        spellCheck={false}
        wrap="off"
        onChange={(e) => onChange(e.target.value)}
        onScroll={(e) => {
          if (gutterRef.current) gutterRef.current.scrollTop = e.currentTarget.scrollTop;
        }}
      />
    </div>
  );
}
