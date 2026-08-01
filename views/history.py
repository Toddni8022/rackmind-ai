import streamlit as st

from services.incident_history import load_incident_history, search_incident_history


def show_history():

    st.header("🗂️ Historical Incidents")
    st.caption("Search past resolved incidents by rack, symptom, or resolution")

    records = load_incident_history()

    if not records:
        st.info("No historical incident records found.")
        return

    query = st.text_input(
        "Search historical incidents (e.g. CRC, temperature, Rack22)"
    )

    results = search_incident_history(query, records) if query else records

    st.caption(f"{len(results)} of {len(records)} incidents shown")

    if not results:
        st.warning("No historical incidents match that search.")
        return

    for record in results:

        title = f"{record['id']} — {record['rack'] or 'Unknown rack'} ({record['status'] or 'Unknown status'})"

        with st.expander(title):

            st.markdown("**Symptoms**")

            for symptom in record["symptoms"]:
                st.markdown(f"- {symptom}")

            st.markdown("**Resolution**")

            for step in record["resolution"]:
                st.markdown(f"- {step}")
