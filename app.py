import streamlit as st

from pages.dashboard import show_dashboard
from pages.runbook import show_runbook
from pages.logs import show_logs
from pages.sensors import show_sensors

st.set_page_config(
    page_title="RackMind AI",
    page_icon="🖥️",
    layout="wide"
)

st.title("🖥️ RackMind AI")
st.caption("Autonomous Data Center Operations Copilot")

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "🏠 Dashboard",
        "📄 Runbook",
        "📜 Log Agent",
        "📊 Sensor Agent",
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