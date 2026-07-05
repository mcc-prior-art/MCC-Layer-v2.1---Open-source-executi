/**
 * Strict schemas for the governed notification proposal.
 *
 * These bind the VoltAgent tool arguments to the existing MCC-Core
 * `send_notification` contract (recipient / message / priority / channel /
 * correlation_id). The LLM only ever fills the *content* of a notification; the
 * actor identity, action, and resource come from trusted integration config —
 * the agent cannot choose its own authority.
 *
 * Proposal is not permission: a valid proposal is still only a request. MCC-Core
 * decides ALLOW / DENY / ESCALATE / CONSTRAIN.
 */

import { z } from "zod";

/** The action this integration proposes. Fixed — never chosen by the model. */
export const ACTION = "send_notification" as const;

/**
 * Priority words the model may use, mapped to the numeric priority the MCC
 * policy bounds. `high`/`urgent` exceed the pilot cap (3) and therefore drive a
 * CONSTRAIN (clamp), never a silent downgrade by the agent.
 */
export const PRIORITY_MAP: Record<string, number> = {
  low: 1,
  normal: 2,
  high: 9,
  urgent: 9,
};

/** Tool arguments the VoltAgent model fills. Deliberately minimal + strict. */
export const NotificationArgsSchema = z
  .object({
    recipient: z
      .string()
      .min(1)
      .max(200)
      .describe("Who to notify, e.g. an account id like customer-123"),
    message: z.string().min(1).max(2000).describe("The notification text to deliver"),
    priority: z
      .enum(["low", "normal", "high", "urgent"])
      .default("normal")
      .describe("Urgency; high/urgent may be constrained by policy"),
    channel: z
      .enum(["email", "sms", "pager"])
      .default("email")
      .describe("Delivery channel; some channels may not be permitted by policy"),
    correlationId: z
      .string()
      .min(1)
      .max(120)
      .optional()
      .describe("Optional caller correlation id; one is generated if omitted"),
  })
  .strict();

export type NotificationArgs = z.infer<typeof NotificationArgsSchema>;

/** The canonical notification payload sent to MCC-Core (the `context`). */
export const NotificationPayloadSchema = z
  .object({
    recipient: z.string().min(1),
    message: z.string().min(1),
    priority: z.number().int().min(1).max(9),
    channel: z.string().min(1),
    correlation_id: z.string().min(1),
  })
  .strict();

export type NotificationPayload = z.infer<typeof NotificationPayloadSchema>;

/** The full structured proposal submitted through the MCC contract. */
export const GovernedProposalSchema = z
  .object({
    actor: z.string().min(1),
    action: z.literal(ACTION),
    resource: z.string().min(1),
    context: NotificationPayloadSchema,
  })
  .strict();

export type GovernedProposal = z.infer<typeof GovernedProposalSchema>;

/** Trusted (non-model) identity/resource config for the governed tool. */
export interface ProposalIdentity {
  /** The actor identity MCC evaluates authority against (not model-chosen). */
  actor: string;
  /** The resource the action targets. */
  resource: string;
}

export function newCorrelationId(): string {
  return `corr-${crypto.randomUUID()}`;
}

/**
 * Build a validated governed proposal from model tool-args + trusted identity.
 * Throws (ZodError) on any invalid argument — a malformed proposal never reaches
 * the gateway.
 */
export function buildProposal(
  args: NotificationArgs,
  identity: ProposalIdentity,
): GovernedProposal {
  const parsed = NotificationArgsSchema.parse(args);
  const payload: NotificationPayload = {
    recipient: parsed.recipient,
    message: parsed.message,
    priority: PRIORITY_MAP[parsed.priority] ?? 2,
    channel: parsed.channel,
    correlation_id: parsed.correlationId ?? newCorrelationId(),
  };
  return GovernedProposalSchema.parse({
    actor: identity.actor,
    action: ACTION,
    resource: identity.resource,
    context: payload,
  });
}
