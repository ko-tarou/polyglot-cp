// Static problem catalog. Both the light index and per-problem bundles are
// plain JSON assets emitted by tools/build_static_problems.py into
// public/problems/. Nothing here needs a backend: the picker fetches the index
// once, and each problem's full data (statement + all test cases) is fetched
// lazily on selection.

export interface IndexEntry {
  id: string;
  title: string;
  topic: string;
  difficulty: number;
  tags: string[];
  tests: number;
}

export interface TestCase {
  name: string;
  input: string;
  output: string;
  hidden: boolean;
}

export interface ProblemData {
  id: string;
  title: string;
  topic: string;
  difficulty: number;
  tags: string[];
  statement: string;
  samples: { input: string; output: string }[];
  tests: TestCase[];
}

// Resolve asset URLs against Vite's base so the site works when deployed under
// a subpath (e.g. GitHub Pages project sites at /<repo>/).
const base = import.meta.env.BASE_URL;

export async function loadIndex(): Promise<IndexEntry[]> {
  const res = await fetch(`${base}problems/index.json`);
  if (!res.ok) throw new Error(`index.json の取得に失敗しました (${res.status})`);
  const data = (await res.json()) as { problems: IndexEntry[] };
  return data.problems;
}

const cache = new Map<string, ProblemData>();

export async function loadProblem(id: string): Promise<ProblemData> {
  const hit = cache.get(id);
  if (hit) return hit;
  const res = await fetch(`${base}problems/${id}.json`);
  if (!res.ok) throw new Error(`問題 ${id} の取得に失敗しました (${res.status})`);
  const data = (await res.json()) as ProblemData;
  cache.set(id, data);
  return data;
}
