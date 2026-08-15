// MCC-Core Control Room — browser UI logic.
//
// This file only fetches from the local Control Room backend (`/api/*`) and
// renders what it receives. It never computes a decision, a token, a gate
// verdict, or an audit result itself.

const $ = (sel) => document.querySelector(sel);

async function api(path, opts) {
  const resp = await fetch(path, opts);
  const body = await resp.json().catch(() => ({}));
  if (!resp.ok) {
    throw new Error(body.detail || `${resp.status} ${resp.statusText}`);
  }
  return body;
}

async function refreshHealth() {
  const el = $("#gateway-status");
  try {
    const health = await api("/api/health");
    el.className = health.gateway_ready ? "status status--ok" : "status status--pending";
    el.textContent = `real gateway ${health.gateway_url} — ${health.gateway_ready ? "READY" : "not ready"} — policy ${health.gateway.policy_hash}`;
  } catch (err) {
    el.className = "status status--error";
    el.textContent = `gateway unreachable: ${err.message}`;
  }
}

function renderStage(stage) {
  const div = document.createElement("div");
  div.className = `stage ${stage.ok ? "stage--ok" : "stage--blocked"}`;
  const h4 = document.createElement("h4");
  h4.innerHTML = `<span>${stage.label}</span><span class="badge">${stage.ok ? "OK" : "BLOCKED"}</span>`;
  div.appendChild(h4);
  const pre = document.createElement("pre");
  pre.textContent = JSON.stringify(stage.detail, null, 2);
  div.appendChild(pre);
  return div;
}

function renderScenarioResult(result) {
  $("#result").hidden = false;
  $("#result-title").textContent = `${result.title} — ${result.passed ? "as expected" : "unexpected result"}`;
  $("#result-summary").textContent = result.summary;
  const container = $("#result-stages");
  container.innerHTML = "";
  result.stages.forEach((s) => container.appendChild(renderStage(s)));
  $("#result").scrollIntoView({ behavior: "smooth", block: "start" });
}

async function loadScenarios() {
  const { scenarios } = await api("/api/scenarios");
  const grid = $("#scenario-list");
  grid.innerHTML = "";
  scenarios.forEach((s) => {
    const card = document.createElement("div");
    card.className = "scenario-card";
    const h3 = document.createElement("h3");
    h3.textContent = s.title;
    const p = document.createElement("p");
    p.textContent = s.description;
    const btn = document.createElement("button");
    btn.textContent = "Run this scenario";
    btn.addEventListener("click", async () => {
      btn.disabled = true;
      btn.textContent = "Running…";
      try {
        const result = await api(`/api/scenarios/${s.id}/run`, { method: "POST" });
        renderScenarioResult(result);
      } catch (err) {
        alert(`Scenario failed to run: ${err.message}`);
      } finally {
        btn.disabled = false;
        btn.textContent = "Run this scenario";
      }
    });
    card.append(h3, p, btn);
    grid.appendChild(card);
  });
}

function stageFromDecisionResponse(data) {
  const stages = [
    { name: "proposed_action", label: "Proposed Action", ok: true, detail: data.proposed_action },
    { name: "mcc_decision", label: "MCC Decision", ok: true, detail: data.decision },
    { name: "decision_token", label: "Decision Token", ok: true, detail: data.token },
  ];
  if (data.audit) {
    stages.push({ name: "audit_record", label: "Audit Record (matching this proposal)", ok: true, detail: data.audit });
  }
  return stages;
}

async function handleCustomSubmit(event) {
  event.preventDefault();
  const mode = event.submitter.dataset.mode;
  const identity = $("#custom-identity").value.trim();
  const action = $("#custom-action").value.trim();
  const resource = $("#custom-resource").value.trim() || null;
  let context;
  try {
    context = JSON.parse($("#custom-context").value || "{}");
  } catch (err) {
    alert(`Context must be valid JSON: ${err.message}`);
    return;
  }

  try {
    const propose = await api("/api/propose", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ identity, action, context, resource_id: resource }),
    });
    let stages = stageFromDecisionResponse(propose);
    let summary = `MCC decision: ${propose.decision.decision} (${propose.decision.reason})`;

    if (mode === "execute" && (propose.decision.decision === "ALLOW" || propose.decision.decision === "CONSTRAIN")) {
      const execBody = propose.decision.decision === "CONSTRAIN" ? propose.decision.forward_context : context;
      const exec = await api("/api/execute", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ actor: identity, action, context: execBody, resource_id: resource }),
      });
      stages.push({ name: "gate_and_actuation", label: "Gate Verification & Actuation", ok: exec.gate_and_actuation.detail.executed, detail: exec.gate_and_actuation.detail });
      stages.push({ name: "actuation_result", label: "Actuation Result", ok: exec.gate_and_actuation.detail.executed, detail: exec.actuation_result.detail });
      summary += ` — execution: ${exec.gate_and_actuation.detail.status}`;
    } else if (mode === "execute") {
      stages.push({
        name: "gate_and_actuation", label: "Gate Verification & Actuation", ok: true,
        detail: { note: `Decision was ${propose.decision.decision}; only ALLOW/CONSTRAIN carry execution authority, so there is nothing to execute.` },
      });
    }

    renderScenarioResult({
      title: `Custom proposal — ${action}`,
      passed: true,
      summary,
      stages,
    });
  } catch (err) {
    alert(`Request failed: ${err.message}`);
  }
}

async function verifyChain() {
  const out = $("#verify-chain-output");
  out.textContent = "verifying…";
  try {
    const chain = await api("/api/audit/verify");
    out.textContent = JSON.stringify(chain, null, 2);
  } catch (err) {
    out.textContent = `error: ${err.message}`;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  refreshHealth();
  loadScenarios();
  $("#custom-form").addEventListener("submit", handleCustomSubmit);
  $("#verify-chain-btn").addEventListener("click", verifyChain);
  setInterval(refreshHealth, 15000);
});
