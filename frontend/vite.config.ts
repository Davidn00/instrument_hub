
import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");

  const apiTarget =
    env.VITE_DEV_PROXY_TARGET || "http://127.0.0.1:8200";

  return {
    plugins: [react(), tailwindcss()],

    server: {
      host: "127.0.0.1",
      port: 5173,
      strictPort: true,

      proxy: {
        "/api": {
          target: apiTarget,
          changeOrigin: true,
          ws: true,
        },
      },
    },
  };
});
