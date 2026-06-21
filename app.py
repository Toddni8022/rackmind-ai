import streamlit as st

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

    st.subheader("Agents")

    st.success("🟢 Coordinator")

    st.info("⚪ Runbook")

    st.info("⚪ Log")

    st.info("⚪ Sensor")

st.header("Ask RackMind")

question = st.text_area(
    "Describe the infrastructure issue",
    placeholder="Rack 22 is overheating and showing CRC errors..."
)

if st.button("Analyze"):

    if question.strip() == "":
        st.warning("Enter an infrastructure problem.")
    else:

        st.subheader("Root Cause")

        st.write(
            "Likely cooling degradation causing intermittent network failures."
        )

        st.subheader("Recommended Actions")

        st.markdown("""
1. Verify rack airflow

2. Inspect fan status

3. Check SFP modules

4. Review switch logs

5. Monitor for 15 minutes
""")

        st.subheader("Priority")

        st.error("HIGH")

        st.subheader("Confidence")

        st.progress(91)
        st.write("91%")