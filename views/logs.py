import streamlit as st

from agents.coordinator import coordinate_log_workflow
from services.log_parser import build_log_timeline, compute_health_score, parse_log


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

        with st.spinner("Reading infrastructure log..."):

            log_text = logfile.read().decode("utf-8", errors="replace")
            summary = parse_log(log_text)
            timeline = build_log_timeline(log_text)

        st.divider()

        st.subheader("Infrastructure Health")

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("Events", summary["events"])
        c2.metric("Warnings", summary["warnings"])
        c3.metric("Errors", summary["errors"])
        c4.metric("CRC Errors", summary["crc_errors"])

        c5, c6 = st.columns(2)

        c5.metric(
            "Interface Resets",
            summary["resets"],
        )

        c6.metric(
            "Max Temperature",
            f'{summary["max_temp"]}°F',
        )

        score = compute_health_score(summary)

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

        if timeline:
            for event in timeline:
                st.markdown(f"- {event}")
        else:
            st.markdown("No noteworthy events detected.")

        st.divider()

        st.subheader("🤖 Executive Incident Report")

        with st.spinner("Coordinator Agent orchestrating AI agents..."):

            report = coordinate_log_workflow(summary)

        st.markdown(report)
