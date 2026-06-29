import { describe, it, expect } from 'vitest';
import { languageForLines } from './types';

// languageForLines drives the editor gutter badges. The contract that matters
// for grading: only NON-empty lines consume a rotation slot, so the badge a
// user sees on a line matches the language the engine will actually run it in.
describe('languageForLines', () => {
  it('assigns rotation languages to non-empty lines in order', () => {
    const code = 'a\nb\nc';
    expect(languageForLines(code, ['python', 'javascript'])).toEqual(['python', 'javascript', 'python']);
  });

  it('returns null for blank / whitespace-only lines and does not consume a slot', () => {
    const code = 'a\n\n   \nb';
    // line1 -> python, blanks -> null (no slot), line4 -> javascript (slot #2)
    expect(languageForLines(code, ['python', 'javascript'])).toEqual(['python', null, null, 'javascript']);
  });

  it('cycles through more than two languages', () => {
    const code = '1\n2\n3\n4\n5';
    expect(languageForLines(code, ['python', 'javascript', 'ruby'])).toEqual([
      'python',
      'javascript',
      'ruby',
      'python',
      'javascript',
    ]);
  });

  it('uses a single language for every line when only one is given', () => {
    expect(languageForLines('a\nb\nc', ['ruby'])).toEqual(['ruby', 'ruby', 'ruby']);
  });

  it('falls back to python when the language list is empty', () => {
    expect(languageForLines('a\nb', [])).toEqual(['python', 'python']);
  });

  it('returns all nulls for entirely blank input', () => {
    expect(languageForLines('\n\n', ['python', 'javascript'])).toEqual([null, null, null]);
  });

  it('keeps the gutter length equal to the physical line count', () => {
    const code = 'x\n\ny\n\nz';
    const langs = languageForLines(code, ['python', 'javascript']);
    expect(langs).toHaveLength(code.split('\n').length);
  });
});
