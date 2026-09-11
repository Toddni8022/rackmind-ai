"""Small, deployment-friendly session authentication for the Streamlit UI."""
import hashlib
import hmac
import json
import os
import streamlit as st


def _users():
    raw = os.getenv("RACKMIND_USERS", "")
    if not raw:
        try:
            raw = st.secrets.get("RACKMIND_USERS", "")
        except Exception:
            raw = ""
    try:
        parsed = json.loads(raw) if raw else {}
        return parsed if isinstance(parsed, dict) else {}
    except json.JSONDecodeError:
        return {}


def auth_enabled():
    return bool(_users()) or bool(os.getenv("RACKMIND_OIDC_PROVIDER"))


def require_login():
    """Render login when configured; return the current user or None."""
    oidc_provider = os.getenv("RACKMIND_OIDC_PROVIDER", "").strip()
    if oidc_provider and hasattr(st, "login") and hasattr(st, "user"):
        if getattr(st.user, "is_logged_in", False):
            username = getattr(st.user, "email", None) or getattr(st.user, "name", "oidc-user")
            st.session_state.setdefault("rackmind_user", username)
            st.session_state.setdefault("rackmind_role", role_for(username))
            return username
        st.info("Sign in with your organization account to continue.")
        if st.button("Sign in with SSO", type="primary"):
            st.login(oidc_provider)
        return None
    if not _users():
        return "demo"
    if st.session_state.get("rackmind_user"):
        return st.session_state["rackmind_user"]
    st.subheader("Sign in to RackMind")
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")
    if st.button("Sign in", type="primary"):
        expected = _users().get(username)
        expected_hash = expected.get("password_sha256") if isinstance(expected, dict) else expected
        role = expected.get("role", "operator") if isinstance(expected, dict) else "operator"
        if expected_hash and hmac.compare_digest(hashlib.sha256(password.encode()).hexdigest(), str(expected_hash)):
            st.session_state["rackmind_user"] = username
            st.session_state["rackmind_role"] = role
            st.rerun()
        st.error("Invalid username or password.")
    st.caption("Authentication is configured by the deployment owner.")
    return None


def current_role():
    return st.session_state.get("rackmind_role", "operator")


def role_for(username):
    entry = _users().get(username, {})
    return entry.get("role", "operator") if isinstance(entry, dict) else "operator"


def can(permission):
    permissions = {
        "viewer": {"view"},
        "operator": {"view", "analyze", "upload"},
        "admin": {"view", "analyze", "upload", "manage_users", "configure_integrations"},
    }
    return permission in permissions.get(current_role(), set())


def logout():
    if st.session_state.get("rackmind_user"):
        if st.button("Sign out", key="sign_out"):
            st.session_state.pop("rackmind_user", None)
            st.session_state.pop("rackmind_role", None)
            st.rerun()
