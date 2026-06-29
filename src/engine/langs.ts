// Single source of truth for languages and how each one runs in the *static*
// (browser) build. This mirrors the language_id table in server/runner.ts.
//
// client engine per language:
//   pyodide -> 100% in-browser (Python via WebAssembly, loaded from CDN)
//   js      -> 100% in-browser (native JS in a Web Worker)
//   judge0  -> needs an external Judge0 API (configured in the UI); not a backend
//              we own. zig has no Judge0 CE runtime, so it is dev-server-only.
import type { EngineKind } from '../types';

export interface LangInfo {
  id: string;
  label: string; // short badge label
  color: string;
  // Which engine runs this language in the static browser build.
  client: Extract<EngineKind, 'pyodide' | 'js' | 'judge0'> | null;
  judge0Id?: number; // Judge0 CE language_id (absent => no Judge0 runtime)
}

export const LANGS: Record<string, LangInfo> = {
  python: { id: 'python', label: 'PY', color: '#3776ab', client: 'pyodide', judge0Id: 71 },
  javascript: { id: 'javascript', label: 'JS', color: '#b8860b', client: 'js', judge0Id: 63 },
  ruby: { id: 'ruby', label: 'RB', color: '#cc342d', client: 'judge0', judge0Id: 72 },
  perl: { id: 'perl', label: 'PL', color: '#39457e', client: 'judge0', judge0Id: 85 },
  bash: { id: 'bash', label: 'SH', color: '#4eaa25', client: 'judge0', judge0Id: 46 },
  swift: { id: 'swift', label: 'SW', color: '#f05138', client: 'judge0', judge0Id: 83 },
  dart: { id: 'dart', label: 'DA', color: '#0175c2', client: 'judge0', judge0Id: 90 },
  go: { id: 'go', label: 'GO', color: '#007d9c', client: 'judge0', judge0Id: 60 },
  zig: { id: 'zig', label: 'ZIG', color: '#f7a41d', client: null }, // no Judge0 CE runtime; dev-server only
  c: { id: 'c', label: 'C', color: '#5a6b7b', client: 'judge0', judge0Id: 50 },
  cpp: { id: 'cpp', label: 'C++', color: '#00599c', client: 'judge0', judge0Id: 54 },
  rust: { id: 'rust', label: 'RS', color: '#b7410e', client: 'judge0', judge0Id: 73 },
  java: { id: 'java', label: 'JV', color: '#b07219', client: 'judge0', judge0Id: 62 },
  php: { id: 'php', label: 'PHP', color: '#777bb4', client: 'judge0', judge0Id: 68 },
  typescript: { id: 'typescript', label: 'TS', color: '#3178c6', client: 'judge0', judge0Id: 74 },
  kotlin: { id: 'kotlin', label: 'KT', color: '#7f52ff', client: 'judge0', judge0Id: 78 },
  scala: { id: 'scala', label: 'SC', color: '#c22d40', client: 'judge0', judge0Id: 81 },
  lua: { id: 'lua', label: 'LUA', color: '#2c2d72', client: 'judge0', judge0Id: 64 },
  csharp: { id: 'csharp', label: 'C#', color: '#68217a', client: 'judge0', judge0Id: 51 },
};

export const ALL_LANGUAGES = Object.keys(LANGS);

// Languages that run with zero external dependencies in the static build.
export const FULLY_STATIC_LANGUAGES = ALL_LANGUAGES.filter((l) => {
  const c = LANGS[l].client;
  return c === 'pyodide' || c === 'js';
});

// Languages that need an external Judge0 API in the static build.
export const JUDGE0_LANGUAGES = ALL_LANGUAGES.filter((l) => LANGS[l].client === 'judge0');
