import { defineConfig } from 'vitest/config';

// Standalone Vitest config (kept separate from vite.config.ts so the dev-server
// runnerPlugin / BASE_PATH handling never runs during tests). jsdom gives the
// pure logic under test a localStorage + import.meta.env.BASE_URL ('/').
export default defineConfig({
  test: {
    environment: 'jsdom',
    globals: true,
    include: ['src/**/*.test.ts'],
  },
});
