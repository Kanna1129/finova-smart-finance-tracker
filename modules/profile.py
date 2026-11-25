import streamlit as st
from utils.db import db
from modules.auth import verify_password, hash_password
from utils.styles import render_header

def render_profile_page(user_id: str):
    """Renders User Profile, Password Change, and Demo Data Loader."""
    render_header("User Profile & Settings", "Manage account details, password, and load presentation demo data.")

    user = db.get_user_by_email(st.session_state.get("user_email", ""))

    c1, c2 = st.columns([1, 1])

    # Column 1: Account Information & Demo Data
    with c1:
        with st.container(border=True):
            st.markdown("<h3 style='font-size: 1.15rem; font-weight: 700; color: #1E293B; margin-bottom: 1rem;'>👤 Account Information</h3>", unsafe_allow_html=True)
            if user:
                st.write(f"**Name:** {user.get('name', 'N/A')}")
                st.write(f"**Email:** {user.get('email', 'N/A')}")
                st.write(f"**User ID:** `{user.get('user_id', 'N/A')}`")
                st.write(f"**Account Created:** {user.get('created_at', 'N/A')}")

            st.markdown("---")
            st.markdown("<h3 style='font-size: 1.15rem; font-weight: 700; color: #1E293B; margin-bottom: 0.5rem;'>🚀 Presentation Demo Setup</h3>", unsafe_allow_html=True)
            st.caption("Clicking below will insert ~40 realistic income and expense transactions for your account across the past 3 months.")

            if st.button("✨ Load Demo Data (~40 Sample Transactions)", type="primary", use_container_width=True):
                with st.spinner("Generating sample transactions..."):
                    count = db.load_demo_data(user_id)
                    st.toast(f"Successfully loaded {count} sample transactions!", icon="🎉")
                    st.rerun()

    # Column 2: Change Password
    with c2:
        with st.container(border=True):
            st.markdown("<h3 style='font-size: 1.15rem; font-weight: 700; color: #1E293B; margin-bottom: 1rem;'>🔐 Change Password</h3>", unsafe_allow_html=True)

            with st.form("change_pwd_form", clear_on_submit=True):
                current_pwd = st.text_input("Current Password", type="password")
                new_pwd = st.text_input("New Password (min 6 chars)", type="password")
                confirm_pwd = st.text_input("Confirm New Password", type="password")
                submitted = st.form_submit_button("Update Password", use_container_width=True)

                if submitted:
                    if not current_pwd or not new_pwd or not confirm_pwd:
                        st.error("Please fill in all fields.")
                    elif not user or not verify_password(current_pwd, user["password_hash"]):
                        st.error("Incorrect current password.")
                    elif len(new_pwd) < 6:
                        st.error("New password must be at least 6 characters.")
                    elif new_pwd != confirm_pwd:
                        st.error("New passwords do not match.")
                    else:
                        new_hash = hash_password(new_pwd)
                        db.update_user_password(user_id, new_hash)
                        st.toast("Password updated successfully!", icon="✅")
