import streamlit as st


def show_logs():

    st.header("📜 Log Agent")

    st.success("Ready")

    logfile = st.file_uploader(
        "Upload switch.log",
        type=["log", "txt"]
    )

    if logfile:

        st.success(logfile.name)

        st.info(
            "Log Agent integration coming next step."
        )