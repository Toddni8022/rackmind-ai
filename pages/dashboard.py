import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

from config import APP_NAME, APP_VERSION
from services.vector_service import collection


def show_dashboard():

    st.header("🏠 RackMind Operations Center")

    st.caption(f"{APP_NAME} | Version {APP_VERSION}")

    csv_path = Path("sample_data/sensors/rack22.csv")

    if csv_path.exists():

        df = pd.read_csv(csv_path)

        df.columns = (
            df.columns
            .str.strip()
            .str.lower()
        )

        df["timestamp"] = pd.to_datetime(df["timestamp"])

        max_temp = round(df["temperature"].max(), 1)
        avg_temp = round(df["temperature"].mean(), 1)
        avg_humidity = round(df["humidity"].mean(), 1)
        peak_power = round(df["power_kw"].max(), 2)

    else:

        st.error("Sensor data not found.")

        return

    runbooks = collection.count()

    alerts = []

    if max_temp >= 90:
        alerts.append("🔥 Rack temperature exceeds 90°F")

    if peak_power >= 4.5:
        alerts.append("⚡ High rack power consumption")

    if runbooks == 0:
        alerts.append("📄 No indexed runbooks")

    if max_temp >= 90:
        health = "🔴 Critical"
    elif max_temp >= 80:
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

    left, right = st.columns([2,1])

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

        st.success("✅ Google ADK")
        st.success("✅ Gemini")
        st.success("✅ ChromaDB")
        st.success(f"📚 {runbooks} Runbooks")

    st.divider()

    fig_temp = px.line(
        df,
        x="timestamp",
        y="temperature",
        title="Temperature Trend",
        markers=True,
    )

    fig_temp.update_layout(
        template="plotly_dark",
        height=350,
        xaxis_title="Time",
        yaxis_title="Temperature (°F)",
    )

    st.plotly_chart(
        fig_temp,
        use_container_width=True,
        config={
            "displaylogo": False,
            "modeBarButtonsToRemove": [
                "lasso2d",
                "select2d",
            ],
        },
    )

    fig_humidity = px.line(
        df,
        x="timestamp",
        y="humidity",
        title="Humidity Trend",
        markers=True,
    )

    fig_humidity.update_layout(
        template="plotly_dark",
        height=350,
        xaxis_title="Time",
        yaxis_title="Humidity (%)",
    )

    st.plotly_chart(
        fig_humidity,
        use_container_width=True,
        config={"displaylogo": False},
    )

    fig_power = px.area(
        df,
        x="timestamp",
        y="power_kw",
        title="Power Consumption",
    )

    fig_power.update_layout(
        template="plotly_dark",
        height=350,
        xaxis_title="Time",
        yaxis_title="Power (kW)",
    )

    st.plotly_chart(
        fig_power,
        use_container_width=True,
        config={"displaylogo": False},
    )

    st.divider()

    st.caption(
        "RackMind AI v1.0 | Google ADK | Gemini | ChromaDB"
    )