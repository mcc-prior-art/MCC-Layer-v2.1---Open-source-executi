# Self-contained image for the Framework-Neutral Reference Governed Agent demo.
#
# Build from the repository root:
#   docker build -f examples/reference_governed_agent/Dockerfile -t mcc-reference-agent .
#   docker run --rm mcc-reference-agent            # runs all four verdict scenarios
#
# The default command runs the CLI, which stands up an in-process governed stack
# (real MCC gateway + mock notification service + receipt-verifying governed
# executor) — no external services required. For the multi-container E2E (redis +
# gateway + mock + agent), use docker-compose.reference-agent.yml instead.
FROM python:3.11-slim

RUN useradd --create-home --uid 10006 mcc
WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Authoritative runtime + gateway + governed executor + mock service + SDK + the
# reference agent. The agent talks only to the gateway via the SDK.
COPY src /app/src
COPY gateway /app/gateway
COPY examples /app/examples
COPY pilot_notify /app/pilot_notify
COPY sdk /app/sdk

ENV PYTHONPATH=/app/src:/app:/app/sdk/python/src
USER mcc

# Run each verdict flow (auto-approve for ESCALATE so the demo is non-interactive).
CMD ["sh", "-c", "for s in allow deny constrain escalate; do python -m examples.reference_governed_agent.cli --scenario $s --operator auto; done"]
