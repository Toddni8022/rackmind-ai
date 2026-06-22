import streamlit as st


def show_dashboard():

    st.header("🏠 Dashboard")
    st.caption("Autonomous Network Operations Center")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("🟢 Healthy", "124")
    c2.metric("🟡 Warning", "3")
    c3.metric("🔴 Critical", "1")
    c4.metric("🤖 Agents", "4")

    st.divider()

    left, right = st.columns(2)

    with left:

        st.subheader("Agent Status")

        st.success("🟢 Coordinator Agent Online")

        st.success("🟢 Runbook Agent Online")

        st.success("🟢 Log Agent Online")

        st.success("🟢 Sensor Agent Online")

    with right:

        st.subheader("Recent Activity")

        st.write("✅ Log analysis available")

        st.write("✅ Runbook search available")

        st.write("✅ Sensor analytics available")

        st.write("🚧 Google ADK orchestration in progress")

    st.divider()

    st.subheader("RackMind AI")

    st.info(
        """
Autonomous Network Operations Copilot

Features

• AI Log Analysis

• Runbook Search

• Sensor Analytics

• Executive Incident Reports

Version 0.6
"""
    )