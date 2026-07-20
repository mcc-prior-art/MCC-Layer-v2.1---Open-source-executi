"""``python -m mcc_evidence`` entrypoint (offline verification CLI)."""

from __future__ import annotations

import sys

from .cli import main

if __name__ == "__main__":
    sys.exit(main())
