import hashlib
import json

from healthcheck import check
from services import auth


def test_readiness_check_and_configured_users(monkeypatch):
    digest = hashlib.sha256(b"secret").hexdigest()
    monkeypatch.setenv("RACKMIND_USERS", json.dumps({"alice": {"password_sha256": digest, "role": "admin"}}))
    assert check()["status"] == "ok"
    assert auth.auth_enabled()
    assert auth._users()["alice"]["role"] == "admin"
