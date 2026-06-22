import streamlit as st


def show_dashboard():

    st.header("🏠 Dashboard")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Healthy", "124")

    with col2:
        st.metric("Warnings", "3")

    with col3:
        st.metric("Critical", "1")

    with col4:
        st.metric("Agents", "4")

    st.divider()

    st.subheader("Agent Status")

    st.success("🟢 Coordinator Agent")

    st.success("🟢 Runbook Agent")

    st.success("🟢 Log Agent")

    st.info("⚪ Sensor Agent (Coming Soon)")

    st.divider()

    st.subheader("Recent Alerts")

    st.warning("Rack22 CRC Errors")

    st.warning("Temperature Spike Detected")

    st.warning("Cooling Efficiency Degraded")