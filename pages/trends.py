import pandas as pd
import plotly.express as px
import streamlit as st

from config import TEMP_CRITICAL, TEMP_WARNING
from services.telemetry_store import get_history, list_racks
from services.trend_service import (
    PREDICTION_WINDOW_HOURS,
    analyze_all_racks,
    seed_sample_telemetry,
)

METRIC_LABELS = {
    "temperature": "Temperature (°F)",
    "power_kw": "Power (kW)",
    "crc_errors": "CRC Errors",
    "resets": "Interface Resets",
    "health_score": "Health Score",
}

RISK_BADGES = {
    "Critical": "🔴",
    "At Risk": "🟠",
    "Stable": "🟢",
}


def show_trends(user=None):

    st.header("📈 Trends + Predictions")
    st.caption(
        "Temperature, power, CRC errors, resets, and health score over "
        "time — with racks likely to become critical flagged early"
    )

    seeded = seed_sample_telemetry()

    if seeded:
        st.info(
            f"Loaded {seeded} sample telemetry readings. Use the Live "
            "Telemetry tab to feed real data."
        )

    racks = list_racks()

    if not racks:
        st.warning(
            "No telemetry history yet. Fetch data on the Live Telemetry "
            "tab first."
        )
        return

    # ---------------- Predictions ----------------

    st.subheader("🔮 Rack Risk Predictions")

    predictions = analyze_all_racks()

    flagged = [p for p in predictions if p["risk"] != "Stable"]

    if flagged:
        for prediction in flagged:
            badge = RISK_BADGES.get(prediction["risk"], "⚪")

            reasons = "; ".join(prediction["reasons"]) or "Thresholds breached"

            message = f"{badge} **{prediction['rack']}** — {prediction['risk']}: {reasons}"

            if prediction["risk"] == "Critical":
                st.error(message)
            else:
                st.warning(message)
    else:
        st.success(
            f"🟢 No racks are projected to go critical within "
            f"{PREDICTION_WINDOW_HOURS} hours."
        )

    table = pd.DataFrame(
        [
            {
                "Rack": p["rack"],
                "Risk": f"{RISK_BADGES.get(p['risk'], '⚪')} {p['risk']}",
                "ETA (h)": p["eta_hours"] if p["eta_hours"] is not None else "—",
                "Latest Temp (°F)": p["latest_temperature"],
                "Latest Power (kW)": p["latest_power_kw"],
                "Health Score": p["latest_health_score"],
                "Temp Slope (°F/h)": p["temp_slope_per_hour"],
                "Samples": p["samples"],
            }
            for p in predictions
        ]
    )

    st.dataframe(table, use_container_width=True, hide_index=True)

    st.divider()

    # ---------------- Trend charts ----------------

    st.subheader("📊 Metric History")

    c1, c2 = st.columns(2)

    selected_racks = c1.multiselect(
        "Racks",
        racks,
        default=racks,
    )

    metric = c2.selectbox(
        "Metric",
        list(METRIC_LABELS.keys()),
        format_func=METRIC_LABELS.get,
    )

    if not selected_racks:
        st.info("Select at least one rack.")
        return

    rows = []

    for rack in selected_racks:
        rows.extend(get_history(rack=rack))

    df = pd.DataFrame(rows)

    if df.empty or metric not in df.columns or df[metric].dropna().empty:
        st.info(f"No {METRIC_LABELS[metric]} data recorded yet.")
        return

    df["recorded_at"] = pd.to_datetime(df["recorded_at"], errors="coerce")

    fig = px.line(
        df.dropna(subset=[metric]),
        x="recorded_at",
        y=metric,
        color="rack",
        markers=True,
        title=f"{METRIC_LABELS[metric]} Over Time",
        labels={"recorded_at": "Time", metric: METRIC_LABELS[metric]},
    )

    if metric == "temperature":
        fig.add_hline(
            y=TEMP_WARNING,
            line_dash="dash",
            line_color="orange",
            annotation_text=f"Warning ({TEMP_WARNING}°F)",
        )
        fig.add_hline(
            y=TEMP_CRITICAL,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Critical ({TEMP_CRITICAL}°F)",
        )

    if metric == "health_score":
        fig.add_hline(
            y=70,
            line_dash="dash",
            line_color="red",
            annotation_text="Critical (<70)",
        )

    st.plotly_chart(fig, use_container_width=True)

    st.caption(
        f"{len(df)} readings across {len(selected_racks)} rack(s). "
        "Predictions use a least-squares trend over each rack's history."
    )
