import streamlit as st
import pandas as pd

from agents.coordinator import coordinate_sensor_workflow


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

    df = pd.read_csv(sensor_file)

    st.subheader("Sensor Data")

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    numeric_columns = df.select_dtypes(include="number").columns

    st.subheader("Charts")

    for column in numeric_columns:

        st.write(f"### {column.title()}")

        st.line_chart(df[column])

    summary = {}

    for column in numeric_columns:

        summary[column] = {
            "min": float(df[column].min()),
            "max": float(df[column].max()),
            "mean": round(float(df[column].mean()), 2),
        }

    st.divider()

    col1, col2, col3 = st.columns(3)

    if "temperature" in df.columns:

        col1.metric(
            "Maximum Temperature",
            f"{df['temperature'].max()}°F",
        )

        col2.metric(
            "Average Temperature",
            f"{round(df['temperature'].mean(), 1)}°F",
        )

    if "power_kw" in df.columns:

        col3.metric(
            "Peak Power",
            f"{df['power_kw'].max()} kW",
        )

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