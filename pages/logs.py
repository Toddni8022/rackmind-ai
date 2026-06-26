import streamlit as st

from agents.coordinator import coordinate_log_workflow
from services.assessment_service import (
    build_recommendations,
    score_log_summary,
)
from tools.log_reader import analyze_log


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

    if st.button("Analyze Log", type="primary", width="stretch"):

        with st.spinner("Reading infrastructure log..."):
            summary = analyze_log(logfile)

        st.session_state["rackmind_log_summary"] = summary
        st.session_state["rackmind_log_source"] = logfile.name

        scorecard = score_log_summary(summary)
        recommendations = build_recommendations(log_summary=summary)

        st.divider()
        st.subheader("Infrastructure Health")

        c1, c2, c3, c4, c5 = st.columns(5)

        c1.metric("Score", f"{scorecard['score']}/100")
        c2.metric("Status", scorecard["status"])
        c3.metric("Events", summary["total_events"])
        c4.metric("Errors", summary["errors"])
        c5.metric("CRC", summary["crc_errors"])

        st.progress(scorecard["score"] / 100)

        c6, c7, c8 = st.columns(3)
        c6.metric("Warnings", summary["warnings"])
        c7.metric("Interface Resets", summary["interface_resets"])
        c8.metric("Max Temperature", f'{summary["max_temperature"]}°F')

        st.divider()
        st.subheader("Recommended Actions")

        for item in recommendations:
            st.markdown(f"- {item}")

        st.divider()
        st.subheader("📅 Incident Timeline")

        if summary["timeline"]:
            for event in summary["timeline"]:
                st.markdown(f"- {event}")
        else:
            st.success("No critical timeline events were detected.")

        st.divider()
        st.subheader("🤖 Executive Incident Report")

        with st.spinner("Coordinator Agent orchestrating AI agents..."):
            report = coordinate_log_workflow(summary)

        st.markdown(report)
