import streamlit as st
import pandas as pd


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

    st.divider()

    if "temperature" in df.columns:

        max_temp = df["temperature"].max()
        avg_temp = round(df["temperature"].mean(), 1)

        col1, col2 = st.columns(2)

        col1.metric(
            "Maximum Temperature",
            f"{max_temp}°F"
        )

        col2.metric(
            "Average Temperature",
            f"{avg_temp}°F"
        )

        st.divider()

        st.subheader("🤖 AI Insight")

        if max_temp >= 90:

            st.error(
                """
Critical temperature detected.

### Recommended Actions

- Verify rack airflow
- Inspect cooling fans
- Check power utilization
- Schedule immediate inspection
"""
            )

        elif max_temp >= 80:

            st.warning(
                """
Elevated temperatures detected.

### Recommended Actions

- Increase monitoring frequency
- Verify cooling efficiency
"""
            )

        else:

            st.success(
                "Infrastructure temperatures are within normal operating limits."
            )

    st.divider()

    st.subheader("Summary Statistics")

    st.dataframe(
        df.describe(),
        use_container_width=True,
    )