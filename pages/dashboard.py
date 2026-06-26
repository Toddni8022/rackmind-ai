from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from config import APP_NAME, APP_VERSION
from services.assessment_service import (
    build_alerts,
    build_recommendations,
    normalize_log_summary,
    normalize_sensor_summary,
    score_operations,
)
from services.app_state import (
    clear_runtime_state,
    load_runtime_state,
    records_to_dataframe,
)
from services.sensor_parser import parse_sensor_data
from services.vector_service import collection


REQUIRED_COLUMNS = {"timestamp", "temperature", "humidity", "power_kw"}


def _load_sensor_data():
    if "rackmind_sensor_df" in st.session_state:
        return (
            st.session_state["rackmind_sensor_df"].copy(),
            st.session_state.get("rackmind_sensor_summary", {}),
            st.session_state.get("rackmind_sensor_source", "uploaded sensor data"),
            True,
        )

    runtime_state = load_runtime_state()
    persisted_df = records_to_dataframe(runtime_state.get("sensor_records"))

    if persisted_df is not None:
        persisted_df.columns = persisted_df.columns.str.strip().str.lower()

        return (
            persisted_df,
            runtime_state.get("sensor_summary", {}),
            runtime_state.get("sensor_source", "latest saved sensor data"),
            True,
        )

    csv_path = Path("sample_data/sensors/rack22.csv")

    if not csv_path.exists():
        return None, {}, "missing sample data", False

    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip().str.lower()

    missing_columns = REQUIRED_COLUMNS.difference(df.columns)

    if missing_columns:
        st.error(
            "Sample sensor data is missing: "
            + ", ".join(sorted(missing_columns))
        )
        return None, {}, "invalid sample data", False

    return df, parse_sensor_data(df), "sample_data/sensors/rack22.csv", False


def _prepare_chart_data(df):
    df = df.copy()

    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(
            df["timestamp"],
            format="mixed",
            errors="coerce",
        )
        df = df.dropna(subset=["timestamp"])
        return df, "timestamp"

    df["reading"] = range(1, len(df) + 1)
    return df, "reading"


def show_dashboard():

    st.header("🏠 RackMind Operations Center")
    st.caption(f"{APP_NAME} | Version {APP_VERSION}")

    runtime_state = load_runtime_state()
    df, sensor_summary, sensor_source, is_live_sensor = _load_sensor_data()

    if df is None:
        st.error("Sensor data not found.")
        return

    sensor_summary = normalize_sensor_summary(sensor_summary)
    df, x_axis = _prepare_chart_data(df)
    log_summary = st.session_state.get(
        "rackmind_log_summary",
        runtime_state.get("log_summary"),
    )
    log = normalize_log_summary(log_summary)
    scorecard = score_operations(log_summary, sensor_summary)

    runbooks = collection.count()
    alerts = build_alerts(
        log_summary=log_summary,
        sensor_summary=sensor_summary,
        runbooks=runbooks,
    )
    recommendations = build_recommendations(
        log_summary=log_summary,
        sensor_summary=sensor_summary,
        runbooks=runbooks,
    )

    st.divider()

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric("Health", scorecard["status"])
    c2.metric("Score", f"{scorecard['score']}/100")
    c3.metric("Max Temp", f"{sensor_summary['max_temp']:.1f}°F")
    c4.metric("Log Errors", log["errors"])
    c5.metric("CRC Errors", log["crc_errors"])

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

        st.subheader("Data Sync")
        if is_live_sensor:
            st.success(f"Sensor data: {sensor_source}")
        else:
            st.info(f"Sensor data: {sensor_source}")

        if log_summary:
            st.success(
                "Log data: "
                + st.session_state.get(
                    "rackmind_log_source",
                    runtime_state.get("log_source", "latest analysis"),
                )
            )
        else:
            st.info("Log data: no log analyzed yet")

        if runtime_state.get("updated_at"):
            st.caption(f"Last analysis: {runtime_state['updated_at']}")

        if st.button("Reset to sample data", width="stretch"):
            for key in (
                "rackmind_log_summary",
                "rackmind_log_source",
                "rackmind_sensor_df",
                "rackmind_sensor_summary",
                "rackmind_sensor_source",
            ):
                st.session_state.pop(key, None)

            clear_runtime_state()
            st.rerun()

        st.subheader("Readiness")
        st.metric("Indexed Runbooks", runbooks)
        st.metric("Telemetry Samples", len(df))
        st.metric("Severity", scorecard["severity"])
        st.metric("Interface Resets", log["resets"])

        if runbooks:
            st.success("Runbook retrieval is ready.")
        else:
            st.warning("Runbook retrieval needs indexing.")

    st.divider()

    if "temperature" in df.columns:
        fig_temp = px.line(
            df,
            x=x_axis,
            y="temperature",
            title="Temperature Trend",
            markers=True,
            color_discrete_sequence=["#22d3ee"],
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
            paper_bgcolor="rgba(15, 23, 42, 0)",
            plot_bgcolor="rgba(15, 23, 42, 0.38)",
            font_color="#e0f2fe",
            height=360,
            xaxis_title="Time" if x_axis == "timestamp" else "Reading",
            yaxis_title="Temperature (°F)",
        )

        st.plotly_chart(
            fig_temp,
            width="stretch",
            config={"displaylogo": False},
        )
    else:
        st.info("No temperature column is available for dashboard trend charts.")

    col_a, col_b = st.columns(2)

    with col_a:
        if "humidity" in df.columns:
            fig_humidity = px.line(
                df,
                x=x_axis,
                y="humidity",
                title="Humidity Trend",
                markers=True,
                color_discrete_sequence=["#10b981"],
            )
            fig_humidity.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(15, 23, 42, 0)",
                plot_bgcolor="rgba(15, 23, 42, 0.38)",
                font_color="#e0f2fe",
                height=320,
                xaxis_title="Time" if x_axis == "timestamp" else "Reading",
                yaxis_title="Humidity (%)",
            )
            st.plotly_chart(
                fig_humidity,
                width="stretch",
                config={"displaylogo": False},
            )
        else:
            st.info("No humidity column is available.")

    with col_b:
        if "power_kw" in df.columns:
            fig_power = px.area(
                df,
                x=x_axis,
                y="power_kw",
                title="Power Consumption",
                color_discrete_sequence=["#ec4899"],
            )
            fig_power.add_hline(
                y=4.5,
                line_dash="dash",
                line_color="orange",
                annotation_text="High draw",
            )
            fig_power.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(15, 23, 42, 0)",
                plot_bgcolor="rgba(15, 23, 42, 0.38)",
                font_color="#e0f2fe",
                height=320,
                xaxis_title="Time" if x_axis == "timestamp" else "Reading",
                yaxis_title="Power (kW)",
            )
            st.plotly_chart(
                fig_power,
                width="stretch",
                config={"displaylogo": False},
            )
        else:
            st.info("No power_kw column is available.")

    st.divider()
    st.caption("RackMind AI v1.0 | Google ADK | Gemini | ChromaDB")
