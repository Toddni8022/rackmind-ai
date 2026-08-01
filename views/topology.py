import pandas as pd
import streamlit as st

from config import APP_NAME, APP_VERSION, SAMPLE_DIR, TEMP_CRITICAL, TEMP_WARNING


def show_topology():

    st.header("🖥️ Infrastructure Topology")

    st.caption("Current Data Center Infrastructure Status")

    csv_path = SAMPLE_DIR / "sensors" / "rack22.csv"

    rack22 = "🟢 Healthy"

    if csv_path.exists():

        df = pd.read_csv(csv_path)

        df.columns = (
            df.columns
            .str.strip()
            .str.lower()
        )

        if "temperature" in df.columns:

            max_temp = df["temperature"].max()

            if max_temp >= TEMP_CRITICAL:
                rack22 = "🔴 Critical"

            elif max_temp >= TEMP_WARNING:
                rack22 = "🟡 Warning"

    topology = pd.DataFrame(
        {
            "Device": [
                "Rack 22",
                "Rack 23",
                "Rack 24",
                "Core Switch",
                "Access Switch",
                "Firewall",
                "UPS",
                "CRAC Unit",
                "Storage Array",
            ],
            "Status": [
                rack22,
                "🟢 Healthy",
                "🟢 Healthy",
                "🟢 Healthy",
                "🟡 CRC Errors",
                "🟢 Healthy",
                "🟢 Healthy",
                "🟡 Cooling Warning",
                "🟢 Healthy",
            ],
        }
    )

    st.dataframe(
        topology,
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    col1, col2, col3 = st.columns(3)

    col1.metric("Racks", "3")
    col2.metric("Network Devices", "3")
    col3.metric("Critical Alerts", "1")

    st.divider()

    st.subheader("AI Assessment")

    st.info(
        f"""
**Rack 22:** {rack22}

• Network core is operating normally.

• Access switch is reporting CRC errors.

• Cooling system should be inspected due to elevated temperatures.

• Overall infrastructure remains operational.
"""
    )

    st.divider()

    st.caption(f"{APP_NAME} v{APP_VERSION} | Infrastructure Topology")
