/**
 * Deterministic patient-intent classifier + offline model for the clinic pilot.
 *
 * Classifies a patient's natural-language request into one structured clinic
 * action (the agent's reasoning) with no external API, key, or network — so the
 * demo, tests, and Docker E2E are reproducible offline. Classification is only
 * reasoning: MCC-Core still decides whether the proposed action may run. A real
 * LLM provider can be swapped in via env (see resolveModel in model.ts); the
 * governance is independent of the model.
 */

import type { LanguageModelV3CallOptions, LanguageModelV3GenerateResult } from "@ai-sdk/provider";
import { MockLanguageModelV3 } from "ai/test";
import type { ClinicActionType, ClinicArgs } from "./clinic-schemas.js";
import { CLINIC_TOOL_NAME } from "./tools/clinic-action.js";

function extractPatientId(t: string): string {
  return t.match(/\b((?:patient|pat|lead)-[\w]+)/i)?.[1]?.toLowerCase() ?? "patient-unknown";
}

/** Deterministically classify a patient request into a structured clinic action. */
export function classifyClinicRequest(text: string): ClinicArgs {
  const t = text.trim();
  const base = {
    patient_request: t || "(empty request)",
    patient_id: extractPatientId(t),
    channel: "email" as const,
    risk_level: "normal" as const,
    requires_human_review: false,
  };

  const pick = (action_type: ClinicActionType, extra: Partial<ClinicArgs> = {}): ClinicArgs =>
    ({ ...base, action_type, ...extra }) as ClinicArgs;

  // Unsafe medical advice / diagnosis / prescription -> DENY at MCC.
  if (
    /\b(antibiotic|prescri|diagnos|medical advice|what .*(take|medication|drug)|treat .*infection)/i.test(
      t,
    )
  ) {
    return pick("medical_advice_request", { risk_level: "high", requires_human_review: true });
  }
  // Human-review escalations.
  if (/\brefund\b/i.test(t)) return pick("refund_request", { requires_human_review: true });
  if (/\bcomplain|complaint\b/i.test(t))
    return pick("complaint_escalate", { requires_human_review: true });
  if (/\b(high[-\s]?risk|urgent (medical|care|handling)|high-risk procedure)\b/i.test(t)) {
    return pick("complaint_escalate", { risk_level: "high", requires_human_review: true });
  }
  // Commercial / operational actions that MCC clamps (CONSTRAIN).
  const discount = t.match(/(\d{1,3})\s*(?:%|percent)/i);
  if (/\bdiscount\b/i.test(t) || discount) {
    return pick("discount_offer", {
      requested_discount_percent: discount ? Number(discount[1]) : 50,
    });
  }
  if (/\b(priority|mark).*(emergency|urgent|priority)|emergency priority\b/i.test(t)) {
    const level = /emergency/i.test(t) ? 3 : 2;
    return pick("priority_mark", { priority_level: level });
  }
  // Normal booking / messaging (ALLOW within mandate).
  const time = t.match(/\b(\d{1,2}:\d{2})\b/);
  const when = `${/\btomorrow\b/i.test(t) ? "tomorrow " : ""}${time ? time[1] : ""}`.trim();
  if (/\bconfirm\b/i.test(t))
    return pick("appointment_confirm", { appointment_time: when || "unspecified" });
  if (/\b(book|schedule|appointment|reschedul)\b/i.test(t)) {
    return pick("appointment_book", { appointment_time: when || "unspecified" });
  }
  if (/\b(qualify|new lead|interested in)\b/i.test(t)) return pick("lead_qualify");
  return pick("patient_message_send", { message: t });
}

// -- offline model (Vercel AI SDK v6 mock) ----------------------------------- //

function extractUserText(prompt: unknown): string {
  if (!Array.isArray(prompt)) return "";
  const parts: string[] = [];
  for (const msg of prompt as Array<{ role?: string; content?: unknown }>) {
    if (msg.role !== "user") continue;
    if (typeof msg.content === "string") parts.push(msg.content);
    else if (Array.isArray(msg.content)) {
      for (const p of msg.content as Array<{ type?: string; text?: string }>) {
        if (p.type === "text" && typeof p.text === "string") parts.push(p.text);
      }
    }
  }
  return parts.join("\n");
}

function hasToolResult(prompt: unknown): boolean {
  return (
    Array.isArray(prompt) && (prompt as Array<{ role?: string }>).some((m) => m.role === "tool")
  );
}

/** A deterministic model: classify -> one clinic tool call, then a short summary. */
export function createClinicModel(): MockLanguageModelV3 {
  const usage: LanguageModelV3GenerateResult["usage"] = {
    inputTokens: { total: 1, noCache: undefined, cacheRead: undefined, cacheWrite: undefined },
    outputTokens: { total: 1, text: 1, reasoning: undefined },
  };
  const finish = (
    unified: "stop" | "tool-calls",
  ): LanguageModelV3GenerateResult["finishReason"] => ({
    unified,
    raw: undefined,
  });

  const doGenerate = async (
    options: LanguageModelV3CallOptions,
  ): Promise<LanguageModelV3GenerateResult> => {
    if (hasToolResult(options.prompt)) {
      return {
        content: [
          { type: "text", text: "The clinic action was submitted to MCC-Core for governance." },
        ],
        finishReason: finish("stop"),
        usage,
        warnings: [],
      };
    }
    const args = classifyClinicRequest(extractUserText(options.prompt));
    return {
      content: [
        {
          type: "tool-call",
          toolCallId: `call-${Math.random().toString(36).slice(2, 10)}`,
          toolName: CLINIC_TOOL_NAME,
          input: JSON.stringify(args),
        },
      ],
      finishReason: finish("tool-calls"),
      usage,
      warnings: [],
    };
  };
  return new MockLanguageModelV3({ doGenerate });
}
