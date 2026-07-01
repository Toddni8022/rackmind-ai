import pandas as pd
import streamlit as st

from services.auth_service import (
    ROLES,
    change_password,
    create_user,
    delete_user,
    list_users,
    set_role,
)


def show_admin(user=None):

    st.header("🔐 User Administration")
    st.caption("Manage team accounts and roles (admin only)")

    users = list_users()

    st.subheader("Team Accounts")

    st.dataframe(
        pd.DataFrame(
            [
                {
                    "Username": account["username"],
                    "Role": account["role"],
                    "Created": account["created_at"],
                    "Last Login": account["last_login"] or "Never",
                }
                for account in users
            ]
        ),
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    col_add, col_manage = st.columns(2)

    with col_add:

        st.subheader("➕ Add User")

        with st.form("add_user", clear_on_submit=True):

            new_username = st.text_input("Username")
            new_password = st.text_input("Password", type="password")
            new_role = st.selectbox("Role", ROLES, index=0)

            if st.form_submit_button("Create User", type="primary"):

                try:
                    create_user(new_username, new_password, new_role)
                    st.success(f"User '{new_username}' created.")
                    st.rerun()
                except ValueError as ex:
                    st.error(str(ex))

    with col_manage:

        st.subheader("🛠️ Manage User")

        usernames = [account["username"] for account in users]

        target = st.selectbox("User", usernames)

        new_role = st.selectbox(
            "Change role to",
            ROLES,
            index=ROLES.index(
                next(
                    account["role"]
                    for account in users
                    if account["username"] == target
                )
            ),
            key="manage_role",
        )

        if st.button("Update Role"):

            try:
                set_role(target, new_role)
                st.success(f"'{target}' is now {new_role}.")
                st.rerun()
            except ValueError as ex:
                st.error(str(ex))

        reset_password = st.text_input(
            "New password",
            type="password",
            key="manage_password",
        )

        if st.button("Reset Password"):

            try:
                change_password(target, reset_password)
                st.success(f"Password updated for '{target}'.")
            except ValueError as ex:
                st.error(str(ex))

        st.divider()

        if st.button("🗑️ Delete User", type="secondary"):

            if user and target == user.get("username"):
                st.error("You cannot delete your own account.")
            else:
                try:
                    delete_user(target)
                    st.success(f"User '{target}' deleted.")
                    st.rerun()
                except ValueError as ex:
                    st.error(str(ex))
