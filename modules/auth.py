import re
import hashlib
import streamlit as st
from utils.db import db
from utils.branding import asset_data_uri

def hash_password(password: str) -> str:
    """Hashes password securely using bcrypt or SHA-256 fallback."""
    try:
        import bcrypt
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")
    except Exception:
        salt = "finova_mca_salt_2026"
        return hashlib.sha256((password + salt).encode("utf-8")).hexdigest()

def verify_password(password: str, password_hash: str) -> bool:
    """Verifies plain password against stored hash."""
    try:
        import bcrypt
        if password_hash.startswith("$2b$") or password_hash.startswith("$2a$"):
            return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except Exception:
        pass
    
    salt = "finova_mca_salt_2026"
    expected = hashlib.sha256((password + salt).encode("utf-8")).hexdigest()
    return expected == password_hash

def validate_email(email: str) -> bool:
    """Validates email format using regex."""
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(pattern, email.strip()))

def render_auth_page():
    """Renders centered, modern fintech styled Login and Register interface."""
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2.2, 1])

    with col2:
        st.markdown(
            f"""
            <div style="text-align: center; margin-bottom: 2rem;">
                <img src="{asset_data_uri('logo_icon.svg')}" alt="Finova logo" style="width: 76px; height: 76px; margin-bottom: 0.8rem;">
                <h1 style="color: #0F172A; font-size: 2.8rem; font-weight: 800; margin: 0; letter-spacing: -0.8px;">Finova</h1>
                <p style="color: #64748B; font-size: 1.05rem; font-weight: 500; margin-top: 0.4rem;">Smart Personal Finance Tracker with Machine Learning & Gemini AI</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        with st.container(border=True):
            tab_login, tab_register = st.tabs(["🔐 Sign In", "📝 Create Account"])

        with tab_login:
            st.markdown("<h3 style='font-size: 1.3rem; font-weight: 700; color: #1E293B; margin-top: 0.5rem;'>Welcome Back</h3>", unsafe_allow_html=True)
            st.caption("Sign in to access your financial dashboard, ML forecasts, and AI assistant.")

            with st.form("login_form", clear_on_submit=False):
                email = st.text_input("Email Address", placeholder="user@example.com")
                password = st.text_input("Password", type="password", placeholder="••••••••")
                submitted = st.form_submit_button("Sign In to Finova ➔", use_container_width=True, type="primary")

                if submitted:
                    if not email or not password:
                        st.error("Please enter both email address and password.")
                    else:
                        user = db.get_user_by_email(email)
                        if user and verify_password(password, user["password_hash"]):
                            st.session_state["logged_in"] = True
                            st.session_state["user_id"] = user["user_id"]
                            st.session_state["user_name"] = user["name"]
                            st.session_state["user_email"] = user["email"]
                            st.toast(f"Welcome back, {user['name']}!", icon="🎉")
                            st.rerun()
                        else:
                            st.error("Invalid email address or password.")

            st.markdown("<div class='or-divider'><span>OR</span></div>", unsafe_allow_html=True)
            if st.button("🌐  Continue with Google", use_container_width=True, key="google_sign_in"):
                try:
                    st.login("google")
                except Exception:
                    st.error(
                        "Google sign-in is not configured yet. Add the Google OAuth settings "
                        "to .streamlit/secrets.toml and restart the app."
                    )

        with tab_register:
            st.markdown("<h3 style='font-size: 1.3rem; font-weight: 700; color: #1E293B; margin-top: 0.5rem;'>Join Finova</h3>", unsafe_allow_html=True)
            st.caption("Set up your account to start tracking, budgeting, and optimizing your money.")

            with st.form("register_form", clear_on_submit=False):
                name = st.text_input("Full Name", placeholder="e.g. Alex Johnson")
                email = st.text_input("Email Address", placeholder="user@example.com")
                password = st.text_input("Password (min 6 characters)", type="password", placeholder="••••••••")
                confirm_password = st.text_input("Confirm Password", type="password", placeholder="••••••••")
                submitted = st.form_submit_button("Create My Account ➔", use_container_width=True, type="primary")

                if submitted:
                    if not name or not email or not password or not confirm_password:
                        st.error("Please fill in all required fields.")
                    elif not validate_email(email):
                        st.error("Please enter a valid email address.")
                    elif len(password) < 6:
                        st.error("Password must be at least 6 characters long.")
                    elif password != confirm_password:
                        st.error("Passwords do not match.")
                    else:
                        existing_user = db.get_user_by_email(email)
                        if existing_user:
                            st.error("An account with this email already exists. Please sign in.")
                        else:
                            pwd_hash = hash_password(password)
                            new_user = db.add_user(name, email, pwd_hash)
                            st.session_state["logged_in"] = True
                            st.session_state["user_id"] = new_user["user_id"]
                            st.session_state["user_name"] = new_user["name"]
                            st.session_state["user_email"] = new_user["email"]
                            st.toast("Account created successfully!", icon="✅")
                            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

def logout_user():
    """Logs out current user and resets session state."""
    st.session_state["logged_in"] = False
    st.session_state["user_id"] = None
    st.session_state["user_name"] = None
    st.session_state["user_email"] = None
    st.rerun()
