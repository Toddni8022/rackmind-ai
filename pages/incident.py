import streamlit as st
import pandas as pd

from adk.chat import investigate
from services.pdf_service import create_report


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

            st.warning(
                "Please upload a switch log."
            )

            return

        if sensor_file is None:

            st.warning(
                "Please upload a sensor CSV."
            )

            return

        with st.spinner(
            "Investigating infrastructure incident..."
        ):

            log_text = log_file.read().decode("utf-8")

            sensor_df = pd.read_csv(sensor_file)

            report = investigate(
                log_text,
                sensor_df,
            )

        st.success(
            "Executive Incident Report"
        )

        st.markdown(report)

        filename = create_report(report)

        with open(filename, "rb") as pdf:

            st.download_button(
                label="📄 Download Executive Report",
                data=pdf,
                file_name=filename,
                mime="application/pdf",
            )

    st.divider()

    st.caption(
        "RackMind AI v1.0 | Google ADK | Gemini | ChromaDB"
    )