import { readFileSync, readdirSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";
import { MccClient, MccError } from "../src/mcc-client.js";

const SRC_DIR = fileURLToPath(new URL("../src", import.meta.url));

function tsFiles(dir: string): string[] {
  const out: string[] = [];
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    const p = join(dir, entry.name);
    if (entry.isDirectory()) out.push(...tsFiles(p));
    else if (entry.name.endsWith(".ts")) out.push(p);
  }
  return out;
}

describe("no direct external execution route (static)", () => {
  const files = tsFiles(SRC_DIR);

  it("only the MCC client performs network calls", () => {
    for (const f of files) {
      const src = readFileSync(f, "utf8");
      if (f.endsWith("mcc-client.ts")) continue;
      // No other module may call fetch, open sockets, spawn processes, or import
      // an HTTP/notification client. All side effects go through the MCC client.
      expect(src, `${f} must not call fetch directly`).not.toMatch(/\bfetch\s*\(/);
      expect(src, `${f} must not import node:http/https/net`).not.toMatch(
        /from\s+["']node:(http|https|net|dgram|tls)["']/,
      );
      expect(src, `${f} must not import axios/got/node-fetch`).not.toMatch(
        /from\s+["'](axios|got|node-fetch|undici)["']/,
      );
      expect(src, `${f} must not spawn processes`).not.toMatch(/from\s+["']node:child_process["']/);
    }
  });

  it("the MCC client knows only the gateway and quorum — never the notification service", () => {
    const src = readFileSync(join(SRC_DIR, "mcc-client.ts"), "utf8");
    // No notification-service endpoints appear anywhere in the client.
    expect(src).not.toMatch(
      /send_notification|\/notifications?\b|notify-service|notification-service/i,
    );
    // Its only base URLs are the gateway and the quorum.
    expect(src).toMatch(/gatewayUrl/);
    expect(src).toMatch(/quorumUrl/);
    // There is no direct-execute / send method exposed.
    expect(src).not.toMatch(/\b(send|notify|deliver|dispatch)Notification\s*\(/);
  });
});

describe("the agent cannot self-authorize (structural)", () => {
  it("a client without an operator key refuses operator actions (fail-closed)", async () => {
    const client = new MccClient({
      gatewayUrl: "http://127.0.0.1:1",
      quorumUrl: "http://127.0.0.1:1",
      apiKey: "k",
      // no operatorKey — this is how the agent's client is always built
    });
    await expect(client.approveAsOperator("req-x", "corr-x")).rejects.toBeInstanceOf(MccError);
  });

  it("buildGovernedAgentFromEnv never gives the agent an operator key", async () => {
    const src = readFileSync(join(SRC_DIR, "agent.ts"), "utf8");
    // The agent's client construction must not ASSIGN operatorKey (a comment
    // mentioning it is fine; a `operatorKey:` property is not).
    const agentClientBlock = src.slice(
      src.indexOf("new MccClient("),
      src.indexOf("});", src.indexOf("new MccClient(")),
    );
    expect(agentClientBlock).not.toMatch(/operatorKey\s*:/);
  });
});
