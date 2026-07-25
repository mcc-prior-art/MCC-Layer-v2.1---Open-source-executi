# Normative v1.0 Conformance Remediation Waves

Each remediation wave selects a bounded subset of `GAP`/`PARTIAL`
requirements from `conformance/normative-v1.0/requirements.json`, implements
the minimal corrections needed to move them to `CONFORMANT`, and records the
result here as `wave-<n>-<name>-scope-manifest.{json,md}`.

A wave manifest is required even when the wave's proposed scope turns out to
have no eligible requirements — see `wave-1-execution-boundary-scope-manifest.md`
for why Wave 1 could not select anything, and why fabricating a selection
would have misrepresented conformance rather than establishing it.

## Waves

| Wave | Name | Selected requirements | Outcome |
|---|---|---|---|
| 1 | Execution Boundary | 0 | Blocked — target vocabulary is explicitly out of scope for all four Normative v1.0 specifications; see manifest. |
