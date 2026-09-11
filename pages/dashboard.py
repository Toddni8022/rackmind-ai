import json
import pandas as pd
import plotly.express as px
import streamlit as st
from config import APP_NAME, APP_VERSION, SAMPLE_DIR, TEMP_WARNING, TEMP_CRITICAL, POWER_WARNING
from services.telemetry_service import assess_telemetry, prepare_telemetry
from services.interface import apply_design, overview_header, rack_overview
from services.audit import record


def _metric(value, unit):
    return "N/A" if pd.isna(value) else f"{value:.1f} {unit}"


def show_dashboard():
    apply_design()
    overview_header()
    source = st.radio("Data source", ["Sample data", "Upload CSV"], horizontal=True, key="dashboard_source")
    if source == "Upload CSV":
        upload = st.file_uploader("Upload rack telemetry (max 10 MB)", type=["csv"], key="dashboard_csv")
        if upload is None:
            st.info("Upload a CSV with temperature (°F), humidity (%), or power_kw. Add a rack column to compare racks.")
            return
        csv_source, source_name = upload, upload.name
        if getattr(upload, "size", 0) > 10 * 1024 * 1024:
            st.error("This upload exceeds the 10 MB safety limit.")
            return
        record("telemetry_upload", st.session_state.get("rackmind_user", "demo"), {"filename": upload.name, "bytes": getattr(upload, "size", 0)})
        st.info("Uploaded snapshot · Assessment stays in this app and makes no AI provider calls.")
    else:
        csv_source = SAMPLE_DIR / "sensors" / "rack22.csv"
        source_name = "Rack 22 sample"
        st.info("Demo data · Bundled Rack 22 readings. This is not a live facility feed.")
    try:
        raw = pd.read_csv(csv_source)
        if source == "Sample data":
            raw["rack"] = "Rack 22"
        telemetry = prepare_telemetry(raw)
    except (ValueError, OSError, pd.errors.ParserError) as exc:
        st.error(f"Unable to review telemetry: {exc}")
        return
    options = sorted(telemetry["rack"].unique())
    selected = st.multiselect("Racks to review", options, default=options)
    if not selected:
        st.info("Select at least one rack to review.")
        return
    readings = telemetry[telemetry["rack"].isin(selected)].copy()
    assessment = assess_telemetry(readings, TEMP_WARNING, TEMP_CRITICAL, POWER_WARNING)
    rack_label = "rack" if len(selected) == 1 else "racks"
    st.caption(f"{source_name} · {len(readings):,} samples · {len(selected)} {rack_label} · Assessment covers all selected readings, not current live conditions.")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Review status", assessment["status"])
    c2.metric("Peak temperature", _metric(readings["temperature"].max(), "°F"))
    c3.metric("Average humidity", _metric(readings["humidity"].mean(), "%"))
    c4.metric("Peak power", _metric(readings["power_kw"].max(), "kW"))
    rack_overview(assessment["racks"])
    st.subheader("Priority review queue")
    if assessment["alerts"]:
        for alert in assessment["alerts"]:
            message = f"{alert['severity']} · {alert['rack']} · {alert['detail']} — {alert['action']}"
            renderer = st.error if alert["severity"] == "Critical" else st.warning
            renderer(message)
    else:
        st.success("No temperature or power thresholds exceeded in these readings.")
    st.caption(f"Demo thresholds: temperature warning ≥ {TEMP_WARNING} °F, critical ≥ {TEMP_CRITICAL} °F; power warning ≥ {POWER_WARNING} kW. Humidity is displayed for context; no humidity alarm policy is applied. Follow your facility's approved thresholds and response procedures.")
    with st.expander("Rack details and coverage"):
        st.dataframe(pd.DataFrame(assessment["racks"]), hide_index=True, width="stretch")
    st.subheader("Telemetry trends")
    st.caption("Samples follow file order within each rack. Gaps represent missing or invalid readings; timestamps are shown as supplied, without freshness validation.")
    readings["sample"] = readings.groupby("rack").cumcount() + 1
    panels = st.tabs(["Temperature", "Humidity", "Power"])
    for panel, metric, label in zip(panels, ["temperature", "humidity", "power_kw"], ["Temperature (°F)", "Humidity (%)", "Power (kW)"]):
        with panel:
            if readings[metric].notna().any():
                hover = ["timestamp"] if "timestamp" in readings.columns else None
                figure = px.line(readings, x="sample", y=metric, color="rack", markers=True, hover_data=hover,
                                 color_discrete_sequence=["#d4f77d", "#ff9c7c", "#83c7c7", "#d3b3ef", "#efcc79"],
                                 labels={"sample": "Sample in file order", metric: label, "rack": "Rack"})
                if metric == "temperature":
                    figure.add_hline(y=TEMP_WARNING, line_dash="dot", line_color="#d97706", annotation_text="Warning")
                    figure.add_hline(y=TEMP_CRITICAL, line_dash="dot", line_color="#dc2626", annotation_text="Critical")
                elif metric == "power_kw":
                    figure.add_hline(y=POWER_WARNING, line_dash="dot", line_color="#d97706", annotation_text="Warning")
                figure.update_traces(line_width=2.5, marker_size=5)
                figure.update_layout(height=350, margin=dict(l=20, r=20, t=35, b=20),
                                     paper_bgcolor="#19241c", plot_bgcolor="#19241c",
                                     font=dict(color="#cbd7c9", family="DM Sans"),
                                     legend=dict(orientation="h", y=1.15, x=0), hovermode="x unified")
                figure.update_xaxes(gridcolor="#2c3a30", zeroline=False)
                figure.update_yaxes(gridcolor="#2c3a30", zeroline=False)
                st.plotly_chart(figure, width="stretch", config={"displaylogo": False})
            else:
                st.info(f"No valid {label.lower()} readings in this selection.")
    with st.expander("Inspect readings"):
        st.dataframe(readings.drop(columns="sample"), hide_index=True, use_container_width=True)
    report = {"source": source_name, "scope": "Selected upload window; not live monitoring",
              "thresholds": {"temperature_warning_f": TEMP_WARNING, "temperature_critical_f": TEMP_CRITICAL,
                             "power_warning_kw": POWER_WARNING}, **assessment}
    st.download_button("Download review report", json.dumps(report, indent=2, allow_nan=False),
                       file_name="rackmind-telemetry-review.json", mime="application/json")
