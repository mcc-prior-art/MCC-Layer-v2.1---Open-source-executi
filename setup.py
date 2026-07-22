"""Packaging shim for the ``mcc-core`` distribution (PR #50).

Metadata + package layout live in ``pyproject.toml``. This file exists only to add a
**narrow packaging correction**: the wheel/sdist include the public facade (``mcc``),
the Adapter SDK (``mcc_adapter_sdk``), and the Canonical Governance Protocol
(``mcc_protocol``). Those import only *pure* primitives from ``mcc_core`` (canonical
hashing) and ``mcc_compliance`` (the capability vocabulary). To satisfy the clean
install without shipping the governance engine, the custom ``build_py`` below ships
only the governance-free modules of ``mcc_core`` and ``mcc_compliance`` and excludes
the execution gate, authority, coordinator, consensus, mandate, audit, nonce,
policy, velocity, idempotency, challenge, approvals, profiles, redis client, and the
whole compliance runner/reporting/program/registry/adapters surface. Importing the
SDK/protocol never loads those (they resolve lazily), so a clean install is fully
functional while remaining engine-free.
"""

from __future__ import annotations

from setuptools import setup
from setuptools.command.build_py import build_py as _build_py

# The ONLY modules of the heavy packages that ship in the distribution. Everything
# else in these packages is governance/suite code and is excluded from the wheel.
_SHIP_ONLY = {
    "mcc_core": {"__init__", "signing", "version"},
    # capability_profile imports the pure models module (SUITE_VERSION); both are
    # governance-free. Nothing else from the compliance suite ships.
    "mcc_compliance": {"__init__", "capability_profile", "models"},
}


class build_py(_build_py):
    """Ship only the governance-free modules of the curated heavy packages."""

    def find_package_modules(self, package, package_dir):
        modules = super().find_package_modules(package, package_dir)
        allow = _SHIP_ONLY.get(package)
        if allow is None:
            return modules
        return [(pkg, mod, path) for (pkg, mod, path) in modules if mod in allow]


setup(cmdclass={"build_py": build_py})
