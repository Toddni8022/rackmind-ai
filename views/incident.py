import pandas as pd
import streamlit as st

from adk.chat import investigate
from services.pdf_service import create_report, report_filename
from services.upload_guard import exceeds_upload_limit, upload_limit_message


def show_incident():

    st.header("🚨 Incident Commander")

    st.caption(
        "Autonomous AI Infrastructure Investigation"
    )

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
    ):

        if log_file is None:
            st.warning("Please upload a switch log.")
            return

        if sensor_file is None:
            st.warning("Please upload a sensor CSV.")
            return

        if exceeds_upload_limit(log_file):
            st.error(upload_limit_message(log_file))
            return

        if exceeds_upload_limit(sensor_file):
            st.error(upload_limit_message(sensor_file))
            return

        log_text = log_file.read().decode("utf-8", errors="replace")

        try:
            sensor_df = pd.read_csv(sensor_file)
        except Exception as ex:
            st.error(f"Unable to read sensor CSV: {ex}")
            return

        if sensor_df.empty:
            st.warning("The uploaded sensor CSV does not contain any rows.")
            return

        with st.spinner(
            "Investigating infrastructure incident..."
        ):

            report = investigate(
                log_text,
                sensor_df,
            )

        st.success(
            "Executive Incident Report"
        )

        st.markdown(report)

        st.download_button(
            label="📄 Download Executive Report",
            data=create_report(report),
            file_name=report_filename(),
            mime="application/pdf",
        )

    st.divider()

    st.caption(
        "RackMind AI | Google ADK | Gemini | OpenAI"
    )
