"""Optional mutual TLS via governed references. mTLS preserves all PR #26
server-side protections (verify, hostname, SNI, pinning, peer-IP) and fails
closed on missing/mismatched/invalid material. Deterministic, offline."""

import asyncio
import glob
import ssl
import tempfile
from pathlib import Path

import httpx
import pytest

from egress_proxy.canonical_action import build_canonical_action
from egress_proxy.credentials import (
    CLIENT_IDENTITY, CredentialBinding, CredentialEntry, CredentialError,
    InMemoryCredentialProvider,
)
from egress_proxy.executor import HTTPEgressExecutor
from egress_proxy.ssrf import DestinationPolicy
from tests._tls_harness import (
    host_resolver, make_ca, make_leaf, serve_mtls, write_ca_bundle, write_cert_and_key,
)

HOST = "egress.test"
AUTH = {"decision": "ALLOW", "action": "http.request", "actor_id": "agent/egress"}
run = asyncio.run


def _enc(cert):
    from cryptography.hazmat.primitives import serialization
    return cert.public_bytes(serialization.Encoding.PEM)


def _enc_key(key):
    from cryptography.hazmat.primitives import serialization
    return key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
                             serialization.NoEncryption())


def _setup(tmp_path: Path):
    # One internal CA signs both the server and the client identity (a common,
    # valid mTLS model): the executor trusts the CA for the server, and the server
    # requires a client cert from the same CA.
    ca_key, ca_cert = make_ca()
    s_key, s_cert = make_leaf(ca_key, ca_cert, HOST)
    server_cert, server_key = write_cert_and_key(tmp_path, s_cert, s_key, prefix="server")
    ca_file = write_ca_bundle(tmp_path, ca_cert)
    c_key, c_cert = make_leaf(ca_key, ca_cert, "client")
    port = serve_mtls(server_cert, server_key, ca_file)
    return {"port": port, "server_ca_file": ca_file,
            "client_cert_pem": _enc(c_cert), "client_key_pem": _enc_key(c_key)}


def _client_entry(cert_pem, key_pem):
    return CredentialEntry(
        binding=CredentialBinding(allowed_hosts=(HOST,), allowed_methods=("GET",),
                                  allowed_actions=("http.request",), allowed_envs=("dev",)),
        type=CLIENT_IDENTITY, loader=lambda: (cert_pem, key_pem))


def _executor(ctx, *, provider=None, ca_file=None):
    return HTTPEgressExecutor(
        policy=DestinationPolicy(allow_loopback=True, allowed_hosts=frozenset({HOST})),
        resolver=host_resolver({HOST: "127.0.0.1"}), require_https=True,
        tls_ca_file=ca_file or ctx["server_ca_file"], credential_provider=provider, env_name="dev")


def _act(port, *, client_identity_ref=None, **refs):
    return build_canonical_action(method="GET", url=f"https://{HOST}:{port}/x", headers={},
                                  client_identity_ref=client_identity_ref, **refs)


def _temp_mtls_files():
    return set(glob.glob(str(Path(tempfile.gettempdir()) / "mcc-mtls-*")))


def test_valid_mtls_succeeds_and_preserves_pinning(tmp_path):
    ctx = _setup(tmp_path)
    provider = InMemoryCredentialProvider(
        {"cid": _client_entry(ctx["client_cert_pem"], ctx["client_key_pem"])})
    ex = _executor(ctx, provider=provider)
    before = _temp_mtls_files()
    r = run(ex.execute("http.request", _act(ctx["port"], client_identity_ref="cid"),
                       authorization=AUTH))
    assert r["executed"] and r["tls_validated"] is True
    assert r["peer_ip"] == "127.0.0.1" and r["mtls_requested"] and r["client_identity_loaded"]
    assert _temp_mtls_files() == before  # temp material cleaned up after success


def test_missing_client_cert_fails_closed(tmp_path):
    ctx = _setup(tmp_path)
    ex = _executor(ctx, provider=InMemoryCredentialProvider({}))  # no client identity
    # The server requires a client cert. Under TLS 1.2 the rejection surfaces at
    # handshake time wrapped as httpx.HTTPError; under TLS 1.3 client auth is
    # deferred, so the server's "certificate required" alert arrives during the
    # response read as a bare ssl.SSLError. Both prove the same fail-closed
    # outcome — the connection is rejected and nothing executes.
    with pytest.raises((httpx.HTTPError, ssl.SSLError)):
        run(ex.execute("http.request", _act(ctx["port"]), authorization=AUTH))
    assert ex.count() == 0


def test_mismatched_cert_and_key_fails_closed(tmp_path):
    ctx = _setup(tmp_path)
    # Key from a different identity than the cert.
    _, other_key = make_leaf(*make_ca(), "client")
    bad = CredentialEntry(
        binding=CredentialBinding(allowed_hosts=(HOST,), allowed_methods=("GET",),
                                  allowed_actions=("http.request",), allowed_envs=("dev",)),
        type=CLIENT_IDENTITY, loader=lambda: (ctx["client_cert_pem"], _enc_key(other_key)))
    ex = _executor(ctx, provider=InMemoryCredentialProvider({"cid": bad}))
    before = _temp_mtls_files()
    with pytest.raises(CredentialError):
        run(ex.execute("http.request", _act(ctx["port"], client_identity_ref="cid"),
                       authorization=AUTH))
    assert ex.count() == 0
    assert _temp_mtls_files() == before  # cleaned up after failure too


def test_invalid_ca_bundle_fails_closed(tmp_path):
    ctx = _setup(tmp_path)
    from egress_proxy.credentials import CA_BUNDLE
    provider = InMemoryCredentialProvider({
        "cid": _client_entry(ctx["client_cert_pem"], ctx["client_key_pem"]),
        "ca": CredentialEntry(
            binding=CredentialBinding(allowed_hosts=(HOST,), allowed_methods=("GET",),
                                      allowed_actions=("http.request",), allowed_envs=("dev",)),
            type=CA_BUNDLE, loader=lambda: b"-----BEGIN CERTIFICATE-----\nnotvalid\n-----END CERTIFICATE-----\n")})
    ex = _executor(ctx, provider=provider)
    with pytest.raises(CredentialError):
        run(ex.execute("http.request", _act(ctx["port"], client_identity_ref="cid",
                                            ca_bundle_ref="ca"), authorization=AUTH))
    assert ex.count() == 0


def test_mtls_does_not_bypass_server_trust(tmp_path):
    ctx = _setup(tmp_path)
    provider = InMemoryCredentialProvider(
        {"cid": _client_entry(ctx["client_cert_pem"], ctx["client_key_pem"])})
    # Executor trusts the WRONG CA for the server -> still fails (mTLS doesn't relax it).
    _, wrong_ca = make_ca()
    wrong_ca_file = write_ca_bundle(tmp_path, wrong_ca)
    ex = _executor(ctx, provider=provider, ca_file=wrong_ca_file)
    with pytest.raises(httpx.HTTPError):
        run(ex.execute("http.request", _act(ctx["port"], client_identity_ref="cid"),
                       authorization=AUTH))
    assert ex.count() == 0


def test_mtls_still_enforces_ssrf(tmp_path):
    ctx = _setup(tmp_path)
    provider = InMemoryCredentialProvider(
        {"cid": _client_entry(ctx["client_cert_pem"], ctx["client_key_pem"])})
    # A loopback-denying policy still blocks even with a valid client identity.
    ex = HTTPEgressExecutor(
        policy=DestinationPolicy(allowed_hosts=frozenset({HOST})),  # loopback NOT allowed
        resolver=host_resolver({HOST: "127.0.0.1"}), require_https=True,
        tls_ca_file=ctx["server_ca_file"], credential_provider=provider, env_name="dev")
    from egress_proxy.ssrf import SSRFError
    with pytest.raises(SSRFError):
        run(ex.execute("http.request", _act(ctx["port"], client_identity_ref="cid"),
                       authorization=AUTH))
    assert ex.count() == 0
