/**
 * Real VoltAgent governed integration with MCC-Core.
 *
 * VoltAgent provides agent reasoning and orchestration. MCC-Core provides
 * verified execution governance. The agent proposes; MCC-Core decides, gates,
 * executes through the governed executor, and verifies the external receipt. The
 * agent has no direct execution authority and no bypass path.
 *
 * This module is the public surface of the integration.
 */

export {
  MccClient,
  MccError,
  MccTransportError,
  MccDeniedError,
  MccExecutionError,
  MccAmbiguousExecutionError,
  receiptSummary,
} from "./mcc-client.js";
export type {
  Verdict,
  Decision,
  GovernedOutcome,
  ExecutionStatus,
  ReceiptSummary,
  MccClientOptions,
} from "./mcc-client.js";

export {
  ACTION,
  PRIORITY_MAP,
  NotificationArgsSchema,
  NotificationPayloadSchema,
  GovernedProposalSchema,
  buildProposal,
  newCorrelationId,
} from "./schemas.js";
export type {
  NotificationArgs,
  NotificationPayload,
  GovernedProposal,
  ProposalIdentity,
} from "./schemas.js";

export {
  createGovernedNotificationTool,
  GOVERNED_TOOL_NAME,
} from "./tools/governed-notification.js";
export type { GovernedToolConfig } from "./tools/governed-notification.js";

export {
  createGovernedAgent,
  agentEnv,
  buildGovernedAgentFromEnv,
} from "./agent.js";
export type { GovernedAgentConfig, AgentIdentityEnv } from "./agent.js";

export {
  resolveModel,
  createDeterministicModel,
  parseNotificationRequest,
} from "./model.js";
