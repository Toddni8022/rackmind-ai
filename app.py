import streamlit as st

from agents.coordinator import analyze_issue
from agents.runbook_agent import search_runbook
from tools.pdf_search import extract_pdf_text

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
        "📄 Upload Runbook (PDF)",
        type=["pdf"],
        accept_multiple_files=False
    )

    logfile = st.file_uploader(
        "📜 Upload Log",
        type=["log", "txt"],
        accept_multiple_files=False
    )

    sensor = st.file_uploader(
        "📊 Upload Sensor CSV",
        type=["csv"],
        accept_multiple_files=False
    )

    st.divider()

    st.subheader("Agent Status")

    st.success("🟢 Coordinator Agent Online")

    if runbook:
        st.success("🟢 Runbook Agent Ready")
    else:
        st.info("⚪ Runbook Agent")

    st.info("⚪ Log Agent")

    st.info("⚪ Sensor Agent")

    st.info("⚪ Report Agent")

st.header("Ask RackMind")

question = st.text_area(
    "Describe the infrastructure issue",
    placeholder="Example: Rack 22 is overheating and showing CRC errors..."
)

if st.button("Analyze"):

    if question.strip() == "":
        st.warning("Please enter an infrastructure issue.")

    else:

        if runbook:

            with st.spinner("Runbook Agent Reading Documentation..."):

                runbook_text = extract_pdf_text(runbook)

                answer = search_runbook(
                    question,
                    runbook_text
                )

        else:

            with st.spinner("Coordinator Agent Thinking..."):

                answer = analyze_issue(question)

        st.markdown("---")

        st.markdown(answer)