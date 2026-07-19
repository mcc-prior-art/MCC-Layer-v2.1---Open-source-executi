"""Single authoritative source of the ``mcc-core`` distribution version.

This module holds the ONE version string for the distribution. The build backend
reads it via setuptools' attribute-based dynamic version (see ``pyproject.toml``:
``[tool.setuptools.dynamic] version = {attr = "mcc._version.__version__"}``), and
``mcc/__init__.py`` re-exports it as ``mcc.__version__``.

Because the wheel/sdist metadata is generated from this exact attribute, the
installed distribution metadata version returned by
``importlib.metadata.version("mcc-core")`` equals ``mcc.__version__`` — a property
enforced by ``tests/test_version_contract.py``. Bump the version here and nowhere
else.
"""

from __future__ import annotations

__version__ = "0.1.0"
