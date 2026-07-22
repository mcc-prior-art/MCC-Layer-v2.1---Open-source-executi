/**
 * Interoperability proposal originator (PR #48e).
 *
 * This is the VoltAgent side of the Multi-Adapter Interoperability Proof. It runs
 * a REAL native VoltAgent `Agent` (`@voltagent/core`) offline — the same agent
 * construction and the same deterministic (no-network, no-key) model the rest of
 * this integration uses — and lets the agent genuinely SELECT its governed tool
 * and fill the notification arguments. The tool here CAPTURES that proposal
 * instead of running the TypeScript governed path, because in the interop proof
 * the shared MCC Gateway (reached from Python over real HTTP) is the one and only
 * governance path. VoltAgent's job stops at originating the proposal — exactly
 * like the LangGraph / AutoGen / CrewAI adapters stop at their native step.
 *
 * It prints ONE line of JSON (the canonical notification content the native agent
 * proposed) to stdout; the Python `VoltAgentAdapter` reads it and normalizes it
 * into the shared canonical Integration Contract proposal. No governance, no
 * signing, no execution happens here.
 *
 * Usage:  tsx src/interop-originate.ts <email|pager>
 */

import { Agent, createTool } from "@voltagent/core";

import { createDeterministicModel } from "./model.js";
import {
  ACTION,
  type NotificationArgs,
  NotificationArgsSchema,
  PRIORITY_MAP,
  buildProposal,
} from "./schemas.js";
import { GOVERNED_TOOL_NAME } from "./tools/governed-notification.js";

const IDENTITY = { actor: "agent/notify-bot", resource: "notifications" } as const;

interface Captured {
  recipient: string;
  message: string;
  priority: number;
  channel: string;
}

async function originate(channel: "email" | "pager"): Promise<Captured> {
  let captured: Captured | null = null;

  // A native VoltAgent tool. The agent SELECTS it and fills the arguments; its
  // execute step captures the proposal (the interop harness governs it later).
  const captureTool = createTool({
    name: GOVERNED_TOOL_NAME,
    description:
      "Propose sending a customer notification. In the interoperability proof the " +
      "proposal is governed by the shared MCC Gateway, not here.",
    parameters: NotificationArgsSchema,
    execute: async (args: NotificationArgs) => {
      // Reuse the real proposal builder so the captured content is bound and
      // validated exactly as production would (strict schema, priority mapping).
      const proposal = buildProposal({ ...args, correlationId: "interop" }, IDENTITY);
      captured = {
        recipient: proposal.context.recipient,
        message: proposal.context.message,
        priority: proposal.context.priority,
        channel: proposal.context.channel,
      };
      return { status: "CAPTURED" as const };
    },
  });

  const agent = new Agent({
    name: "voltagent-interop-originator",
    purpose: "Originate a governed notification proposal for the interoperability proof.",
    instructions: `You help send customer notifications. To send anything you MUST call the ${GOVERNED_TOOL_NAME} tool — it is your only capability.`,
    model: createDeterministicModel() as never,
    tools: [captureTool],
  });

  // The channel word steers the deterministic model's native tool-argument parse
  // (a "pager" request drives the channel the shared policy rejects → DENY).
  const request =
    channel === "pager"
      ? "Notify customer-123 via pager that their appointment is confirmed"
      : "Notify customer-123 by email that their appointment is confirmed";

  await agent.generateText(request);

  if (!captured) {
    throw new Error("VoltAgent agent did not select the governed tool / emit a proposal");
  }
  return captured;
}

async function main(): Promise<void> {
  const channelArg = (process.argv[2] ?? "email").toLowerCase();
  const channel: "email" | "pager" = channelArg === "pager" ? "pager" : "email";
  const captured = await originate(channel);
  // Emit the canonical notification content the native agent proposed. The Python
  // adapter wraps this with the shared actor/action/resource and correlation id.
  const emitted = JSON.stringify({
    framework: "voltagent",
    action: ACTION,
    recipient: captured.recipient,
    message: captured.message,
    priority: captured.priority,
    channel: captured.channel,
    priority_map_normal: PRIORITY_MAP.normal,
  });
  process.stdout.write(`${emitted}\n`);
}

// VoltAgent keeps the event loop alive with background work, so (like this
// integration's demo/e2e runners) we exit explicitly once the proposal is emitted.
main()
  .then(() => process.exit(0))
  .catch((err) => {
    process.stderr.write(`${(err as Error).stack ?? String(err)}\n`);
    process.exit(1);
  });
