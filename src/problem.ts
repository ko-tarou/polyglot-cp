// Starter submission shown when the app loads. The default rotation (python ->
// javascript) is fully static: line 1 runs in Pyodide, line 2 in the JS worker,
// line 3 back in Pyodide - no external services needed.
//
// Problems themselves now come from the static catalog (src/problems.ts); this
// file only holds the editor's initial code + rotation.

export const DEFAULT_LANGUAGES = ['python', 'javascript'];

// A + B starter (the default selected problem is the first math problem):
//   line 1 (python)     : read "A B", print them back unchanged
//   line 2 (javascript) : read "A B", print A + B
//   line 3 (python)     : echo the answer as the final output
export const DEFAULT_CODE = [
  'import sys; print(sys.stdin.read().strip())',
  "const [a,b]=require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number); console.log(a+b);",
  'print(input())',
].join('\n');
