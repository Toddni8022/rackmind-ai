import pandas as pd
import streamlit as st

from adk.chat import investigate
from services.assessment_service import (
    build_alerts,
    build_recommendations,
    score_log_summary,
    score_sensor_summary,
)
from services.app_state import dataframe_to_records, replace_runtime_state
from services.log_parser import parse_log
from services.pdf_service import create_report
from services.sensor_parser import parse_sensor_data


def show_incident():

    st.header("🚨 Incident Commander")
    st.caption("Autonomous AI Infrastructure Investigation")

    log_file = st.file_uploader(
        "Upload switch.log",
        type=["log", "txt"],
        key="incident_log",
    )

    sensor_file = st.file_uploader(
        "Upload rack22.csv",
        type=["csv"],
        key="incident_sensor",
    )

    if st.button(
        "Analyze Incident",
        type="primary",
        width="stretch",
    ):

        if log_file is None:
            st.warning("Please upload a switch log.")
            return

        if sensor_file is None:
            st.warning("Please upload a sensor CSV.")
            return

        try:
            log_text = log_file.getvalue().decode("utf-8")
            sensor_df = pd.read_csv(sensor_file)
        except Exception as ex:
            st.error(f"Unable to read uploaded files: {ex}")
            return

        sensor_df.columns = sensor_df.columns.str.strip().str.lower()

        if sensor_df.empty:
            st.warning("The uploaded sensor CSV is empty.")
            return

        log_summary = parse_log(log_text)
        sensor_summary = parse_sensor_data(sensor_df)
        st.session_state["rackmind_log_summary"] = log_summary
        st.session_state["rackmind_log_source"] = log_file.name
        st.session_state["rackmind_sensor_df"] = sensor_df
        st.session_state["rackmind_sensor_summary"] = sensor_summary
        st.session_state["rackmind_sensor_source"] = sensor_file.name
        replace_runtime_state(
            log_summary=log_summary,
            log_source=log_file.name,
            sensor_records=dataframe_to_records(sensor_df),
            sensor_summary=sensor_summary,
            sensor_source=sensor_file.name,
        )

        log_score = score_log_summary(log_summary)
        sensor_score = score_sensor_summary(sensor_summary)
        alerts = build_alerts(
            log_summary=log_summary,
            sensor_summary=sensor_summary,
        )
        recommendations = build_recommendations(
            log_summary=log_summary,
            sensor_summary=sensor_summary,
        )

        st.divider()
        st.subheader("Incident Triage")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Log Score", f"{log_score['score']}/100")
        c2.metric("Sensor Score", f"{sensor_score['score']}/100")
        c3.metric("Severity", min(log_score, sensor_score, key=lambda x: x["score"])["severity"])
        c4.metric("Samples", sensor_summary["samples"])

        if alerts:
            for alert in alerts:
                st.warning(alert)
        else:
            st.success("No active incident signals were detected.")

        st.subheader("Immediate Actions")
        for item in recommendations:
            st.markdown(f"- {item}")

        with st.spinner("Investigating infrastructure incident..."):
            report = investigate(
                log_text,
                sensor_df,
            )

        st.divider()
        st.success("Executive Incident Report")
        st.markdown(report)

        filename = create_report(report)

        with open(filename, "rb") as pdf:
            st.download_button(
                label="📄 Download Executive Report",
                data=pdf,
                file_name=filename,
                mime="application/pdf",
                width="stretch",
            )

    st.divider()
    st.caption("RackMind AI v1.0 | Google ADK | Gemini | ChromaDB")
