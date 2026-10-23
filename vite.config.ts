import { defineConfig } from "vite";

// Art assets are served from /assets so sprite paths match the asset tracker.
export default defineConfig({
  publicDir: "public",
  base: "./",
  test: { environment: "node", include: ["src/tests/**/*.test.ts"] },
} as any);
