import pandas as pd
import streamlit as st

from agents.coordinator import coordinate_sensor_workflow
from connectors import (
    CONNECTORS,
    CloudWatchConnector,
    ConnectorError,
    PrometheusConnector,
    RedfishConnector,
    SimulatorConnector,
    SNMPConnector,
    SyslogConnector,
)
from services.sensor_parser import parse_sensor_data
from services.telemetry_store import record_readings


def _build_connector(kind: str):
    """
    Render config inputs for the chosen connector and return a
    ready-to-fetch instance.
    """

    if kind == "simulator":

        racks = st.text_input(
            "Racks (comma separated)",
            value="Rack-22, Rack-07, Rack-14",
            key="sim_racks",
        )

        samples = st.slider("Samples per rack", 6, 48, 12, key="sim_samples")

        return SimulatorConnector(
            racks=[r.strip() for r in racks.split(",") if r.strip()],
            samples=samples,
        )

    if kind == "prometheus":

        url = st.text_input(
            "Prometheus URL",
            placeholder="http://prometheus:9090",
            key="prom_url",
        )

        c1, c2 = st.columns(2)

        temp_query = c1.text_input(
            "Temperature query",
            value="rack_temperature_fahrenheit",
            key="prom_temp",
        )

        power_query = c2.text_input(
            "Power (kW) query",
            value="rack_power_kw",
            key="prom_power",
        )

        return PrometheusConnector(
            base_url=url,
            metric_queries={
                "temperature": temp_query,
                "power_kw": power_query,
            },
        )

    if kind == "redfish":

        url = st.text_input(
            "BMC URL",
            placeholder="https://bmc.example.com",
            key="rf_url",
        )

        c1, c2, c3 = st.columns(3)

        username = c1.text_input("Username", key="rf_user")
        password = c2.text_input("Password", type="password", key="rf_pass")
        chassis = c3.text_input("Chassis ID", value="1", key="rf_chassis")

        rack = st.text_input("Rack label", placeholder="Rack-22", key="rf_rack")

        verify = st.checkbox(
            "Verify TLS certificate",
            value=True,
            key="rf_tls",
            help="Uncheck only for lab BMCs with self-signed certificates.",
        )

        return RedfishConnector(
            base_url=url,
            username=username,
            password=password,
            chassis_id=chassis,
            rack=rack or None,
            verify_tls=verify,
        )

    if kind == "snmp":

        c1, c2, c3 = st.columns(3)

        host = c1.text_input("Host", placeholder="10.0.0.5", key="snmp_host")
        community = c2.text_input("Community", value="public", key="snmp_comm")
        port = c3.number_input("Port", value=161, key="snmp_port")

        rack = st.text_input("Rack label", placeholder="Rack-22", key="snmp_rack")

        temp_oid = st.text_input(
            "Temperature OID",
            value="1.3.6.1.4.1.9.9.13.1.3.1.3.1",
            key="snmp_temp_oid",
        )

        power_oid = st.text_input(
            "Power (kW) OID (optional)",
            key="snmp_power_oid",
        )

        return SNMPConnector(
            host=host,
            community=community,
            port=int(port),
            rack=rack or None,
            oids={
                "temperature": temp_oid,
                "power_kw": power_oid,
            },
        )

    if kind == "syslog":

        path = st.text_input(
            "Syslog file path",
            value="data/switch.log",
            key="syslog_path",
            help="Point rsyslog / syslog-ng forwarding at a file RackMind can read.",
        )

        rack = st.text_input(
            "Rack label (optional, otherwise parsed from messages)",
            key="syslog_rack",
        )

        return SyslogConnector(path=path, rack=rack or None)

    if kind == "cloudwatch":

        c1, c2 = st.columns(2)

        namespace = c1.text_input(
            "Namespace", value="DataCenter", key="cw_ns"
        )

        region = c2.text_input("Region", value="us-east-1", key="cw_region")

        racks = st.text_input(
            "Racks (comma separated)",
            placeholder="Rack-22, Rack-07",
            key="cw_racks",
        )

        return CloudWatchConnector(
            namespace=namespace,
            region=region,
            racks=[r.strip() for r in racks.split(",") if r.strip()],
        )

    raise ConnectorError(f"Unknown connector: {kind}")


def show_telemetry(user=None):

    st.header("📡 Live Telemetry")
    st.caption(
        "Pull rack telemetry directly from SNMP, Redfish, Prometheus, "
        "syslog, or cloud monitoring instead of uploading files"
    )

    kind = st.selectbox(
        "Telemetry source",
        list(CONNECTORS.keys()),
        format_func=lambda name: (
            f"{name.title()} — {CONNECTORS[name].description}"
        ),
    )

    connector = _build_connector(kind)

    store_history = st.checkbox(
        "Save readings to telemetry history (feeds the Trends dashboard)",
        value=True,
    )

    if not st.button("📥 Fetch Telemetry", type="primary"):
        return

    try:
        with st.spinner(f"Fetching telemetry from {kind}..."):
            readings = connector.fetch()
    except ConnectorError as ex:
        st.error(str(ex))
        return

    if not readings:
        st.warning("The connector returned no readings.")
        return

    df = pd.DataFrame(readings)

    st.success(
        f"Fetched {len(df)} readings from "
        f"{df['rack'].nunique()} rack(s) via {kind}."
    )

    if store_history:
        saved = record_readings(readings)
        st.caption(f"💾 {saved} readings saved to telemetry history.")

    st.dataframe(df, use_container_width=True, hide_index=True)

    numeric_columns = [
        column
        for column in ("temperature", "power_kw", "humidity")
        if column in df.columns
    ]

    if numeric_columns and "timestamp" in df.columns:

        st.subheader("Readings by Rack")

        for column in numeric_columns:

            chart_df = df.pivot_table(
                index="timestamp",
                columns="rack",
                values=column,
                aggfunc="mean",
            )

            st.write(f"### {column.replace('_', ' ').title()}")
            st.line_chart(chart_df)

    st.divider()

    st.subheader("🤖 AI Infrastructure Assessment")

    summary = parse_sensor_data(df)

    with st.spinner("Coordinator Agent analyzing live telemetry..."):
        report = coordinate_sensor_workflow(summary)

    st.markdown(report)
