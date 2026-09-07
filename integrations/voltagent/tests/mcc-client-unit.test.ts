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
const captured: {
  correlationIds: string[];
  paths: string[];
  idempotencyKeys: (string | undefined)[];
  proposalBodies: Record<string, unknown>[];
} = { correlationIds: [], paths: [], idempotencyKeys: [], proposalBodies: [] };
let cfg: MockConfig = {};
// tenant-scoped in-memory proposal store for the mock /v1/proposals + /v1/operations/{id}
const mockProposals = new Map<string, { binding: string }>();

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

    if (url.pathname === "/v1/proposals" && req.method === "POST") {
      captured.proposalBodies.push(b);
      const logicalOperationId = String(b.logical_operation_id ?? "");
      const binding = JSON.stringify([b.action, b.resource, b.payload]);
      const existing = mockProposals.get(logicalOperationId);
      if (existing && existing.binding !== binding) {
        return json(res, 200, {
          contract_version: "v1",
          accepted: false,
          logical_operation_id: logicalOperationId,
          status: "BINDING_CONFLICT",
          reason: "logical_operation_id is already bound to a different action/resource/payload",
        });
      }
      mockProposals.set(logicalOperationId, { binding });
      return json(res, 200, {
        contract_version: "v1",
        accepted: true,
        logical_operation_id: logicalOperationId,
        status: "PROPOSED",
        proposal_binding: binding,
      });
    }
    if (url.pathname.startsWith("/v1/operations/") && req.method === "GET") {
      const logicalOperationId = decodeURIComponent(url.pathname.slice("/v1/operations/".length));
      const existing = mockProposals.get(logicalOperationId);
      if (!existing) {
        return json(res, 200, {
          contract_version: "v1",
          logical_operation_id: logicalOperationId,
          status: "NOT_FOUND",
        });
      }
      return json(res, 200, {
        contract_version: "v1",
        logical_operation_id: logicalOperationId,
        status: "PROPOSED",
        proposal_binding: existing.binding,
      });
    }

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
        captured.idempotencyKeys.push(b.idempotency_key as string | undefined);
        return json(res, 200, {
          status: cfg.executeStatus ?? "EXECUTED",
          reason: cfg.executeReason ?? "",
          execution: { receipt_verified: true, body: { received: true, correlation_id: "c" } },
          audit_ref: "aref",
        });
      case "/approvals":
        return json(res, 200, { request_id: "req-1", state: "PENDING" });
      case "/approvals/req-1/execute":
        captured.idempotencyKeys.push(b.idempotency_key as string | undefined);
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

/**
 * Round 26 — logical_operation_id (idempotency_key) end-to-end propagation.
 *
 * EnforcementCoordinator.enforce() now fails closed (MISSING_LOGICAL_OPERATION_ID)
 * without a non-empty idempotency_key. These tests prove the TS client side of
 * every VoltAgent/AXFlow-clinic pilot surface (which all funnel through
 * governNotification/governAction/executeApprovedNotification) always presents
 * one to /consensus/execute and /approvals/{id}/execute -- defaulting to the
 * operation's own correlationId when a caller doesn't supply one, never
 * inventing a fresh one per retry, and never silently dropping an explicit one.
 */
describe("Round 26 — logical_operation_id (idempotency_key) propagation", () => {
  it("defaults idempotency_key to the operation's correlationId when the caller supplies none", async () => {
    cfg = {};
    captured.idempotencyKeys.length = 0;
    const out = await client().governNotification(proposal, "corr-idem-default");
    expect(out.executed).toBe(true);
    expect(captured.idempotencyKeys.length).toBeGreaterThan(0);
    expect(captured.idempotencyKeys.every((k) => k === "corr-idem-default")).toBe(true);
  });

  it("never sends a missing/empty idempotency_key to /consensus/execute", async () => {
    cfg = {};
    captured.idempotencyKeys.length = 0;
    await client().governNotification(proposal, "corr-idem-nonempty");
    for (const k of captured.idempotencyKeys) {
      expect(typeof k).toBe("string");
      expect((k ?? "").trim().length).toBeGreaterThan(0);
    }
  });

  it("preserves an explicitly-supplied idempotency_key rather than overriding it with correlationId", async () => {
    cfg = {};
    captured.idempotencyKeys.length = 0;
    await client().governNotification(proposal, "corr-explicit-carrier", {
      idempotencyKey: "op-explicit-1",
    });
    expect(captured.idempotencyKeys.every((k) => k === "op-explicit-1")).toBe(true);
  });

  it("two calls for two DIFFERENT correlationIds get two DIFFERENT idempotency keys (never a shared/derived-from-payload constant)", async () => {
    cfg = {};
    captured.idempotencyKeys.length = 0;
    await client().governNotification(proposal, "corr-a");
    await client().governNotification(proposal, "corr-b");
    expect(captured.idempotencyKeys).toEqual(["corr-a", "corr-b"]);
  });

  it("a retried execute for the SAME operation reuses the SAME idempotency_key (never mints a fresh one)", async () => {
    // Simulate a caller retrying the exact same logical operation (e.g. after a
    // transient client-side error) by calling governNotification twice with the
    // SAME correlationId, as a retry driver would.
    cfg = {};
    captured.idempotencyKeys.length = 0;
    await client().governNotification(proposal, "corr-retry-same-op");
    await client().governNotification(proposal, "corr-retry-same-op");
    expect(captured.idempotencyKeys).toEqual(["corr-retry-same-op", "corr-retry-same-op"]);
  });

  it("ESCALATE -> approve preserves the SAME identity from proposal through to the approved execute", async () => {
    cfg = { evaluateVerdict: "ESCALATE" };
    captured.idempotencyKeys.length = 0;
    const c = client();
    const pending = await c.governNotification(proposal, "corr-escalate-preserve");
    expect(pending.status).toBe("PENDING_APPROVAL");
    expect(pending.approvalRequestId).toBe("req-1");

    // The operator step continues with the SAME correlationId the original
    // proposal carried -- exactly what pilot-cli.ts's escalation.json record +
    // operator_cli.py's re-use of it are for.
    cfg = { evaluateVerdict: "ESCALATE", executeStatus: "EXECUTED" };
    const done = await c.executeApprovedNotification(
      proposal,
      pending.approvalRequestId as string,
      { mandate: "granted" },
      "corr-escalate-preserve",
    );
    expect(done.status).toBe("EXECUTED");
    expect(captured.idempotencyKeys).toEqual(["corr-escalate-preserve"]);
  });
});

/**
 * Universal Proposal Service Phase 1 — VoltAgent facade.
 *
 * ``submitProposal``/``getOperationStatus`` are pure translation onto
 * POST /v1/proposals and GET /v1/operations/{id}: they must never touch
 * /evaluate, /consensus/execute, or /approvals/* (a proposal is never
 * permission), and the wire body they send must be exactly the canonical
 * ProposalRequestV1 shape (mcc_proposal.models.ALLOWED_REQUEST_FIELDS) every
 * other adapter (HTTP, MCP, LangGraph, CrewAI, AutoGen, the Python SDK) sends
 * for the identical semantic operation.
 */
describe("Universal Proposal Service Phase 1 — submitProposal / getOperationStatus", () => {
  it("submitProposal sends exactly the canonical ProposalRequestV1 field set", async () => {
    captured.proposalBodies.length = 0;
    captured.paths.length = 0;
    const out = await client().submitProposal(
      {
        logicalOperationId: "op-volt-1",
        actor: "agent/notify-bot",
        action: "send_notification",
        resource: "crm",
        payload: { recipient: "c-1", message: "hi" },
      },
      "corr-volt-1",
    );
    expect(captured.paths).toContain("/v1/proposals");
    expect(captured.paths).not.toContain("/evaluate");
    expect(captured.paths).not.toContain("/consensus/execute");
    expect(captured.paths).not.toContain("/approvals");
    expect(captured.proposalBodies.length).toBeGreaterThan(0);
    const sent = captured.proposalBodies[0] as Record<string, unknown>;
    expect(Object.keys(sent).sort()).toEqual(
      ["action", "actor", "logical_operation_id", "payload", "resource"].sort(),
    );
    expect(sent.logical_operation_id).toBe("op-volt-1");
    expect(out.status).toBe("PROPOSED");
    expect(out.accepted).toBe(true);
  });

  it("getOperationStatus is read-only and reflects a prior submitProposal", async () => {
    const c = client();
    await c.submitProposal(
      {
        logicalOperationId: "op-volt-2",
        actor: "agent/notify-bot",
        action: "send_notification",
        resource: "crm",
        payload: { recipient: "c-2" },
      },
      "corr-volt-2",
    );
    captured.paths.length = 0;
    const status = await c.getOperationStatus("op-volt-2", "corr-volt-2");
    expect(captured.paths).toEqual(["/v1/operations/op-volt-2"]);
    expect(status.status).toBe("PROPOSED");
  });

  it("getOperationStatus for an unknown operation reports NOT_FOUND (never fabricates a state)", async () => {
    const status = await client().getOperationStatus("op-volt-never-submitted", "corr-volt-3");
    expect(status.status).toBe("NOT_FOUND");
  });

  it("submitting the same logical_operation_id with a different payload reports BINDING_CONFLICT", async () => {
    const c = client();
    await c.submitProposal(
      {
        logicalOperationId: "op-volt-4",
        actor: "agent/notify-bot",
        action: "send_notification",
        resource: "crm",
        payload: { recipient: "c-4" },
      },
      "corr-volt-4a",
    );
    const conflict = await c.submitProposal(
      {
        logicalOperationId: "op-volt-4",
        actor: "agent/notify-bot",
        action: "send_notification",
        resource: "crm",
        payload: { recipient: "DIFFERENT" },
      },
      "corr-volt-4b",
    );
    expect(conflict.status).toBe("BINDING_CONFLICT");
    expect(conflict.accepted).toBe(false);
  });

  it("submitProposal performs no local validation of its own: it forwards logical_operation_id verbatim and relays exactly what the server decides", async () => {
    // The server (mcc_proposal.ProposalRequestV1) is the sole authority on
    // whether an id is valid -- the client never duplicates that judgment
    // (Section 2: "NO adapter may independently implement proposal identity
    // ... semantics"). This proves the client doesn't silently trim/reject
    // locally: whatever value is supplied travels to the wire unchanged.
    const out = await client().submitProposal(
      {
        logicalOperationId: "   ",
        actor: "agent/notify-bot",
        action: "send_notification",
        resource: "crm",
        payload: {},
      },
      "corr-volt-5",
    );
    expect(out.logical_operation_id).toBe("   ");
    expect(out.status).toBe("PROPOSED");
  });
});
