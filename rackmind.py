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
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    :root {
        --rackmind-cyan: #22d3ee;
        --rackmind-blue: #3b82f6;
        --rackmind-violet: #8b5cf6;
        --rackmind-pink: #ec4899;
        --rackmind-amber: #f59e0b;
        --rackmind-green: #10b981;
        --rackmind-surface: rgba(15, 23, 42, 0.78);
        --rackmind-border: rgba(148, 163, 184, 0.22);
    }
    header,
    #MainMenu,
    footer,
    [data-testid="stSidebar"],
    [data-testid="stSidebarNav"],
    [data-testid="collapsedControl"],
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    [data-testid="stStatusWidget"],
    .stDeployButton {
        display: none !important;
    }
    .stApp {
        background:
            radial-gradient(circle at 12% 8%, rgba(34, 211, 238, 0.18), transparent 30%),
            radial-gradient(circle at 80% 4%, rgba(236, 72, 153, 0.16), transparent 24%),
            radial-gradient(circle at 55% 42%, rgba(139, 92, 246, 0.12), transparent 28%),
            linear-gradient(135deg, #07111f 0%, #0b1020 48%, #111827 100%);
        color: #f8fafc;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1480px;
    }
    h1 {
        background: linear-gradient(90deg, #ffffff 0%, var(--rackmind-cyan) 42%, var(--rackmind-pink) 100%);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
        font-weight: 800;
    }
    h2, h3 {
        color: #f8fafc;
    }
    p, li, .stMarkdown {
        color: #dbeafe;
    }
    [data-testid="stMetric"] {
        background:
            linear-gradient(145deg, rgba(15, 23, 42, 0.92), rgba(30, 41, 59, 0.78)),
            linear-gradient(90deg, rgba(34, 211, 238, 0.22), rgba(236, 72, 153, 0.16));
        border: 1px solid var(--rackmind-border);
        border-radius: 8px;
        padding: 0.95rem 1rem;
        box-shadow: 0 18px 38px rgba(2, 8, 23, 0.26);
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.82rem;
        color: #bfdbfe;
    }
    [data-testid="stMetricValue"] {
        color: #ffffff;
        text-shadow: 0 0 22px rgba(34, 211, 238, 0.20);
    }
    [data-testid="stTabs"] button {
        color: #e0f2fe;
    }
    [data-testid="stTabs"] button[aria-selected="true"] {
        color: #22d3ee;
    }
    [data-testid="stTabs"] [data-baseweb="tab-highlight"] {
        background: linear-gradient(90deg, var(--rackmind-cyan), var(--rackmind-pink), var(--rackmind-amber));
        height: 3px;
    }
    div[data-testid="stAlert"] {
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.12);
    }
    div[data-testid="stProgress"] > div > div > div {
        background: linear-gradient(90deg, var(--rackmind-cyan), var(--rackmind-blue), var(--rackmind-violet), var(--rackmind-pink));
    }
    hr {
        border-color: rgba(148, 163, 184, 0.22);
    }
    section.main > div {
        padding-left: 1rem;
        padding-right: 1rem;
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
