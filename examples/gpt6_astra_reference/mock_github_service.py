"""Mock GitHub service — the local external system the demo's real actuator
calls in its default (offline/CI) configuration.

A real, separate HTTP service (no governance logic whatsoever), mirroring
``pilot_notify/service.py``'s and ``clinic_service/service.py``'s existing
convention exactly: it exposes the one endpoint the real
:class:`~examples.gpt6_astra_reference.github_actuator.GitHubIssueActuator`
calls (``POST /repos/{owner}/{repo}/issues``), records every call, and
exposes ``GET /repos/{owner}/{repo}/issues`` so a test or demo run can
independently observe -- the dual-oracle side of every scenario -- whether
an issue was actually created, distinct from whatever MCC itself reports.

This is a stand-in for the real GitHub REST API, used so the reference
demo and its test suite need no real GitHub token or network access by
default. ``GitHubIssueActuator`` can equally be pointed at the real
``https://api.github.com`` when an operator explicitly opts into a live
run (see ``docs/GPT6_ASTRA_REFERENCE_INTEGRATION.md``) — this service is
never involved in that path.
"""

from __future__ import annotations

import threading
from typing import Any, Dict, List

from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, Field


class _State:
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.issues: List[Dict[str, Any]] = []

    def create(self, owner: str, repo: str, title: str, body: str) -> Dict[str, Any]:
        with self.lock:
            number = len(self.issues) + 1
            issue = {
                "number": number,
                "html_url": f"https://github.com/{owner}/{repo}/issues/{number}",
                "title": title,
                "body": body,
                "repo": f"{owner}/{repo}",
            }
            self.issues.append(issue)
            return issue


_STATE = _State()


def reset_issues() -> None:
    global _STATE
    _STATE = _State()


def recorded_issues() -> List[Dict[str, Any]]:
    return list(_STATE.issues)


class IssueIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str = Field(min_length=1)
    body: str = ""


def build_mock_github_service() -> FastAPI:
    app = FastAPI(title="MCC-Core Astra Demo — Mock GitHub Service")

    @app.get("/health")
    def health() -> Dict[str, Any]:
        return {"status": "ok", "service": "mock-github", "issues": len(_STATE.issues)}

    @app.get("/repos/{owner}/{repo}/issues")
    def list_issues(owner: str, repo: str) -> Dict[str, Any]:
        matching = [i for i in _STATE.issues if i["repo"] == f"{owner}/{repo}"]
        return {"count": len(matching), "issues": matching}

    @app.post("/repos/{owner}/{repo}/issues")
    def create_issue(owner: str, repo: str, body: IssueIn) -> Dict[str, Any]:
        return _STATE.create(owner, repo, body.title, body.body)

    return app


app = build_mock_github_service()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=9300, log_level="info")
