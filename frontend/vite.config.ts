import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Dev server proxies /api, /static and /health to the FastAPI backend; in
// production set VITE_API_BASE_URL (see .env.example) to the deployed backend.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: "127.0.0.1",
    proxy: {
      "/api": { target: "http://127.0.0.1:8000", changeOrigin: true },
      "/static": { target: "http://127.0.0.1:8000", changeOrigin: true },
      "/health": { target: "http://127.0.0.1:8000", changeOrigin: true },
    },
  },
});
