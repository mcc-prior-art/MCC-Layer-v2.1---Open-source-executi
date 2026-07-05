import { describe, expect, it } from "vitest";
import { receiptSummary } from "../src/mcc-client.js";
import {
  ACTION,
  GovernedProposalSchema,
  NotificationArgsSchema,
  PRIORITY_MAP,
  buildProposal,
} from "../src/schemas.js";

describe("proposal schema validation", () => {
  it("accepts a well-formed notification", () => {
    const parsed = NotificationArgsSchema.parse({
      recipient: "customer-123",
      message: "your order is confirmed",
      priority: "normal",
      channel: "email",
    });
    expect(parsed.recipient).toBe("customer-123");
  });

  it("rejects an empty recipient/message", () => {
    expect(() => NotificationArgsSchema.parse({ recipient: "", message: "x" })).toThrow();
    expect(() => NotificationArgsSchema.parse({ recipient: "c-1", message: "" })).toThrow();
  });

  it("rejects unknown fields (strict) and bad enums", () => {
    expect(() =>
      NotificationArgsSchema.parse({ recipient: "c-1", message: "m", evil: true }),
    ).toThrow();
    expect(() =>
      NotificationArgsSchema.parse({ recipient: "c-1", message: "m", channel: "carrier-pigeon" }),
    ).toThrow();
  });
});

describe("tool-args -> MCC contract mapping", () => {
  it("binds a trusted identity the model did not choose", () => {
    const p = buildProposal(
      { recipient: "customer-9", message: "hi", priority: "normal", channel: "email" },
      { actor: "agent/notify-bot", resource: "crm" },
    );
    expect(p.action).toBe(ACTION);
    expect(p.actor).toBe("agent/notify-bot");
    expect(p.resource).toBe("crm");
    // The proposal validates against the canonical contract schema.
    expect(() => GovernedProposalSchema.parse(p)).not.toThrow();
  });

  it("maps priority words to the numeric priority the policy bounds", () => {
    expect(PRIORITY_MAP.normal).toBe(2);
    expect(PRIORITY_MAP.high).toBe(9);
    expect(PRIORITY_MAP.urgent).toBe(9);
    const high = buildProposal(
      { recipient: "c-1", message: "m", priority: "high", channel: "email" },
      { actor: "a", resource: "r" },
    );
    expect(high.context.priority).toBe(9); // drives CONSTRAIN, never a silent downgrade
  });

  it("generates a correlation id when none is supplied", () => {
    const p = buildProposal(
      { recipient: "c-1", message: "m", priority: "low", channel: "sms" },
      { actor: "a", resource: "r" },
    );
    expect(p.context.correlation_id).toMatch(/^corr-/);
  });
});

describe("receipt summary redaction", () => {
  it("summarizes only safe receipt fields", () => {
    const s = receiptSummary({
      receipt_verified: true,
      upstream_status: 200,
      body: { received: true, correlation_id: "c", payload_sha256: "abc", secret: "TOP" },
    });
    expect(s?.receiptVerified).toBe(true);
    expect(s?.correlationId).toBe("c");
    expect(JSON.stringify(s)).not.toContain("TOP"); // no arbitrary fields leak
  });
});
