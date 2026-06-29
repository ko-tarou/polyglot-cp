import type { ProblemData } from '../problems';

// Minimal markdown renderer for the generated statements (headings, fenced code
// blocks, bullet lists, paragraphs). Intentionally tiny: avoids a markdown dep
// while covering exactly the constructs build_static_problems.py emits.
function renderMarkdown(md: string) {
  const blocks: JSX.Element[] = [];
  const lines = md.split('\n');
  let i = 0;
  let key = 0;
  while (i < lines.length) {
    const line = lines[i];
    if (line.startsWith('```')) {
      const buf: string[] = [];
      i++;
      while (i < lines.length && !lines[i].startsWith('```')) buf.push(lines[i++]);
      i++; // closing fence
      blocks.push(<pre className="md-code" key={key++}>{buf.join('\n')}</pre>);
      continue;
    }
    if (line.startsWith('#')) {
      const m = line.match(/^#+/)!;
      const level = Math.min(m[0].length, 4);
      const text = line.slice(level).trim();
      const Tag = (`h${level + 1}` as keyof JSX.IntrinsicElements);
      blocks.push(<Tag className="md-h" key={key++}>{text}</Tag>);
      i++;
      continue;
    }
    if (/^\s*-\s+/.test(line)) {
      const items: string[] = [];
      while (i < lines.length && /^\s*-\s+/.test(lines[i])) items.push(lines[i++].replace(/^\s*-\s+/, ''));
      blocks.push(
        <ul className="md-ul" key={key++}>
          {items.map((it, j) => (
            <li key={j}>{it}</li>
          ))}
        </ul>,
      );
      continue;
    }
    if (line.trim() === '') {
      i++;
      continue;
    }
    const para: string[] = [];
    while (i < lines.length && lines[i].trim() !== '' && !lines[i].startsWith('#') && !lines[i].startsWith('```') && !/^\s*-\s+/.test(lines[i])) {
      para.push(lines[i++]);
    }
    blocks.push(<p className="md-p" key={key++}>{para.join(' ')}</p>);
  }
  return blocks;
}

export function ProblemView({ problem }: { problem: ProblemData }) {
  return (
    <div className="problem-view">
      <div className="problem-meta">
        <span className="muted">{problem.id}</span>
        <span className="problem-topic">{problem.topic}</span>
        <span className="problem-diff">難易度 {problem.difficulty}/4</span>
        <span className="muted">テスト {problem.tests.length} 件（公開 {problem.samples.length} ・ 非公開 {problem.tests.length - problem.samples.length}）</span>
      </div>
      <div className="problem-statement">{renderMarkdown(problem.statement)}</div>
    </div>
  );
}
