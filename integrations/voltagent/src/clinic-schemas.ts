/**
 * Structured clinic-action proposal schema for the AXFlow clinic pilot.
 *
 * The model classifies a patient's natural-language request into ONE structured
 * clinic action. It fills the action content only — the actor identity and clinic
 * resource come from trusted config, so the agent cannot choose its own authority.
 * MCC-Core decides ALLOW / DENY / CONSTRAIN / ESCALATE on the proposal.
 *
 * Not medical advice, not a medical device — a governed business-workflow pilot.
 */

import { z } from "zod";
import { newCorrelationId } from "./schemas.js";

/** The clinic actions the agent may propose (governance decides each one). */
export const CLINIC_ACTIONS = [
  "appointment_book",
  "appointment_confirm",
  "patient_message_send",
  "lead_qualify",
  "discount_offer",
  "priority_mark",
  "refund_request",
  "complaint_escalate",
  "medical_advice_request",
] as const;

export type ClinicActionType = (typeof CLINIC_ACTIONS)[number];

/** Tool arguments the model fills (strict). */
export const ClinicArgsSchema = z
  .object({
    action_type: z.enum(CLINIC_ACTIONS).describe("The structured clinic action being proposed"),
    patient_request: z.string().min(1).max(2000).describe("The patient's original request"),
    patient_id: z.string().min(1).max(120).default("patient-unknown"),
    appointment_time: z.string().max(64).optional().describe("ISO-ish time for booking/confirm"),
    message: z.string().max(2000).optional().describe("Message text for patient_message_send"),
    channel: z.enum(["email", "sms"]).default("email"),
    risk_level: z.enum(["low", "normal", "high"]).default("normal"),
    requested_discount_percent: z
      .number()
      .int()
      .min(0)
      .max(100)
      .optional()
      .describe("For discount_offer; MCC clamps above the allowed cap"),
    priority_level: z
      .number()
      .int()
      .min(1)
      .max(3)
      .optional()
      .describe("For priority_mark; 1 routine .. 3 emergency; MCC clamps above the cap"),
    requires_human_review: z.boolean().default(false),
    correlationId: z.string().min(1).max(120).optional(),
  })
  .strict();

export type ClinicArgs = z.infer<typeof ClinicArgsSchema>;

/** Trusted (non-model) clinic identity. */
export interface ClinicIdentity {
  /** The actor MCC evaluates authority against (not model-chosen). */
  actor: string;
  /** The clinic resource the action targets. */
  clinicId: string;
}

/** The governed proposal submitted through the MCC contract. */
export interface ClinicProposal {
  actor: string;
  action: ClinicActionType;
  resource: string;
  context: Record<string, unknown>;
}

/**
 * Build a validated clinic proposal from model args + trusted identity. Throws
 * (ZodError) on any invalid argument — a malformed proposal never reaches MCC.
 * The payload fields (`requested_discount_percent`, `priority_level`) are named to
 * match the policy's `max_*` constraints so CONSTRAIN clamps them server-side.
 */
export function buildClinicProposal(args: ClinicArgs, identity: ClinicIdentity): ClinicProposal {
  const p = ClinicArgsSchema.parse(args);
  const context: Record<string, unknown> = {
    actor_id: identity.actor,
    action_type: p.action_type,
    clinic_id: identity.clinicId,
    patient_id: p.patient_id,
    patient_request: p.patient_request,
    channel: p.channel,
    risk_level: p.risk_level,
    requires_human_review: p.requires_human_review,
    correlation_id: p.correlationId ?? newCorrelationId(),
  };
  if (p.appointment_time) context.appointment_time = p.appointment_time;
  if (p.message) context.message = p.message;
  if (p.requested_discount_percent !== undefined) {
    context.requested_discount_percent = p.requested_discount_percent;
  }
  if (p.priority_level !== undefined) context.priority_level = p.priority_level;

  return { actor: identity.actor, action: p.action_type, resource: identity.clinicId, context };
}
