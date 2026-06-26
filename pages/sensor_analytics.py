import streamlit as st
import pandas as pd

from agents.root_cause_agent import analyze_root_cause


def show_sensors():
    """
    AI Infrastructure Health Monitor

    Upload a CSV containing sensor readings and automatically:
    - Preview the data
    - Display summary statistics
    - Plot selected metrics
    - Detect anomalies
    - Generate a health score
    - Produce an AI root cause analysis
    """

    st.header("📊 AI Infrastructure Health Monitor")
    st.caption("AI-powered environmental monitoring and anomaly detection")

    sensor_file = st.file_uploader(
        "Upload Sensor CSV",
        type=["csv"],
        key="sensor_upload"
    )

    if sensor_file is None:
        st.info("Upload a sensor CSV to begin analysis.")
        return

    try:
        df = pd.read_csv(sensor_file)
    except Exception as e:
        st.error(f"Unable to read CSV: {e}")
        return

    st.subheader("Dataset Preview")
    st.dataframe(df.head())

    st.subheader("Dataset Information")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Rows", len(df))

    with col2:
        st.metric("Columns", len(df.columns))

    st.subheader("Summary Statistics")
    st.dataframe(df.describe())

    numeric_columns = df.select_dtypes(include=["number"]).columns.tolist()

    if len(numeric_columns) == 0:
        st.warning("No numeric columns were found in this dataset.")
        return

    st.subheader("Metric Visualization")

    selected_metric = st.selectbox(
        "Select a metric",
        numeric_columns
    )

    st.line_chart(df[selected_metric])

    mean_value = df[selected_metric].mean()
    std_value = df[selected_metric].std()

    upper_limit = mean_value + (2 * std_value)
    lower_limit = mean_value - (2 * std_value)

    anomalies = df[
        (df[selected_metric] > upper_limit)
        | (df[selected_metric] < lower_limit)
    ]

    st.subheader("AI Anomaly Detection")

    if anomalies.empty:
        st.success("No significant anomalies detected.")
    else:
        st.warning(
            f"{len(anomalies)} potential anomalies detected."
        )
        st.dataframe(anomalies)

    anomaly_count = len(anomalies)

    health_score = max(
        0,
        min(100, 100 - (anomaly_count * 2))
    )

    st.subheader("Infrastructure Health Score")

    st.progress(health_score / 100)

    st.metric(
        "Health Score",
        f"{health_score}/100"
    )

    if health_score >= 90:
        st.success("System Status: Healthy")
    elif health_score >= 70:
        st.warning("System Status: Monitor Closely")
    else:
        st.error("System Status: Immediate Attention Recommended")

    st.subheader("🤖 AI Root Cause Analysis")

    analysis = analyze_root_cause(
        metric_name=selected_metric,
        mean_value=mean_value,
        std_value=std_value,
        anomaly_count=anomaly_count,
        health_score=health_score,
    )

    st.info(analysis)