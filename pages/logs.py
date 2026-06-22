import streamlit as st

from tools.log_reader import analyze_log
from agents.log_agent import analyze_log_summary


def show_logs():

    st.header("📜 Log Analysis")
    st.caption("AI-powered infrastructure incident analysis")

    logfile = st.file_uploader(
        "Upload switch.log",
        type=["log", "txt"],
        accept_multiple_files=False,
    )

    if logfile is None:
        st.info("Upload a switch log to begin analysis.")
        return

    st.success(f"Loaded: {logfile.name}")

    if st.button("Analyze Log", use_container_width=True):

        with st.spinner("Analyzing infrastructure log..."):

            summary = analyze_log(logfile)

        st.divider()

        st.subheader("Infrastructure Health")

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("Events", summary["total_events"])
        c2.metric("Warnings", summary["warnings"])
        c3.metric("Errors", summary["errors"])
        c4.metric("CRC Errors", summary["crc_errors"])

        c5, c6 = st.columns(2)

        c5.metric(
            "Interface Resets",
            summary["interface_resets"],
        )

        c6.metric(
            "Max Temperature",
            f'{summary["max_temperature"]}°F',
        )

        score = 100
        score -= summary["errors"] * 8
        score -= summary["warnings"] * 2
        score -= summary["crc_errors"] * 3

        score = max(score, 0)

        st.divider()

        st.subheader("Network Health")

        st.progress(score / 100)

        if score >= 90:
            st.success(f"Health Score: {score}/100")
        elif score >= 70:
            st.warning(f"Health Score: {score}/100")
        else:
            st.error(f"Health Score: {score}/100")

        st.divider()

        st.subheader("📅 Incident Timeline")

        for event in summary["timeline"]:
            st.markdown(f"- {event}")

        st.divider()

        st.subheader("🤖 Executive Incident Report")

        report = analyze_log_summary(summary)

        st.markdown(report)