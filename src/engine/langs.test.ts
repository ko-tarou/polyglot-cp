import { describe, it, expect } from 'vitest';
import { LANGS, ALL_LANGUAGES, FULLY_STATIC_LANGUAGES, JUDGE0_LANGUAGES } from './langs';

// The language table is the source of truth for which engine runs each line.
// These tests pin the invariants the judge orchestrator relies on.
describe('LANGS table integrity', () => {
  it('exposes every key through ALL_LANGUAGES', () => {
    expect(ALL_LANGUAGES).toEqual(Object.keys(LANGS));
    expect(ALL_LANGUAGES.length).toBeGreaterThan(0);
  });

  it('keeps each entry id in sync with its map key', () => {
    for (const [key, info] of Object.entries(LANGS)) {
      expect(info.id).toBe(key);
      expect(info.label.length).toBeGreaterThan(0);
      expect(info.color).toMatch(/^#[0-9a-fA-F]{6}$/);
    }
  });

  it('requires a judge0Id for every judge0-client language', () => {
    for (const l of JUDGE0_LANGUAGES) {
      expect(LANGS[l].client).toBe('judge0');
      expect(typeof LANGS[l].judge0Id).toBe('number');
    }
  });

  it('marks python and javascript as the fully-static (no-dependency) languages', () => {
    expect([...FULLY_STATIC_LANGUAGES].sort()).toEqual(['javascript', 'python']);
    expect(LANGS.python.client).toBe('pyodide');
    expect(LANGS.javascript.client).toBe('js');
  });

  it('treats zig as dev-server-only: no client engine and no Judge0 runtime', () => {
    expect(LANGS.zig.client).toBeNull();
    expect(LANGS.zig.judge0Id).toBeUndefined();
    expect(JUDGE0_LANGUAGES).not.toContain('zig');
    expect(FULLY_STATIC_LANGUAGES).not.toContain('zig');
  });

  it('partitions languages so static + judge0 + null-client cover everything once', () => {
    const nullClient = ALL_LANGUAGES.filter((l) => LANGS[l].client === null);
    expect(FULLY_STATIC_LANGUAGES.length + JUDGE0_LANGUAGES.length + nullClient.length).toBe(ALL_LANGUAGES.length);
  });
});
