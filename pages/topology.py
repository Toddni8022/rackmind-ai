import streamlit as st
import pandas as pd
from pathlib import Path


def show_topology():

    st.header("🖥️ Infrastructure Topology")

    st.caption("Current Data Center Infrastructure Status")

    csv_path = Path("sample_data/sensors/rack22.csv")

    rack22 = "🟢 Healthy"

    if csv_path.exists():

        df = pd.read_csv(csv_path)

        # Normalize column names
        df.columns = (
            df.columns
            .str.strip()
            .str.lower()
        )

        max_temp = df["temperature"].max()

        if max_temp >= 90:
            rack22 = "🔴 Critical"

        elif max_temp >= 80:
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
        width="stretch",
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

    st.caption("RackMind AI v1.0 | Infrastructure Topology")
