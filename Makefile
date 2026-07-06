# Deployable VoltAgent + MCC-Core pilot — operator commands.
#
# Typical flow:
#   make pilot-up        # build + start the stack (detached)
#   make pilot-ready     # wait until MCC + quorum are READY
#   make pilot-allow     # compliant request  -> EXECUTED
#   make pilot-deny      # prohibited request -> blocked
#   make pilot-constrain # excessive request  -> clamped + EXECUTED
#   make pilot-escalate  # high-risk request  -> PENDING_APPROVAL
#   make pilot-approve   # operator approves  -> EXECUTED
#   make pilot-audit-verify   # verify the cryptographic audit chain
#   make pilot-restart-check  # prove audit survives a restart
#   make pilot-down      # stop (KEEPS volumes -> audit persists)
#   make pilot-clean     # stop + remove volumes (wipes audit)
#
# The VoltAgent agent never holds the operator key and has no network route to
# the external service. See docs/PILOT_VOLTAGENT_DEPLOYMENT.md.

COMPOSE ?= docker compose -f docker-compose.pilot-voltagent.yml --env-file .env.pilot
AGENT   := $(COMPOSE) exec -T voltagent-agent
GATEWAY := $(COMPOSE) exec -T mcc-gateway

.PHONY: pilot-config pilot-up pilot-ready pilot-allow pilot-deny pilot-constrain \
        pilot-escalate pilot-approve pilot-audit-verify pilot-restart-check \
        pilot-demo pilot-down pilot-clean pilot-logs pilot-ps

pilot-config: ## Create .env.pilot from the template if missing
	@test -f .env.pilot || cp .env.pilot.example .env.pilot
	@echo ".env.pilot ready (edit it to change keys/endpoints)."

pilot-up: pilot-config ## Build + start the full pilot stack (detached)
	$(COMPOSE) up --build -d

pilot-ready: ## Wait until the gateway + quorum report READY (fail-closed)
	@echo "waiting for pilot readiness..."
	@for i in $$(seq 1 100); do \
	  if $(AGENT) node -e "fetch('http://mcc-gateway:8001/ready').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))" 2>/dev/null \
	     && $(AGENT) node -e "fetch('http://evaluator-quorum:8080/ready').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))" 2>/dev/null; then \
	    echo "pilot READY"; exit 0; fi; \
	  sleep 3; done; \
	echo "pilot did not become ready in time"; exit 1

pilot-allow: ## ALLOW: a compliant request -> governed execution -> EXECUTED
	$(AGENT) npx tsx src/pilot-cli.ts allow

pilot-deny: ## DENY: a prohibited request -> blocked, external service never called
	$(AGENT) npx tsx src/pilot-cli.ts deny

pilot-constrain: ## CONSTRAIN: an excessive request -> only the clamped payload executes
	$(AGENT) npx tsx src/pilot-cli.ts constrain

pilot-escalate: ## ESCALATE: a high-risk request -> PENDING_APPROVAL (no execution yet)
	$(AGENT) npx tsx src/pilot-cli.ts escalate

pilot-approve: ## Operator approves the pending escalation -> EXECUTED (operator key)
	$(GATEWAY) python -m integrations.voltagent.mcc_side.operator_cli

pilot-audit-verify: ## Verify the persisted cryptographic audit chain
	$(GATEWAY) python -c "import sys; sys.path.insert(0,'/app/src'); from mcc_core import AuditLog; ok=AuditLog.verify_chain('/data/audit.jsonl'); print('audit chain valid=%s' % ok); sys.exit(0 if ok else 1)"

pilot-restart-check: ## Prove the audit chain survives a restart
	$(MAKE) pilot-allow
	@echo "restarting the gateway (audit + keys are on persistent volumes)..."
	$(COMPOSE) restart mcc-gateway
	$(MAKE) pilot-ready
	$(MAKE) pilot-audit-verify
	@echo "audit persisted and re-verified after restart."

pilot-demo: ## Run all four scenarios + approval + audit verification end to end
	$(MAKE) pilot-allow
	$(MAKE) pilot-deny
	$(MAKE) pilot-constrain
	$(MAKE) pilot-escalate
	$(MAKE) pilot-approve
	$(MAKE) pilot-audit-verify
	@echo "\nPILOT DEMO COMPLETE: ALLOW + DENY + CONSTRAIN + ESCALATE(+approve) + audit verified."

pilot-ps: ## Show pilot container status
	$(COMPOSE) ps

pilot-logs: ## Tail pilot logs
	$(COMPOSE) logs --no-color --timestamps

pilot-down: ## Stop the stack, KEEPING volumes (audit persists)
	$(COMPOSE) down

pilot-clean: ## Stop the stack and REMOVE volumes (wipes the audit chain)
	$(COMPOSE) down -v --remove-orphans
