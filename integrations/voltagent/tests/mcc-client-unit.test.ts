import { type IncomingMessage, type Server, type ServerResponse, createServer } from "node:http";
import type { AddressInfo } from "node:net";
import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { MccClient } from "../src/mcc-client.js";

/**
 * A controllable mock of the gateway + quorum contract, used to test the TS
 * client's dispatch and fail-closed behavior deterministically (no Python). The
 * REAL governance is exercised by the integration + Python tests; here we assert
 * that the client never fabricates success and always propagates correlation.
 */
interface MockConfig {
  evaluateVerdict?: string;
  executeStatus?: string;
  executeReason?: string;
}

let server: Server;
let baseUrl: string;
const captured: { correlationIds: string[]; paths: string[] } = { correlationIds: [], paths: [] };
let cfg: MockConfig = {};

function body(req: IncomingMessage): Promise<Record<string, unknown>> {
  return new Promise((resolve) => {
    let raw = "";
    req.on("data", (c) => {
      raw += c;
    });
    req.on("end", () => resolve(raw ? JSON.parse(raw) : {}));
  });
}

function json(res: ServerResponse, code: number, obj: unknown): void {
  res.writeHead(code, { "content-type": "application/json" });
  res.end(JSON.stringify(obj));
}

beforeAll(async () => {
  server = createServer(async (req, res) => {
    const url = new URL(req.url ?? "/", "http://localhost");
    captured.paths.push(url.pathname);
    const cid = req.headers["x-mcc-correlation-id"];
    if (typeof cid === "string") captured.correlationIds.push(cid);
    const b = req.method === "POST" ? await body(req) : {};

    switch (url.pathname) {
      case "/evaluate":
        return json(res, 200, {
          decision: cfg.evaluateVerdict ?? "ALLOW",
          reason: "mock",
          audit_id: "audit-1",
          actor_id: b.actor_id,
          resource_id: b.resource_id,
          forward_context: b.context,
        });
      case "/consensus/challenge":
        return json(res, 200, { challenge_id: "ch-1", nonce: "nonce-1" });
      case "/vote":
        return json(res, 200, {
          verdict: "ALLOW",
          authorized_context: b.context,
          votes: [{ v: 1 }],
        });
      case "/consensus/execute":
        return json(res, 200, {
          status: cfg.executeStatus ?? "EXECUTED",
          reason: cfg.executeReason ?? "",
          execution: { receipt_verified: true, body: { received: true, correlation_id: "c" } },
          audit_ref: "aref",
        });
      case "/verify":
        return json(res, 200, { valid: true });
      default:
        return json(res, 404, { error: "not found" });
    }
  });
  await new Promise<void>((r) => server.listen(0, "127.0.0.1", r));
  const { port } = server.address() as AddressInfo;
  baseUrl = `http://127.0.0.1:${port}`;
});

afterAll(() => {
  server.close();
});

function client(url = baseUrl): MccClient {
  return new MccClient({ gatewayUrl: url, quorumUrl: url, apiKey: "k" });
}

const proposal = {
  actor: "agent/notify-bot",
  action: "send_notification" as const,
  resource: "crm",
  context: {
    recipient: "c-1",
    message: "m",
    priority: 2,
    channel: "email",
    correlation_id: "corr-unit",
  },
};

describe("MCC client fail-closed + correlation", () => {
  it("propagates the correlation id on every request", async () => {
    cfg = {};
    captured.correlationIds.length = 0;
    await client().governNotification(proposal, "corr-XYZ");
    expect(captured.correlationIds.length).toBeGreaterThan(0);
    expect(captured.correlationIds.every((c) => c === "corr-XYZ")).toBe(true);
  });

  it("fails closed when the gateway is unreachable (never reports success)", async () => {
    const dead = client("http://127.0.0.1:1");
    const out = await dead.governNotification(proposal, "corr-dead");
    expect(out.executed).toBe(false);
    expect(out.status === "ERROR" || out.status === "BLOCKED").toBe(true);
  });

  it("never reports EXECUTED when the governed executor rejected the receipt", async () => {
    cfg = { executeStatus: "BLOCKED", executeReason: "receipt payload hash does not match" };
    const out = await client().governNotification(proposal, "corr-forged");
    expect(out.executed).toBe(false);
    expect(out.status).toBe("BLOCKED");
  });

  it("surfaces a replayed/duplicate authorization as not-executed", async () => {
    cfg = { executeStatus: "BLOCKED", executeReason: "nonce already consumed" };
    const out = await client().governNotification(proposal, "corr-replay");
    expect(out.executed).toBe(false);
    expect(out.error).toMatch(/replay|duplicate/i);
  });

  it("DENY never executes and never calls consensus execute", async () => {
    cfg = { evaluateVerdict: "DENY" };
    captured.paths.length = 0;
    const out = await client().governNotification(proposal, "corr-deny");
    expect(out.verdict).toBe("DENY");
    expect(out.executed).toBe(false);
    expect(captured.paths).not.toContain("/consensus/execute");
  });

  it("fails closed on an unexpected/unknown verdict (never attempts execution)", async () => {
    cfg = { evaluateVerdict: "WAT" };
    captured.paths.length = 0;
    const out = await client().governNotification(proposal, "corr-unknown");
    expect(out.executed).toBe(false);
    expect(out.status).toBe("BLOCKED");
    expect(captured.paths).not.toContain("/consensus/execute");
  });
});
