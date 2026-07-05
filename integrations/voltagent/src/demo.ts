/**
 * Natural-language demonstration of the VoltAgent governed integration.
 *
 *   npm run demo -- "Send a confirmation to customer-123 that their order was approved"
 *
 * A user gives VoltAgent a natural-language instruction. VoltAgent interprets it,
 * selects the governed notification tool, constructs the structured proposal, and
 * submits it to MCC-Core. This script prints the boundary:
 *
 *   VoltAgent proposes. MCC-Core decides. The gate enforces. The governed
 *   executor acts. The external receipt proves execution. The audit chain records.
 *
 * Uses the deterministic offline model unless MCC_VOLTAGENT_MODEL_PROVIDER is set.
 */

import { buildGovernedAgentFromEnv } from "./agent.js";
import type { GovernedOutcome } from "./mcc-client.js";

const DEFAULT_REQUEST =
  "Send a confirmation notification to customer-123 that their order has been approved.";

async function main(): Promise<number> {
  const request = process.argv.slice(2).join(" ").trim() || DEFAULT_REQUEST;
  let outcome: GovernedOutcome | undefined;
  const { agent, provider, identity } = await buildGovernedAgentFromEnv(process.env, (o) => {
    outcome = o;
  });

  console.log("=".repeat(70));
  console.log("VoltAgent → MCC-Core governed integration (model provider:", provider, ")");
  console.log("=".repeat(70));
  console.log(`  user request        : ${request}`);
  console.log(`  agent identity      : ${identity.actor} on ${identity.resource}`);

  const result = await agent.generateText(request);

  if (!outcome) {
    console.log("  agent did NOT select the governed tool; nothing was proposed or executed.");
    console.log(`  agent said          : ${result.text}`);
    return 1;
  }

  console.log(`  governance verdict  : ${outcome.verdict}`);
  console.log(`  verdict reason      : ${outcome.reason}`);
  if (outcome.appliedConstraints.length > 0) {
    console.log(`  applied constraints : ${outcome.appliedConstraints.join(", ")}`);
  }
  if (outcome.approvalRequestId) {
    console.log(`  approval required   : request ${outcome.approvalRequestId} (not executed)`);
  }
  if (outcome.finalPayload) {
    console.log(`  executed payload    : ${JSON.stringify(outcome.finalPayload)}`);
  }
  console.log(`  execution status    : ${outcome.status}`);
  console.log(`  correlation id      : ${outcome.correlationId}`);
  if (outcome.receipt) {
    console.log(`  verified receipt    : ${JSON.stringify(outcome.receipt)}`);
  }
  if (outcome.auditRef) {
    console.log(`  audit reference     : ${outcome.auditRef}`);
  }
  if (outcome.error) {
    console.log(`  detail              : ${outcome.error}`);
  }
  console.log(`  agent said          : ${result.text}`);
  return 0;
}

main()
  .then((code) => process.exit(code))
  .catch((err) => {
    console.error("demo failed:", err);
    process.exit(1);
  });
