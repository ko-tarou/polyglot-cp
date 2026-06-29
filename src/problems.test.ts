import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { loadIndex, loadProblem, filterProblems, type IndexEntry } from './problems';

const entry = (over: Partial<IndexEntry>): IndexEntry => ({
  id: 'add-two-d1-0001',
  title: 'A + B',
  topic: 'math',
  difficulty: 1,
  tags: ['arithmetic', 'io'],
  tests: 7,
  ...over,
});

const sample: IndexEntry[] = [
  entry({ id: 'add-two-d1-0001', title: 'A + B', topic: 'math', difficulty: 1, tags: ['arithmetic'] }),
  entry({ id: 'gcd-d2-0060', title: 'GCD', topic: 'number-theory', difficulty: 2, tags: ['gcd', 'euclid'] }),
  entry({ id: 'palindrome-d2-0311', title: 'Palindrome', topic: 'strings', difficulty: 2, tags: ['string'] }),
  entry({ id: 'is-prime-d3-0085', title: 'Is Prime', topic: 'number-theory', difficulty: 3, tags: ['prime'] }),
];

// ---- filterProblems (the picker's selection logic) --------------------------
describe('filterProblems', () => {
  it('returns everything with no constraints', () => {
    expect(filterProblems(sample, {})).toHaveLength(4);
  });

  it('filters by topic', () => {
    const r = filterProblems(sample, { topic: 'number-theory' });
    expect(r.map((p) => p.id)).toEqual(['gcd-d2-0060', 'is-prime-d3-0085']);
  });

  it('filters by difficulty (string form, matching the <select> value)', () => {
    expect(filterProblems(sample, { difficulty: '2' }).map((p) => p.id)).toEqual(['gcd-d2-0060', 'palindrome-d2-0311']);
  });

  it('matches the free-text query against title, id and tags, case-insensitively', () => {
    expect(filterProblems(sample, { query: 'PALIN' }).map((p) => p.id)).toEqual(['palindrome-d2-0311']); // title
    expect(filterProblems(sample, { query: '0060' }).map((p) => p.id)).toEqual(['gcd-d2-0060']); // id
    expect(filterProblems(sample, { query: 'euclid' }).map((p) => p.id)).toEqual(['gcd-d2-0060']); // tag
  });

  it('trims whitespace-only queries to no constraint', () => {
    expect(filterProblems(sample, { query: '   ' })).toHaveLength(4);
  });

  it('combines topic + difficulty + query (AND semantics)', () => {
    expect(filterProblems(sample, { topic: 'number-theory', difficulty: '3', query: 'prime' }).map((p) => p.id)).toEqual([
      'is-prime-d3-0085',
    ]);
    expect(filterProblems(sample, { topic: 'number-theory', difficulty: '1' })).toHaveLength(0);
  });
});

// ---- loadIndex / loadProblem (static JSON fetch + cache) --------------------
describe('loadIndex / loadProblem', () => {
  afterEach(() => vi.restoreAllMocks());

  it('fetches index.json and unwraps the problems array', async () => {
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, json: async () => ({ count: 2, problems: sample.slice(0, 2) }) });
    vi.stubGlobal('fetch', fetchMock);
    const list = await loadIndex();
    expect(list).toHaveLength(2);
    expect(fetchMock).toHaveBeenCalledWith('/problems/index.json');
  });

  it('throws a helpful error when the index fetch fails', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: false, status: 404 }));
    await expect(loadIndex()).rejects.toThrow(/index\.json/);
  });

  it('fetches a problem by id and caches it (second call does not refetch)', async () => {
    const data = { id: 'gcd-d2-0060', title: 'GCD', topic: 'number-theory', difficulty: 2, tags: [], statement: '', samples: [], tests: [] };
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, json: async () => data });
    vi.stubGlobal('fetch', fetchMock);
    const first = await loadProblem('gcd-d2-0060');
    const second = await loadProblem('gcd-d2-0060');
    expect(first).toBe(second); // same cached reference
    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(fetchMock).toHaveBeenCalledWith('/problems/gcd-d2-0060.json');
  });

  it('throws when a problem fetch fails', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: false, status: 500 }));
    await expect(loadProblem('does-not-exist-9999')).rejects.toThrow(/does-not-exist-9999/);
  });
});
