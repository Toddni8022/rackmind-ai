import streamlit as st


def show_dashboard():

    st.header("🏠 Dashboard")
    st.caption("Autonomous Network Operations Copilot")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("🟢 Healthy", "124")
    c2.metric("🟡 Warning", "3")
    c3.metric("🔴 Critical", "1")
    c4.metric("🤖 Agents", "5")

    st.divider()

    left, right = st.columns(2)

    with left:

        st.subheader("Agent Status")

        st.success("🟢 Coordinator Agent")

        st.success("🟢 Log Agent")

        st.success("🟢 Runbook Agent")

        st.success("🟢 Sensor Agent")

        st.success("🟢 Report Agent")

    with right:

        st.subheader("Capabilities")

        st.write("✅ Infrastructure Log Analysis")

        st.write("✅ Runbook Search")

        st.write("✅ Sensor Analytics")

        st.write("✅ Executive Incident Reports")

        st.write("🚧 Google ADK Integration")

    st.divider()

    st.subheader("Architecture")

    st.code(
        """
User
 │
 ▼
Coordinator Agent
 │
 ├── Log Agent
 ├── Runbook Agent
 ├── Sensor Agent
 └── Report Agent
 │
 ▼
Executive Incident Report
"""
    )

    st.divider()

    st.info(
        """
RackMind AI is a multi-agent Network Operations Copilot designed
to assist infrastructure engineers with incident response,
documentation search, sensor analytics, and executive reporting.
"""
    )