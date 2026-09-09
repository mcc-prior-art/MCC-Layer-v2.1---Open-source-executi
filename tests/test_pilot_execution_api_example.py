"""Smoke test for the runnable Pilot Execution API reference composition
(``examples/pilot_execution_api/app.py``) -- proves the documented
shared-instance wiring (docs/PILOT_EXECUTION_API.md §11) actually works
end-to-end: a proposal submitted via the Phase 1 routes is visible to,
and executable through, the Phase 2 execute route on the SAME app.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from examples.pilot_execution_api.app import build_app


def test_example_app_shared_instance_wiring_end_to_end():
    app = build_app(tenants_credentials={"k": "demo-tenant"}, tenants_authority={"demo-tenant": {}})
    client = TestClient(app)

    r = client.post("/v1/proposals", headers={"x-api-key": "k"}, json={
        "logical_operation_id": "example-op", "actor": "agent/demo", "action": "send_notification",
        "resource": None, "payload": {"msg": "hi"},
    })
    assert r.status_code == 200
    assert r.json()["status"] == "PROPOSED"

    r2 = client.post("/v1/operations/example-op/execute", headers={"x-api-key": "k"})
    assert r2.status_code == 200
    assert r2.json()["status"] == "EXECUTED"

    r3 = client.get("/v1/operations/example-op", headers={"x-api-key": "k"})
    assert r3.json()["status"] == "EXECUTED"

    assert client.get("/health").status_code == 200


def test_example_app_default_credentials_work_out_of_the_box():
    app = build_app()
    client = TestClient(app)
    r = client.post("/v1/proposals", headers={"x-api-key": "demo-key"}, json={
        "logical_operation_id": "example-op-2", "actor": "agent/demo", "action": "send_notification",
        "resource": None, "payload": {},
    })
    assert r.status_code == 200
    r2 = client.post("/v1/operations/example-op-2/execute", headers={"x-api-key": "demo-key"})
    assert r2.status_code == 200
    assert r2.json()["status"] == "EXECUTED"
