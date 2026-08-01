import streamlit as st

from views.dashboard import show_dashboard
from views.incident import show_incident
from views.logs import show_logs
from views.runbook import show_runbook
from views.sensors import show_sensors
from views.topology import show_topology

st.set_page_config(
    page_title="RackMind AI",
    page_icon="🖥️",
    layout="wide",
)

st.title("🖥️ RackMind AI")
st.caption("Autonomous Data Center Operations Copilot")

tabs = st.tabs(
    [
        "🏠 Dashboard",
        "📄 Runbook",
        "📜 Log Agent",
        "📊 Sensor Agent",
        "🚨 Incident Commander",
        "🗺️ Topology",
    ]
)

views = (
    show_dashboard,
    show_runbook,
    show_logs,
    show_sensors,
    show_incident,
    show_topology,
)

for tab, view in zip(tabs, views):
    with tab:
        view()
