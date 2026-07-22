"""Adapter SDK version — reuses the repository's single-source distribution version.

The Adapter SDK ships **inside** the existing ``mcc-core`` distribution (no separate
package, no separate version). ``SDK_VERSION`` therefore mirrors the single
authoritative version string in ``mcc._version`` — the same source the ``mcc-core``
wheel/sdist metadata is generated from. There is no second version number.
"""

from __future__ import annotations

from mcc._version import __version__ as SDK_VERSION

__all__ = ["SDK_VERSION"]
