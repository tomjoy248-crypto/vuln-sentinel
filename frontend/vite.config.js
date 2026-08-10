import { defineConfig, loadEnv } from "vite";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd());
  const apiBase = process.env.VITE_API_BASE || env.VITE_API_BASE || "";
  const appVersion = process.env.VITE_APP_VERSION || env.VITE_APP_VERSION || "";

  return {
    define: {
      __API_BASE__: JSON.stringify(apiBase),
      __APP_VERSION__: JSON.stringify(appVersion),
    },
    server: {
      port: 5173,
      proxy: {
        "/api": {
          target: "http://localhost:8000",
          changeOrigin: true,
          secure: false,
        },
        "/favicon.svg": {
          target: "http://localhost:8000",
          changeOrigin: true,
          secure: false,
        },
        "/fonts": {
          target: "http://localhost:8000",
          changeOrigin: true,
          secure: false,
        },
      },
    },
    base: "./",
    build: {
      outDir: "dist",
      emptyOutDir: true,
    },
  };
});
