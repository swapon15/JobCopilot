import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    environment: "jsdom",
    exclude: ["**/node_modules/**", "**/.next/**", "**/tests/e2e/**"],
    globals: true,
    setupFiles: ["./vitest.setup.ts"]
  }
});
