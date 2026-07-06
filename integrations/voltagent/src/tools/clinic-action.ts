/**
 * The single governed tool exposed to the AXFlow clinic agent.
 *
 * The agent classifies a patient request and SELECTS this tool, filling the
 * structured clinic action. It cannot do anything else: the tool validates the
 * arguments, binds them to a trusted actor/clinic the model did not choose, and
 * submits the proposal to MCC-Core. Selecting the tool is not permission — MCC
 * decides ALLOW/DENY/CONSTRAIN/ESCALATE, the gate enforces, the governed executor
 * acts against the mock clinic service, and EXECUTED is returned only on a
 * verified receipt. The tool holds no clinic-service client and no operator key.
 */

import { createTool } from "@voltagent/core";
import { ClinicArgsSchema, type ClinicIdentity, buildClinicProposal } from "../clinic-schemas.js";
import type { GovernedOutcome, MccClient } from "../mcc-client.js";
import { newCorrelationId } from "../schemas.js";

export const CLINIC_TOOL_NAME = "propose_clinic_action";

export interface ClinicToolConfig {
  client: MccClient;
  identity: ClinicIdentity;
  correlationId?: string;
  onOutcome?: (outcome: GovernedOutcome) => void;
}

export function createGovernedClinicTool(config: ClinicToolConfig) {
  return createTool({
    name: CLINIC_TOOL_NAME,
    description:
      "Propose a structured clinic action (booking, confirmation, patient " +
      "message, lead qualification, discount, priority, refund, complaint, or a " +
      "medical-advice request) for a patient. MCC-Core governs it: ALLOW / DENY / " +
      "ESCALATE / CONSTRAIN, and only reports EXECUTED after a verified clinic " +
      "receipt. This tool never contacts the clinic service directly.",
    parameters: ClinicArgsSchema,
    execute: async (args): Promise<GovernedOutcome> => {
      const correlationId = config.correlationId ?? args.correlationId ?? newCorrelationId();
      const proposal = buildClinicProposal({ ...args, correlationId }, config.identity);
      // Delegate EXCLUSIVELY to MCC-Core. No direct side effect happens here.
      const outcome = await config.client.governAction(proposal, correlationId);
      config.onOutcome?.(outcome);
      return outcome;
    },
  });
}
