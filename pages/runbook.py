import streamlit as st

from adk.chat import ask


def show_runbook():

    st.header("📄 Runbook Agent")

    question = st.text_input(
        "Ask an infrastructure question"
    )

    if st.button("Ask AI"):

        if not question:

            st.warning(
                "Please enter a question."
            )

            return

        with st.spinner(
            "Google ADK is reasoning..."
        ):

            response = ask(question)

        st.success("Answer")

        st.markdown(response)
