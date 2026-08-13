"""Independent, normative Canonical HTTP Action format (PR #71, Workstream D).

This is a SECOND, independently written implementation of the canonical
action format documented in ``docs/CANONICAL_ACTION_FORMAT.md`` -- written
from that specification, not by importing or copying
``egress_proxy.canonical_action`` (the SUT's own implementation). Its sole
purpose is differential testing: if this implementation and the real,
running actuator agree on the action hash for a large corpus of inputs
(including edge cases and malformed inputs that both must reject the same
way), that is evidence the canonical format is unambiguously specified and
consistently implemented -- not merely "whatever the code happens to do".

It reuses ``mcc_core.signing``'s canonical JSON + SHA-256 primitives for the
final hash (the same low-level primitive every signed/hashed structure in
this repository uses -- not something worth re-implementing a third time),
but reimplements every canonicalization DECISION (field set, normalization,
sorting, rejection rules) independently.
"""

from __future__ import annotations

import base64
import json
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import parse_qsl, urlsplit

from mcc_core.signing import hash_payload, sha256_hex

CANONICAL_ACTION_FORMAT_VERSION = "mcc-canonical-http-action/1"

ACTION_TYPE = "http.request"
ALLOWED_METHODS = frozenset({"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"})
ALLOWED_SCHEMES = frozenset({"http", "https"})
DEFAULT_PORTS = {"http": 80, "https": 443}
DEFAULT_GOVERNED_HEADERS: Tuple[str, ...] = ("content-type", "accept")
HOP_BY_HOP_HEADERS = frozenset({
    "connection", "keep-alive", "proxy-authenticate", "proxy-authorization",
    "te", "trailer", "trailers", "transfer-encoding", "upgrade",
    "host", "content-length", "expect", "proxy-connection",
})
SECRET_BEARING_HEADERS = frozenset({
    "authorization", "proxy-authorization", "cookie",
    "x-api-key", "x-operator-key", "api-key",
})
MAX_BODY_BYTES = 1 * 1024 * 1024


class CanonicalActionError(ValueError):
    """The proposed action does not conform to the canonical format spec."""


def _normalize_url(url: str) -> Tuple[str, str, int, str, List[List[str]]]:
    if not isinstance(url, str) or not url.strip():
        raise CanonicalActionError("url is required")
    parsed = urlsplit(url.strip())
    scheme = parsed.scheme.lower()
    if scheme not in ALLOWED_SCHEMES:
        raise CanonicalActionError(f"scheme {scheme!r} is not in {sorted(ALLOWED_SCHEMES)}")
    if parsed.username or parsed.password or "@" in (parsed.netloc or ""):
        raise CanonicalActionError("embedded credentials in the URL are not permitted")
    host = (parsed.hostname or "").lower()
    if not host:
        raise CanonicalActionError("url has no host")
    try:
        port = parsed.port if parsed.port is not None else DEFAULT_PORTS[scheme]
    except ValueError as exc:
        raise CanonicalActionError(f"invalid port: {exc}") from exc
    if not (0 < port < 65536):
        raise CanonicalActionError(f"port {port} is out of range")
    path = parsed.path or "/"
    query_pairs = sorted([k, v] for k, v in parse_qsl(parsed.query, keep_blank_values=True))
    return scheme, host, port, path, query_pairs


def _canonical_headers(headers: Optional[Dict[str, str]],
                        governed_names: Tuple[str, ...]) -> List[List[str]]:
    headers = headers or {}
    governed = {n.lower() for n in governed_names}
    for name in headers:
        if str(name).lower() in SECRET_BEARING_HEADERS:
            raise CanonicalActionError(f"secret-bearing header {str(name).lower()!r} is not permitted")
    kept = [
        [str(name).lower(), str(value)]
        for name, value in headers.items()
        if str(name).lower() not in HOP_BY_HOP_HEADERS and str(name).lower() in governed
    ]
    return sorted(kept)


def _canonical_body(body: Any) -> Dict[str, Any]:
    if body is None or body == {} or body == "":
        return {"body_kind": "empty"}
    if isinstance(body, dict):
        encoded = json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
        if len(encoded) > MAX_BODY_BYTES:
            raise CanonicalActionError("body exceeds the size limit")
        keys = sorted(str(k) for k in body.keys())
        flat: Dict[str, Any] = {"body_kind": "json", "__body_keys__": keys}
        for k in keys:
            flat[f"body.{k}"] = body[k]
        return flat
    raw = body.encode("utf-8") if isinstance(body, str) else bytes(body)
    if len(raw) > MAX_BODY_BYTES:
        raise CanonicalActionError("body exceeds the size limit")
    return {"body_kind": "raw", "__rawbody_b64__": base64.b64encode(raw).decode("ascii"),
            "__rawbody_sha256__": sha256_hex(raw)}


def build_canonical_action(*, method: str, url: str, headers: Optional[Dict[str, str]] = None,
                            body: Any = None, governed_headers: Tuple[str, ...] = DEFAULT_GOVERNED_HEADERS,
                            credential_ref: Optional[str] = None,
                            client_identity_ref: Optional[str] = None,
                            ca_bundle_ref: Optional[str] = None) -> Dict[str, Any]:
    if not isinstance(method, str) or not method.strip():
        raise CanonicalActionError("method is required")
    normalized_method = method.strip().upper()
    if normalized_method not in ALLOWED_METHODS:
        raise CanonicalActionError(f"method {normalized_method!r} is not in {sorted(ALLOWED_METHODS)}")

    scheme, host, port, path, query = _normalize_url(url)
    action: Dict[str, Any] = {
        "action_type": ACTION_TYPE,
        "method": normalized_method,
        "scheme": scheme,
        "host": host,
        "port": port,
        "path": path,
        "query": query,
        "headers": _canonical_headers(headers, governed_headers),
        "destination_id": f"{host}:{port}",
    }
    if credential_ref:
        action["cred_ref"] = str(credential_ref)
    if client_identity_ref:
        action["client_identity_ref"] = str(client_identity_ref)
    if ca_bundle_ref:
        action["ca_bundle_ref"] = str(ca_bundle_ref)
    action.update(_canonical_body(body))
    return action


def action_hash(action: Dict[str, Any]) -> str:
    return hash_payload(action)
