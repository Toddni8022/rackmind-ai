import streamlit as st
from services.interface import apply_design, brand_header
from services.auth import require_login, logout, current_role
from services.audit import record

from pages.dashboard import show_dashboard
from pages.runbook import show_runbook
from pages.logs import show_logs
from pages.sensors import show_sensors
from pages.incident import show_incident

st.set_page_config(
    page_title="RackMind AI",
    page_icon="🖥️",
    layout="wide",
)

apply_design()
brand_header()
user = require_login()
if user is None:
    st.stop()
if user != "demo":
    st.caption(f"Signed in as **{user}** · role: **{current_role()}**")
logout()
record("session_view", user, {"page": "main"})

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "Overview",
        "Runbook library",
        "Network signals",
        "Sensor analysis",
        "Incident desk",
    ]
)

with tab1:
    show_dashboard()

with tab2:
    show_runbook()

with tab3:
    show_logs()

with tab4:
    show_sensors()

with tab5:
    show_incident()
