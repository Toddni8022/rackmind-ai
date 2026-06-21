import streamlit as st
from agents.coordinator import analyze_issue

st.set_page_config(
    page_title="RackMind AI",
    page_icon="🖥️",
    layout="wide"
)

st.title("🖥️ RackMind AI")
st.caption("Autonomous Data Center Operations Copilot")

with st.sidebar:

    st.header("Infrastructure Files")

    runbook = st.file_uploader(
        "📄 Upload Runbook",
        type=["pdf"]
    )

    logfile = st.file_uploader(
        "📜 Upload Log",
        type=["log", "txt"]
    )

    sensor = st.file_uploader(
        "📊 Upload Sensor Data",
        type=["csv"]
    )

    st.divider()

    st.subheader("Agent Status")

    st.success("🟢 Coordinator Agent Online")
    st.info("⚪ Runbook Agent")
    st.info("⚪ Log Agent")
    st.info("⚪ Sensor Agent")
    st.info("⚪ Report Agent")

st.header("Ask RackMind")

question = st.text_area(
    "Describe the infrastructure issue",
    placeholder="Rack 22 is overheating and showing CRC errors..."
)

if st.button("Analyze"):

    if question.strip() == "":
        st.warning("Please enter an infrastructure issue.")

    else:

        with st.spinner("Coordinator Agent Thinking..."):

            answer = analyze_issue(question)

        st.markdown(answer)