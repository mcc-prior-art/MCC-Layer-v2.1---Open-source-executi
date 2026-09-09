"""Runnable reference composition for the Pilot Execution API (PR #111).

See ``docs/PILOT_EXECUTION_API.md`` §12 for why this is a standalone
example rather than wired into ``gateway/app.py``'s default startup.
"""

from .app import build_app

__all__ = ["build_app"]
