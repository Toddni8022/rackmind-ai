"""
Tests for authentication and role-based access.
"""

import pytest

from services.auth_service import (
    auth_enabled,
    authenticate,
    change_password,
    create_user,
    delete_user,
    ensure_default_admin,
    has_role,
    is_default_password,
    list_users,
    set_role,
)


class TestAccounts:

    def test_create_and_authenticate(self):
        create_user("alice", "s3cret", "operator")

        user = authenticate("alice", "s3cret")

        assert user == {"username": "alice", "role": "operator"}

    def test_wrong_password_rejected(self):
        create_user("bob", "correct", "operator")

        assert authenticate("bob", "wrong") is None

    def test_unknown_user_rejected(self):
        assert authenticate("ghost", "anything") is None

    def test_username_is_case_insensitive(self):
        create_user("Carol", "pass1234", "manager")

        assert authenticate("carol", "pass1234") is not None
        assert authenticate("CAROL", "pass1234") is not None

    def test_duplicate_username_rejected(self):
        create_user("dave", "pass1234")

        with pytest.raises(ValueError, match="already exists"):
            create_user("dave", "other123")

    def test_invalid_role_rejected(self):
        with pytest.raises(ValueError, match="Role must be one of"):
            create_user("eve", "pass1234", "superuser")

    def test_short_password_rejected(self):
        with pytest.raises(ValueError, match="at least 4"):
            create_user("frank", "abc")

    def test_passwords_are_hashed_not_stored(self):
        create_user("grace", "topsecret")

        from services.db import get_connection

        with get_connection() as connection:
            row = connection.execute(
                "SELECT * FROM users WHERE username = 'grace'"
            ).fetchone()

        assert row["password_hash"] != "topsecret"
        assert "topsecret" not in row["password_hash"]

    def test_change_password(self):
        create_user("henry", "oldpass")

        change_password("henry", "newpass")

        assert authenticate("henry", "oldpass") is None
        assert authenticate("henry", "newpass") is not None

    def test_set_role(self):
        create_user("iris", "pass1234", "operator")

        set_role("iris", "admin")

        assert authenticate("iris", "pass1234")["role"] == "admin"

    def test_delete_user(self):
        create_user("jack", "pass1234")
        create_user("boss", "pass1234", "admin")

        assert delete_user("jack") is True
        assert authenticate("jack", "pass1234") is None

    def test_cannot_delete_last_admin(self):
        create_user("root", "pass1234", "admin")

        with pytest.raises(ValueError, match="last admin"):
            delete_user("root")


class TestBootstrap:

    def test_default_admin_created_once(self):
        assert ensure_default_admin() is True
        assert ensure_default_admin() is False

        users = list_users()

        assert len(users) == 1
        assert users[0]["username"] == "admin"
        assert users[0]["role"] == "admin"

    def test_default_password_detection(self):
        ensure_default_admin()

        assert is_default_password("admin") is True

        change_password("admin", "rotated-now")

        assert is_default_password("admin") is False


class TestRoles:

    def test_role_hierarchy(self):
        operator = {"username": "o", "role": "operator"}
        manager = {"username": "m", "role": "manager"}
        admin = {"username": "a", "role": "admin"}

        assert has_role(operator, "operator")
        assert not has_role(operator, "manager")
        assert has_role(manager, "operator")
        assert has_role(manager, "manager")
        assert not has_role(manager, "admin")
        assert has_role(admin, "admin")

    def test_anonymous_has_no_role(self):
        assert not has_role(None, "operator")

    def test_auth_disabled_grants_everything(self, monkeypatch):
        monkeypatch.setenv("RACKMIND_AUTH", "off")

        assert auth_enabled() is False
        assert has_role(None, "admin") is True

    def test_auth_enabled_by_default(self, monkeypatch):
        monkeypatch.delenv("RACKMIND_AUTH", raising=False)

        assert auth_enabled() is True
