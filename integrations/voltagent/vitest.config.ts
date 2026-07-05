import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    globalSetup: ["./tests/globalSetup.ts"],
    include: ["tests/**/*.test.ts"],
    testTimeout: 30_000,
    hookTimeout: 70_000,
    // The VoltAgent runtime keeps background timers alive; isolate + don't hang.
    pool: "forks",
    reporters: ["default"],
  },
});
