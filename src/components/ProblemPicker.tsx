import { useMemo, useState } from 'react';
import { filterProblems, type IndexEntry } from '../problems';

interface Props {
  index: IndexEntry[];
  selectedId: string | null;
  onSelect: (id: string) => void;
}

const DIFF_LABEL = ['', '★', '★★', '★★★', '★★★★'];

// Problem catalog with topic / difficulty / text filters. Pure client-side over
// the in-memory index, so filtering 495 problems is instant.
export function ProblemPicker({ index, selectedId, onSelect }: Props) {
  const [topic, setTopic] = useState('');
  const [difficulty, setDifficulty] = useState('');
  const [query, setQuery] = useState('');

  const topics = useMemo(() => Array.from(new Set(index.map((p) => p.topic))).sort(), [index]);

  const filtered = useMemo(() => filterProblems(index, { topic, difficulty, query }), [index, topic, difficulty, query]);

  return (
    <div className="picker">
      <div className="picker-filters">
        <input className="picker-search" placeholder="検索（タイトル / id / タグ）" value={query} onChange={(e) => setQuery(e.target.value)} />
        <select value={topic} onChange={(e) => setTopic(e.target.value)}>
          <option value="">topic: 全て</option>
          {topics.map((t) => (
            <option key={t} value={t}>
              {t}
            </option>
          ))}
        </select>
        <select value={difficulty} onChange={(e) => setDifficulty(e.target.value)}>
          <option value="">難易度: 全て</option>
          {[1, 2, 3, 4].map((d) => (
            <option key={d} value={String(d)}>
              {DIFF_LABEL[d]}
            </option>
          ))}
        </select>
      </div>
      <div className="picker-count">{filtered.length} 問</div>
      <ul className="picker-list">
        {filtered.map((p) => (
          <li
            key={p.id}
            className={`picker-item${p.id === selectedId ? ' selected' : ''}`}
            onClick={() => onSelect(p.id)}
          >
            <span className="picker-title">{p.title}</span>
            <span className="picker-tags">
              <span className="picker-topic">{p.topic}</span>
              <span className="picker-diff">{DIFF_LABEL[p.difficulty]}</span>
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
