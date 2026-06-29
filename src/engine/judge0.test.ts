import { describe, it, expect, beforeEach } from 'vitest';
import { loadJudge0Config, saveJudge0Config, judge0Configured } from './judge0';

// Judge0 credentials live only in localStorage (never bundled/committed). These
// tests cover the load/save round-trip + the "is it usable?" predicate that
// gates whether the orchestrator even attempts a Judge0 request.
describe('judge0 config storage', () => {
  beforeEach(() => localStorage.clear());

  it('returns sane defaults when nothing is stored', () => {
    const cfg = loadJudge0Config();
    expect(cfg.url).toBe('');
    expect(cfg.key).toBe('');
    expect(cfg.host).toBe('judge0-ce.p.rapidapi.com');
  });

  it('round-trips a saved config', () => {
    const cfg = { url: 'https://judge0.example/', key: 'secret', host: 'h.rapidapi.com' };
    saveJudge0Config(cfg);
    expect(loadJudge0Config()).toEqual(cfg);
  });

  it('falls back to defaults when stored JSON is corrupt', () => {
    localStorage.setItem('pcp.judge0', '{not json');
    expect(loadJudge0Config().host).toBe('judge0-ce.p.rapidapi.com');
  });

  it('treats a non-empty url as configured', () => {
    expect(judge0Configured({ url: 'https://x', key: '', host: '' })).toBe(true);
  });

  it('treats an empty or whitespace url as not configured', () => {
    expect(judge0Configured({ url: '', key: 'k', host: 'h' })).toBe(false);
    expect(judge0Configured({ url: '   ', key: 'k', host: 'h' })).toBe(false);
  });
});
