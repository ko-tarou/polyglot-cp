import { defineConfig, devices } from '@playwright/test';

// E2E against the *static* production build served by `vite preview` (the same
// fully-client judge that ships to GitHub Pages). The webServer builds first so
// the run exercises real bundled assets + problem JSON, not the dev server.
const PORT = 4173;

export default defineConfig({
  testDir: './e2e',
  fullyParallel: false,
  workers: 1,
  timeout: 180_000, // first Pyodide load pulls CPython WASM from the CDN
  expect: { timeout: 15_000 },
  reporter: [['list']],
  use: {
    baseURL: `http://localhost:${PORT}`,
    trace: 'on-first-retry',
  },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
  webServer: {
    command: `npm run build && npm run preview -- --port ${PORT} --strictPort`,
    url: `http://localhost:${PORT}/`,
    timeout: 180_000,
    reuseExistingServer: !process.env.CI,
  },
});
