import { defineConfig, loadEnv } from 'vite'

export default defineConfig(({ mode }) => {
  // Load VITE_-prefixed env vars from .env files so the dev environment can use them.
  const env = loadEnv(mode, process.cwd());
  const apiBase = process.env.VITE_API_BASE || env.VITE_API_BASE || '';
  const appVersion = process.env.VITE_APP_VERSION || env.VITE_APP_VERSION || '11-S';

  return {
    // Build-time config injection. __API_BASE__ and __APP_VERSION__ are replaced
    // statically at build (and dev) time. Defaults: empty API base (relative
    // paths) and version "11-S".
    define: {
      __API_BASE__: JSON.stringify(apiBase),
      __APP_VERSION__: JSON.stringify(appVersion),
    },
    server: {
      port: 5173,
      proxy: {
        '/api': {
          target: 'http://localhost:8000',
          changeOrigin: true,
          secure: false,
        },
        '/favicon.svg': {
          target: 'http://localhost:8000',
          changeOrigin: true,
          secure: false,
        },
        '/fonts': {
          target: 'http://localhost:8000',
          changeOrigin: true,
          secure: false,
        },
      },
    },
    base: './',
    build: {
      outDir: 'dist',
      emptyOutDir: true,
    },
  };
})
