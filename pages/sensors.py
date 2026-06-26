import pandas as pd
import streamlit as st

from agents.coordinator import coordinate_sensor_workflow
from services.assessment_service import (
    build_recommendations,
    score_sensor_summary,
)
from services.sensor_parser import parse_sensor_data


def show_sensors():

    st.header("📊 Sensor Analytics")
    st.caption("AI-powered infrastructure monitoring")

    sensor_file = st.file_uploader(
        "Upload Sensor CSV",
        type=["csv"],
        accept_multiple_files=False,
    )

    if sensor_file is None:
        st.info("Upload a sensor CSV to begin analysis.")
        return

    try:
        df = pd.read_csv(sensor_file)
    except Exception as ex:
        st.error(f"Unable to read CSV: {ex}")
        return

    df.columns = df.columns.str.strip().str.lower()

    if df.empty:
        st.warning("The uploaded CSV is empty.")
        return

    numeric_columns = df.select_dtypes(include="number").columns.tolist()

    if not numeric_columns:
        st.warning("No numeric telemetry columns were found.")
        return

    summary = parse_sensor_data(df)
    scorecard = score_sensor_summary(summary)
    recommendations = build_recommendations(sensor_summary=summary)

    st.subheader("Sensor Data")
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )

    st.divider()
    st.subheader("Infrastructure Health")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Score", f"{scorecard['score']}/100")
    c2.metric("Status", scorecard["status"])
    c3.metric("Max Temp", f"{summary['max_temp']:.1f}°F")
    c4.metric("Peak Power", f"{summary['peak_power']:.2f} kW")

    st.progress(scorecard["score"] / 100)

    st.divider()
    st.subheader("Charts")

    selected_columns = st.multiselect(
        "Metrics",
        numeric_columns,
        default=numeric_columns[: min(3, len(numeric_columns))],
    )

    for column in selected_columns:
        st.line_chart(df[column], height=220)

    st.divider()
    st.subheader("Recommended Actions")

    for item in recommendations:
        st.markdown(f"- {item}")

    st.divider()
    st.subheader("🤖 AI Infrastructure Assessment")

    with st.spinner("Coordinator Agent analyzing sensor data..."):
        report = coordinate_sensor_workflow(summary)

    st.markdown(report)

    st.divider()
    st.subheader("Summary Statistics")
    st.dataframe(
        df.describe(),
        use_container_width=True,
    )
