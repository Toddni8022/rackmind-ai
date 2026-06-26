from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from config import APP_NAME, APP_VERSION
from services.assessment_service import (
    build_alerts,
    build_recommendations,
    score_sensor_summary,
)
from services.sensor_parser import parse_sensor_data
from services.vector_service import collection


REQUIRED_COLUMNS = {"timestamp", "temperature", "humidity", "power_kw"}


def show_dashboard():

    st.header("🏠 RackMind Operations Center")
    st.caption(f"{APP_NAME} | Version {APP_VERSION}")

    csv_path = Path("sample_data/sensors/rack22.csv")

    if not csv_path.exists():
        st.error("Sensor data not found.")
        return

    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip().str.lower()

    missing_columns = REQUIRED_COLUMNS.difference(df.columns)

    if missing_columns:
        st.error(
            "Sample sensor data is missing: "
            + ", ".join(sorted(missing_columns))
        )
        return

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        errors="coerce",
    )
    df = df.dropna(subset=["timestamp"])

    sensor_summary = parse_sensor_data(df)
    scorecard = score_sensor_summary(sensor_summary)
    runbooks = collection.count()
    alerts = build_alerts(
        sensor_summary=sensor_summary,
        runbooks=runbooks,
    )
    recommendations = build_recommendations(
        sensor_summary=sensor_summary,
        runbooks=runbooks,
    )

    st.divider()

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric("Health", scorecard["status"])
    c2.metric("Score", f"{scorecard['score']}/100")
    c3.metric("Max Temp", f"{sensor_summary['max_temp']:.1f}°F")
    c4.metric("Humidity", f"{sensor_summary['avg_humidity']:.1f}%")
    c5.metric("Peak Power", f"{sensor_summary['peak_power']:.2f} kW")

    st.progress(scorecard["score"] / 100)

    st.divider()

    left, right = st.columns([1.6, 1])

    with left:

        st.subheader("Active Signals")

        if alerts:
            for alert in alerts:
                st.warning(alert)
        else:
            st.success("No active alerts detected.")

        st.subheader("Recommended Actions")

        for item in recommendations:
            st.markdown(f"- {item}")

    with right:

        st.subheader("Readiness")
        st.metric("Indexed Runbooks", runbooks)
        st.metric("Telemetry Samples", len(df))
        st.metric("Severity", scorecard["severity"])

        if runbooks:
            st.success("Runbook retrieval is ready.")
        else:
            st.warning("Runbook retrieval needs indexing.")

    st.divider()

    fig_temp = px.line(
        df,
        x="timestamp",
        y="temperature",
        title="Temperature Trend",
        markers=True,
    )

    fig_temp.add_hline(
        y=80,
        line_dash="dash",
        line_color="orange",
        annotation_text="Warning",
    )
    fig_temp.add_hline(
        y=90,
        line_dash="dash",
        line_color="red",
        annotation_text="Critical",
    )
    fig_temp.update_layout(
        template="plotly_dark",
        height=360,
        xaxis_title="Time",
        yaxis_title="Temperature (°F)",
    )

    st.plotly_chart(
        fig_temp,
        use_container_width=True,
        config={"displaylogo": False},
    )

    col_a, col_b = st.columns(2)

    with col_a:
        fig_humidity = px.line(
            df,
            x="timestamp",
            y="humidity",
            title="Humidity Trend",
            markers=True,
        )
        fig_humidity.update_layout(
            template="plotly_dark",
            height=320,
            xaxis_title="Time",
            yaxis_title="Humidity (%)",
        )
        st.plotly_chart(
            fig_humidity,
            use_container_width=True,
            config={"displaylogo": False},
        )

    with col_b:
        fig_power = px.area(
            df,
            x="timestamp",
            y="power_kw",
            title="Power Consumption",
        )
        fig_power.add_hline(
            y=4.5,
            line_dash="dash",
            line_color="orange",
            annotation_text="High draw",
        )
        fig_power.update_layout(
            template="plotly_dark",
            height=320,
            xaxis_title="Time",
            yaxis_title="Power (kW)",
        )
        st.plotly_chart(
            fig_power,
            use_container_width=True,
            config={"displaylogo": False},
        )

    st.divider()
    st.caption("RackMind AI v1.0 | Google ADK | Gemini | ChromaDB")
