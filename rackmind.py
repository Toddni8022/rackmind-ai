import streamlit as st

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

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.4rem;
        padding-bottom: 2rem;
    }
    [data-testid="stMetric"] {
        background: rgba(49, 51, 63, 0.08);
        border: 1px solid rgba(128, 128, 128, 0.18);
        border-radius: 8px;
        padding: 0.85rem 1rem;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.82rem;
    }
    div[data-testid="stAlert"] {
        border-radius: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🖥️ RackMind AI")
st.caption("Autonomous Data Center Operations Copilot")

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "🏠 Dashboard",
        "📄 Runbook",
        "📜 Log Agent",
        "📊 Sensor Agent",
        "🚨 Incident Commander",
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
