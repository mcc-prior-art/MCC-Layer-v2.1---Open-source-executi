/**
 * Vitest global setup: start the REAL MCC-Core governed stack (gateway + evaluator
 * quorum + mock notification service) in-process via the Python launcher, so the
 * TypeScript integration tests exercise genuine governance — not a mock.
 *
 * Set MCC_SKIP_INTEGRATION=1 to skip (unit tests still run).
 */

import { type ChildProcess, spawn } from "node:child_process";
import { GATEWAY_PORT, NOTIFY_PORT, QUORUM_PORT, REPO_ROOT, SKIP_INTEGRATION } from "./_config.js";

let proc: ChildProcess | undefined;

export async function setup(): Promise<void> {
  if (SKIP_INTEGRATION) {
    console.log("[globalSetup] MCC_SKIP_INTEGRATION=1 — skipping the real MCC stack.");
    return;
  }
  const python = process.env.MCC_PYTHON ?? "python3";
  proc = spawn(python, ["-m", "integrations.voltagent.mcc_side.testserver"], {
    cwd: REPO_ROOT,
    env: {
      ...process.env,
      MCC_GATEWAY_PORT: String(GATEWAY_PORT),
      MCC_QUORUM_PORT: String(QUORUM_PORT),
      MCC_NOTIFY_PORT: String(NOTIFY_PORT),
    },
    stdio: ["ignore", "pipe", "pipe"],
  });

  await new Promise<void>((resolve, reject) => {
    const timer = setTimeout(
      () => reject(new Error("MCC test stack did not become ready in 60s")),
      60_000,
    );
    let buf = "";
    const onData = (chunk: Buffer) => {
      buf += chunk.toString();
      if (buf.includes("MCC_TESTSERVER_READY")) {
        clearTimeout(timer);
        resolve();
      }
    };
    proc?.stdout?.on("data", onData);
    proc?.stderr?.on("data", (c: Buffer) => {
      buf += c.toString();
    });
    proc?.on("exit", (code) => {
      clearTimeout(timer);
      reject(new Error(`MCC test stack exited early (code ${code}). Output:\n${buf.slice(-2000)}`));
    });
  });
  console.log("[globalSetup] MCC governed stack is ready.");
}

export async function teardown(): Promise<void> {
  if (!proc) return;
  await new Promise<void>((resolve) => {
    proc?.on("exit", () => resolve());
    proc?.kill("SIGTERM");
    setTimeout(() => {
      proc?.kill("SIGKILL");
      resolve();
    }, 5_000);
  });
}
