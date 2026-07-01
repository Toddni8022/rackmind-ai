import streamlit as st

from services.auth_service import (
    auth_enabled,
    authenticate,
    ensure_default_admin,
    has_role,
    is_default_password,
)

st.set_page_config(
    page_title="RackMind AI",
    page_icon="🖥️",
    layout="wide",
)


def _login_screen():

    st.title("🖥️ RackMind AI")
    st.caption("Autonomous Data Center Operations Copilot")

    bootstrapped = ensure_default_admin()

    _, center, _ = st.columns([1, 2, 1])

    with center:

        st.subheader("🔐 Sign In")

        if bootstrapped:
            st.info(
                "First run: a default **admin / rackmind** account was "
                "created. Sign in and change the password immediately."
            )

        with st.form("login"):

            username = st.text_input("Username")
            password = st.text_input("Password", type="password")

            submitted = st.form_submit_button(
                "Sign In",
                type="primary",
                use_container_width=True,
            )

        if submitted:

            user = authenticate(username, password)

            if user:
                st.session_state["user"] = user
                st.rerun()
            else:
                st.error("Invalid username or password.")

        st.caption(
            "Roles: operator (analysis), manager (+ incident archive "
            "management), admin (+ user administration)."
        )


def _main_app(user):

    from pages.admin import show_admin
    from pages.dashboard import show_dashboard
    from pages.history import show_history
    from pages.incident import show_incident
    from pages.logs import show_logs
    from pages.runbook import show_runbook
    from pages.sensors import show_sensors
    from pages.telemetry import show_telemetry
    from pages.trends import show_trends

    st.title("🖥️ RackMind AI")
    st.caption("Autonomous Data Center Operations Copilot")

    if user:

        with st.sidebar:

            st.markdown(
                f"👤 **{user['username']}** — `{user['role']}`"
            )

            if user["username"] == "admin" and is_default_password("admin"):
                st.warning(
                    "The default admin password is still active. "
                    "Change it in the Admin tab."
                )

            if st.button("Sign Out", use_container_width=True):
                st.session_state.pop("user", None)
                st.rerun()

    tabs = [
        ("🏠 Dashboard", show_dashboard, None),
        ("📄 Runbook", show_runbook, None),
        ("📜 Log Agent", show_logs, None),
        ("📊 Sensor Agent", show_sensors, None),
        ("📡 Live Telemetry", show_telemetry, "user"),
        ("📈 Trends", show_trends, "user"),
        ("🚨 Incident Commander", show_incident, None),
        ("🗂️ History", show_history, "user"),
    ]

    if has_role(user, "admin"):
        tabs.append(("🔐 Admin", show_admin, "user"))

    tab_objects = st.tabs([label for label, _, _ in tabs])

    for tab, (label, render, mode) in zip(tab_objects, tabs):

        with tab:

            if mode == "user":
                render(user=user)
            else:
                render()


user = st.session_state.get("user")

if auth_enabled() and user is None:
    _login_screen()
else:
    _main_app(user)
