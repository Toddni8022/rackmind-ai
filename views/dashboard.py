import pandas as pd
import plotly.express as px
import streamlit as st

from config import (
    AI_PROVIDER,
    APP_NAME,
    APP_VERSION,
    POWER_WARNING,
    SAMPLE_DIR,
    TEMP_CRITICAL,
    TEMP_WARNING,
)
from services.vector_service import collection

PLOT_CONFIG = {
    "displaylogo": False,
    "modeBarButtonsToRemove": ["lasso2d", "select2d"],
}


def _trend_chart(df, column, title, y_label, kind=px.line):

    fig = kind(
        df,
        x="timestamp",
        y=column,
        title=title,
        **({"markers": True} if kind is px.line else {}),
    )

    fig.update_layout(
        template="plotly_dark",
        height=350,
        xaxis_title="Time",
        yaxis_title=y_label,
    )

    st.plotly_chart(fig, use_container_width=True, config=PLOT_CONFIG)


def show_dashboard():

    st.header("🏠 RackMind Operations Center")

    st.caption(f"{APP_NAME} | Version {APP_VERSION}")

    csv_path = SAMPLE_DIR / "sensors" / "rack22.csv"

    if not csv_path.exists():
        st.error("Sample sensor data not found.")
        return

    df = pd.read_csv(csv_path)

    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
    )

    required = {"timestamp", "temperature", "humidity", "power_kw"}
    missing = required - set(df.columns)

    if missing:
        st.error(f"Sample sensor data is missing columns: {', '.join(sorted(missing))}")
        return

    df["timestamp"] = pd.to_datetime(df["timestamp"])

    max_temp = round(df["temperature"].max(), 1)
    avg_temp = round(df["temperature"].mean(), 1)
    avg_humidity = round(df["humidity"].mean(), 1)
    peak_power = round(df["power_kw"].max(), 2)

    runbooks = collection.count()

    alerts = []

    if max_temp >= TEMP_CRITICAL:
        alerts.append(f"🔥 Rack temperature exceeds {TEMP_CRITICAL}°F")

    if peak_power >= POWER_WARNING:
        alerts.append("⚡ High rack power consumption")

    if runbooks == 0:
        alerts.append("📄 No indexed runbooks")

    if max_temp >= TEMP_CRITICAL:
        health = "🔴 Critical"
    elif max_temp >= TEMP_WARNING:
        health = "🟡 Warning"
    else:
        health = "🟢 Healthy"

    st.divider()

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Rack Health", health)
    c2.metric("Max Temp", f"{max_temp}°F")
    c3.metric("Humidity", f"{avg_humidity}%")
    c4.metric("Peak Power", f"{peak_power} kW")

    st.divider()

    left, right = st.columns([2, 1])

    with left:

        st.subheader("🚨 Active Alerts")

        if alerts:

            for alert in alerts:
                st.error(alert)

        else:

            st.success("No active alerts detected.")

        st.subheader("Executive Summary")

        st.info(f"""
Rack Health: **{health}**

Maximum Temperature: **{max_temp}°F**

Average Temperature: **{avg_temp}°F**

Average Humidity: **{avg_humidity}%**

Peak Power: **{peak_power} kW**

Indexed Runbooks: **{runbooks}**
""")

    with right:

        st.subheader("Platform")

        st.success("✅ Google ADK Agents")
        st.success(f"🤖 AI Provider: {AI_PROVIDER}")
        st.success("🔎 Keyword Runbook Search")
        st.success(f"📚 {runbooks} Runbooks")

    st.divider()

    _trend_chart(df, "temperature", "Temperature Trend", "Temperature (°F)")
    _trend_chart(df, "humidity", "Humidity Trend", "Humidity (%)")
    _trend_chart(df, "power_kw", "Power Consumption", "Power (kW)", kind=px.area)

    st.divider()

    st.caption(
        f"{APP_NAME} v{APP_VERSION} | Google ADK | Gemini | OpenAI"
    )
