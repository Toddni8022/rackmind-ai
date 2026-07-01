import pandas as pd
import streamlit as st

from services.auth_service import has_role
from services.incident_archive import (
    SEVERITIES,
    delete_incident,
    search_incidents,
    seed_sample_incidents,
)


def show_history(user=None):

    st.header("🗂️ Historical Incident Search")
    st.caption("Search past incidents by rack, severity, time, root cause, and fix")

    seeded = seed_sample_incidents()

    if seeded:
        st.info(f"Loaded {seeded} sample incidents into the archive.")

    with st.expander("🔍 Filters", expanded=True):

        c1, c2, c3 = st.columns(3)

        rack = c1.text_input("Rack", placeholder="Rack-22")

        severity = c2.selectbox(
            "Severity",
            ("Any",) + SEVERITIES,
        )

        text = c3.text_input(
            "Report contains",
            placeholder="CRC, cooling, uplink...",
        )

        c4, c5 = st.columns(2)

        root_cause = c4.text_input(
            "Root cause contains",
            placeholder="cooling",
        )

        fix = c5.text_input(
            "Recommended fix contains",
            placeholder="HVAC",
        )

        c6, c7 = st.columns(2)

        start_date = c6.date_input("From", value=None)
        end_date = c7.date_input("To", value=None)

    results = search_incidents(
        rack=rack or None,
        severity=None if severity == "Any" else severity,
        start=f"{start_date} 00:00:00" if start_date else None,
        end=f"{end_date} 23:59:59" if end_date else None,
        root_cause_contains=root_cause or None,
        fix_contains=fix or None,
        text=text or None,
    )

    st.divider()

    st.subheader(f"Results ({len(results)})")

    if not results:
        st.info("No incidents match these filters.")
        return

    table = pd.DataFrame(
        [
            {
                "ID": row["id"],
                "Time": row["created_at"],
                "Rack": row["rack"],
                "Severity": row["severity"],
                "Root Cause": (row["root_cause"] or "")[:80],
                "Recommended Fix": (row["recommended_fix"] or "")[:80],
                "Source": row["source"],
            }
            for row in results
        ]
    )

    st.dataframe(table, use_container_width=True, hide_index=True)

    st.download_button(
        "⬇️ Export results as CSV",
        table.to_csv(index=False).encode("utf-8"),
        file_name="incident_history.csv",
        mime="text/csv",
    )

    st.divider()

    st.subheader("Incident Detail")

    selected_id = st.selectbox(
        "Select an incident",
        [row["id"] for row in results],
        format_func=lambda incident_id: next(
            f"#{row['id']} | {row['created_at']} | {row['rack']} | {row['severity']}"
            for row in results
            if row["id"] == incident_id
        ),
    )

    incident = next(row for row in results if row["id"] == selected_id)

    badge = {
        "Critical": "🔴",
        "High": "🟠",
        "Medium": "🟡",
        "Low": "🟢",
    }.get(incident["severity"], "⚪")

    st.markdown(
        f"{badge} **{incident['severity']}** | "
        f"**{incident['rack']}** | {incident['created_at']}"
    )

    if incident["root_cause"]:
        st.markdown(f"**Root Cause:** {incident['root_cause']}")

    if incident["recommended_fix"]:
        st.markdown(f"**Recommended Fix:** {incident['recommended_fix']}")

    with st.expander("Full Report", expanded=False):
        st.markdown(incident["report"] or "_No report text stored._")

    if has_role(user, "manager"):

        if st.button("🗑️ Delete this incident", key=f"delete_{selected_id}"):
            delete_incident(selected_id)
            st.success(f"Incident #{selected_id} deleted.")
            st.rerun()

    else:
        st.caption("Manager role is required to delete incidents.")
