import streamlit as st


def show_dashboard():

    st.header("🏠 Dashboard")
    st.caption("Autonomous Network Operations Center")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "🟢 Healthy",
        "124"
    )

    col2.metric(
        "🟡 Warning",
        "3"
    )

    col3.metric(
        "🔴 Critical",
        "1"
    )

    col4.metric(
        "🤖 Agents",
        "4"
    )

    st.divider()

    left, right = st.columns(2)

    with left:

        st.subheader("Agent Status")

        st.success("🟢 Coordinator Agent")

        st.success("🟢 Runbook Agent")

        st.success("🟢 Log Agent")

        st.info("⚪ Sensor Agent (Next Sprint)")

    with right:

        st.subheader("Recent Activity")

        st.write("✅ switch.log analyzed")

        st.write("✅ AI incident report generated")

        st.write("✅ Runbook uploaded")

        st.write("✅ Infrastructure summary created")

    st.divider()

    st.subheader("About RackMind AI")

    st.write(
        """
RackMind AI is an autonomous Network Operations Copilot that uses
specialized AI agents to analyze infrastructure logs, search
technical runbooks, monitor sensor data, and generate executive
incident reports.

Current Version: **0.5**
"""
    )