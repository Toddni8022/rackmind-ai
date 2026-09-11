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
    return bool(_users())


def require_login():
    """Render login when configured; return the current user or None."""
    if not auth_enabled():
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


def logout():
    if st.session_state.get("rackmind_user"):
        if st.button("Sign out", key="sign_out"):
            st.session_state.pop("rackmind_user", None)
            st.session_state.pop("rackmind_role", None)
            st.rerun()
