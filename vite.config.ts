import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import { runnerPlugin } from './server/runner';

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  // Load .env (all keys, no VITE_ prefix filter) for the dev-server runner.
  const env = loadEnv(mode, process.cwd(), '');
  return {
    // Set BASE_PATH=/<repo>/ for GitHub Pages project sites; default '/' suits
    // Vercel and user/org Pages. import.meta.env.BASE_URL flows to asset fetches.
    base: env.BASE_PATH || '/',
    plugins: [
      react(),
      runnerPlugin({
        useJudge0: env.USE_JUDGE0 === 'true',
        judge0Url: env.JUDGE0_URL ?? '',
        judge0Key: env.JUDGE0_KEY ?? '',
        judge0Host: env.JUDGE0_HOST ?? '',
      }),
    ],
    server: { port: 5173 },
  };
});
