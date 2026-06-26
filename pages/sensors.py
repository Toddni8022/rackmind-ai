import streamlit as st
import pandas as pd

from agents.coordinator import coordinate_sensor_workflow
from services.sensor_parser import normalize_sensor_dataframe, parse_sensor_data


def _metric_value(value, suffix=""):

    if value is None:
        return "N/A"

    return f"{value}{suffix}"


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
        st.error(f"Unable to read sensor CSV: {ex}")
        return

    if df.empty:
        st.warning("The uploaded CSV does not contain any rows.")
        return

    df = normalize_sensor_dataframe(df)

    st.subheader("Sensor Data")

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    numeric_columns = df.select_dtypes(include="number").columns.tolist()

    if not numeric_columns:
        st.warning("No numeric sensor columns were found in this CSV.")
        return

    st.subheader("Charts")

    for column in numeric_columns:

        st.write(f"### {column.replace('_', ' ').title()}")

        st.line_chart(df[column])

    summary = parse_sensor_data(df)

    st.divider()

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Maximum Temperature",
        _metric_value(summary.get("max_temp"), "°F"),
    )

    col2.metric(
        "Average Temperature",
        _metric_value(summary.get("avg_temp"), "°F"),
    )

    col3.metric(
        "Peak Power",
        _metric_value(summary.get("peak_power"), " kW"),
    )

    st.divider()

    st.subheader("🤖 AI Infrastructure Assessment")

    with st.spinner("Coordinator Agent analyzing sensor data..."):

        report = coordinate_sensor_workflow(summary)

    st.markdown(report)

    st.divider()

    st.subheader("Summary Statistics")

    st.dataframe(
        df[numeric_columns].describe(),
        use_container_width=True,
    )
