/**
 * The single governed tool exposed to the VoltAgent agent.
 *
 * The agent may SELECT this tool and fill its arguments (the notification
 * content). It cannot do anything else: the tool validates the arguments with a
 * strict schema, binds them to a trusted actor/resource the model did not choose,
 * submits the proposal through MCC-Core, and returns the governance outcome.
 *
 * The tool holds no notification-service client, no operator key, and no
 * execution path of its own. Selecting it is not permission — MCC-Core decides,
 * the gate enforces, the governed executor acts, and EXECUTED is returned only
 * when MCC-Core has verified the external receipt.
 */

import { createTool } from "@voltagent/core";
import type { MccClient } from "../mcc-client.js";
import type { GovernedOutcome } from "../mcc-client.js";
import {
  NotificationArgsSchema,
  type ProposalIdentity,
  buildProposal,
  newCorrelationId,
} from "../schemas.js";

export interface GovernedToolConfig {
  client: MccClient;
  identity: ProposalIdentity;
  /** Optional fixed correlation id (tests); a fresh one is generated otherwise. */
  correlationId?: string;
  /** Observe the governed outcome of each invocation (demos/tests). */
  onOutcome?: (outcome: GovernedOutcome) => void;
}

export const GOVERNED_TOOL_NAME = "propose_governed_notification";

/**
 * Build the governed notification tool bound to an MCC client + trusted identity.
 */
export function createGovernedNotificationTool(config: GovernedToolConfig) {
  return createTool({
    name: GOVERNED_TOOL_NAME,
    description:
      "Propose sending a customer notification. The proposal is governed by " +
      "MCC-Core, which decides ALLOW / DENY / ESCALATE / CONSTRAIN, gates " +
      "execution, and only reports EXECUTED after a verified external receipt. " +
      "This tool never contacts the notification service directly.",
    parameters: NotificationArgsSchema,
    execute: async (args): Promise<GovernedOutcome> => {
      const correlationId = config.correlationId ?? args.correlationId ?? newCorrelationId();
      // Bind model-supplied content to a trusted identity + strict schema. A
      // malformed argument throws here and never reaches the gateway.
      const proposal = buildProposal({ ...args, correlationId }, config.identity);
      // Delegate EXCLUSIVELY to MCC-Core. No direct side effect happens here.
      const outcome = await config.client.governNotification(proposal, correlationId);
      config.onOutcome?.(outcome);
      return outcome;
    },
  });
}
