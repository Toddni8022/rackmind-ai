import streamlit as st

from tools.log_reader import analyze_log
from agents.log_agent import analyze_log_summary


def show_logs():

    st.header("📜 Log Analysis")

    st.caption(
        "AI-powered infrastructure incident analysis."
    )

    logfile = st.file_uploader(
        "Upload switch.log",
        type=["log", "txt"],
    )

    if logfile is None:

        st.info("Upload a switch log to begin.")

        return

    if st.button("Analyze Log", use_container_width=True):

        summary = analyze_log(logfile)

        st.subheader("Infrastructure Metrics")

        c1, c2, c3 = st.columns(3)

        c1.metric("Events", summary["total_events"])
        c1.metric("Warnings", summary["warnings"])

        c2.metric("Errors", summary["errors"])
        c2.metric("CRC Errors", summary["crc_errors"])

        c3.metric("Resets", summary["interface_resets"])
        c3.metric("Max Temp", f'{summary["max_temperature"]}°F')

        st.divider()

        st.subheader("📅 Incident Timeline")

        for item in summary["timeline"]:

            st.write("•", item)

        st.divider()

        st.subheader("🤖 AI Incident Report")

        report = analyze_log_summary(summary)

        st.markdown(report)