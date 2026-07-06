import { describe, expect, it } from "vitest";
import { createClinicAgent } from "../src/clinic-agent.js";
import { classifyClinicRequest, createClinicModel } from "../src/clinic-model.js";
import {
  ClinicArgsSchema,
  type ClinicIdentity,
  buildClinicProposal,
} from "../src/clinic-schemas.js";
import type { GovernedOutcome, MccClient } from "../src/mcc-client.js";
import { createGovernedClinicTool } from "../src/tools/clinic-action.js";

const IDENTITY: ClinicIdentity = { actor: "agent/axflow-clinic", clinicId: "clinic-1" };

/** A fake MCC client that records the governed proposal instead of calling out. */
function fakeClient(): {
  client: MccClient;
  calls: Array<{ action: string; context: Record<string, unknown> }>;
} {
  const calls: Array<{ action: string; context: Record<string, unknown> }> = [];
  const client = {
    governAction: async (proposal: { action: string; context: Record<string, unknown> }) => {
      calls.push({ action: proposal.action, context: proposal.context });
      return {
        verdict: "ALLOW",
        status: "EXECUTED",
        executed: true,
        reason: "ok",
        correlationId: String(proposal.context.correlation_id),
        appliedConstraints: [],
      } satisfies GovernedOutcome;
    },
  } as unknown as MccClient;
  return { client, calls };
}

describe("clinic intent classification", () => {
  it("classifies the four canonical patient requests", () => {
    expect(
      classifyClinicRequest("I want to book a dental cleaning tomorrow at 15:00.").action_type,
    ).toBe("appointment_book");
    expect(
      classifyClinicRequest("Tell me what antibiotics to take for this infection.").action_type,
    ).toBe("medical_advice_request");
    expect(classifyClinicRequest("Give this patient a 90% discount.").action_type).toBe(
      "discount_offer",
    );
    expect(classifyClinicRequest("I want a refund for my treatment.").action_type).toBe(
      "refund_request",
    );
  });

  it("extracts the discount percent and a booking time", () => {
    const d = classifyClinicRequest("Give a 90% discount");
    expect(d.requested_discount_percent).toBe(90);
    const b = classifyClinicRequest("book me tomorrow at 09:30");
    expect(b.appointment_time).toContain("09:30");
  });

  it("routes complaints and emergency-priority + medical advice safely", () => {
    expect(classifyClinicRequest("I want to complain about a doctor.").action_type).toBe(
      "complaint_escalate",
    );
    expect(classifyClinicRequest("Mark this patient as emergency priority.").action_type).toBe(
      "priority_mark",
    );
    expect(classifyClinicRequest("prescribe me something").action_type).toBe(
      "medical_advice_request",
    );
  });
});

describe("clinic proposal schema + mapping", () => {
  it("binds a trusted identity the model did not choose, and constraint-named fields", () => {
    const p = buildClinicProposal(
      {
        action_type: "discount_offer",
        patient_request: "big discount",
        patient_id: "patient-9",
        requested_discount_percent: 90,
        channel: "email",
        risk_level: "normal",
        requires_human_review: false,
      },
      IDENTITY,
    );
    expect(p.actor).toBe("agent/axflow-clinic");
    expect(p.action).toBe("discount_offer");
    expect(p.resource).toBe("clinic-1");
    // The field name matches the policy's max_ constraint so MCC can clamp it.
    expect(p.context.requested_discount_percent).toBe(90);
    expect(p.context.actor_id).toBe("agent/axflow-clinic");
    expect(p.context.correlation_id).toMatch(/^corr-/);
  });

  it("rejects unknown action types and extra fields (strict)", () => {
    expect(() =>
      ClinicArgsSchema.parse({ action_type: "steal_money", patient_request: "x" }),
    ).toThrow();
    expect(() =>
      ClinicArgsSchema.parse({ action_type: "lead_qualify", patient_request: "x", evil: true }),
    ).toThrow();
  });
});

describe("clinic tool + agent (offline)", () => {
  it("the governed tool maps args -> proposal -> MCC (no direct clinic call)", async () => {
    const { client, calls } = fakeClient();
    const tool = createGovernedClinicTool({ client, identity: IDENTITY });
    await (tool.execute as (a: unknown, o?: unknown) => Promise<GovernedOutcome>)(
      { action_type: "appointment_book", patient_request: "book me", appointment_time: "15:00" },
      {},
    );
    expect(calls).toHaveLength(1);
    expect(calls[0]?.action).toBe("appointment_book");
    expect(calls[0]?.context.clinic_id).toBe("clinic-1");
  });

  it("the AXFlow agent classifies a patient request and selects the governed clinic tool", async () => {
    const { client, calls } = fakeClient();
    let captured: GovernedOutcome | undefined;
    const agent = createClinicAgent({
      client,
      identity: IDENTITY,
      model: createClinicModel(),
      onOutcome: (o) => {
        captured = o;
      },
    });
    await agent.generateText("I want to book a dental cleaning tomorrow at 15:00.");
    expect(captured?.status).toBe("EXECUTED");
    expect(calls[0]?.action).toBe("appointment_book");
  });
});
