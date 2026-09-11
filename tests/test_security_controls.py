import hashlib
import json

from healthcheck import check
from services import auth
from services.integrations import IntegrationError, fetch_json


def test_readiness_check_and_configured_users(monkeypatch):
    digest = hashlib.sha256(b"secret").hexdigest()
    monkeypatch.setenv("RACKMIND_USERS", json.dumps({"alice": {"password_sha256": digest, "role": "admin"}}))
    assert check()["status"] == "ok"
    assert auth.auth_enabled()
    assert auth._users()["alice"]["role"] == "admin"


def test_permissions_and_missing_live_source(monkeypatch):
    monkeypatch.delenv("RACKMIND_TELEMETRY_URL", raising=False)
    digest = hashlib.sha256(b"secret").hexdigest()
    monkeypatch.setenv("RACKMIND_USERS", json.dumps({"alice": {"password_sha256": digest, "role": "admin"}}))
    assert auth.role_for("alice") == "admin"
    auth.st.session_state["rackmind_role"] = "viewer"
    assert auth.can("view") and not auth.can("upload")
    try:
        fetch_json()
    except IntegrationError as exc:
        assert "not configured" in str(exc)
    else:
        raise AssertionError("missing telemetry source should fail closed")
