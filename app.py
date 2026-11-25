import streamlit as st
from utils.branding import asset_path, nav_logo_html

st.set_page_config(
    page_title="Finova – Smart Finance Tracker",
    page_icon=asset_path("favicon.png"),
    layout="wide",
    initial_sidebar_state="collapsed"
)

from utils.db import db
from utils.styles import apply_custom_css
from modules.auth import render_auth_page, logout_user
from modules.dashboard import render_dashboard_page
from modules.transactions import render_transactions_page
from modules.budget import render_budget_page
from modules.assistant import render_assistant_page
from modules.insights import render_insights_page
from modules.profile import render_profile_page


def sync_google_user():
    """Create/load the local Finova profile after a successful Google OIDC login."""
    try:
        google_user = st.user
        if not getattr(google_user, "is_logged_in", False):
            return
        email = getattr(google_user, "email", None)
        name = getattr(google_user, "name", None) or (email.split("@")[0] if email else "Google User")
        if not email:
            st.error("Google did not provide an email address. Please try again.")
            return
        user = db.get_user_by_email(email)
        if user is None:
            user = db.add_user(name, email, "")
        st.session_state["logged_in"] = True
        st.session_state["user_id"] = user["user_id"]
        st.session_state["user_name"] = user.get("name", name)
        st.session_state["user_email"] = user.get("email", email)
    except Exception:
        # Streamlit versions/configurations without OIDC should continue to support local login.
        return


def render_intro_page():
    """Public landing page shown before authentication."""
    left, right = st.columns([1.1, 1], gap="large")
    with left:
        st.markdown(nav_logo_html(84), unsafe_allow_html=True)
        st.markdown(
            """
            <div class="intro-copy">
              <div class="intro-eyebrow">SMARTER MONEY. BETTER DECISIONS.</div>
              <h1>Take control of<br><span>your finances.</span></h1>
              <p>Track your income, understand your spending, plan your budgets
              and get intelligent financial insights — all in one place.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Get Started  →", type="primary", use_container_width=False):
            st.session_state["show_auth"] = True
            st.rerun()
        st.caption("A smarter way to manage your everyday money.")
    with right:
        st.markdown(
            """
            <div class="intro-preview">
              <div class="preview-top"><span>FINOVA OVERVIEW</span><span class="live-pill">● LIVE</span></div>
              <div class="preview-label">Total balance</div>
              <div class="preview-amount">₹ 84,500.00</div>
              <div class="preview-change">↗ 12.8% <span>compared to last month</span></div>
              <div class="preview-stats">
                <div><small>INCOME</small><strong>₹ 1,20,000</strong></div>
                <div><small>EXPENSES</small><strong>₹ 35,500</strong></div>
              </div>
              <div class="preview-chart">
                <div style="height:35%"></div><div style="height:52%"></div>
                <div style="height:44%"></div><div style="height:72%"></div>
                <div style="height:60%"></div><div style="height:88%"></div>
                <div style="height:76%"></div>
              </div>
              <div class="preview-foot">Your money, made clear.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div class='intro-section-title'>Everything you need to manage money</div>", unsafe_allow_html=True)
    f1, f2, f3 = st.columns(3)
    features = [
        ("📊", "Smart Dashboard", "See your income, expenses, savings and spending trends."),
        ("🎯", "Budget Planning", "Set monthly limits and stay aware of your spending."),
        ("✨", "AI-Powered Insights", "Get helpful answers and predictions with AI and ML."),
    ]
    for col, (emoji, title, desc) in zip([f1, f2, f3], features):
        with col:
            st.markdown(
                f"<div class='feature-card'><div class='feature-icon'>{emoji}</div>"
                f"<h3>{title}</h3><p>{desc}</p></div>",
                unsafe_allow_html=True,
            )
    st.markdown("<div class='intro-footer'>FINOVA · SMART PERSONAL FINANCE TRACKER</div>", unsafe_allow_html=True)


def main():
    apply_custom_css()
    for key, default in {
        "logged_in": False, "user_id": None, "user_name": None,
        "user_email": None, "show_auth": False
    }.items():
        if key not in st.session_state:
            st.session_state[key] = default

    sync_google_user()

    if not st.session_state["logged_in"]:
        if st.session_state.get("show_auth", False):
            if st.button("← Back to introduction"):
                st.session_state["show_auth"] = False
                st.rerun()
            render_auth_page()
        else:
            render_intro_page()
        return

    # Top navigation bar
    nav_items = {
        "Dashboard": "📊",
        "Transactions": "💳",
        "Budget": "🎯",
        "AI Assistant": "✨",
        "Insights": "💡",
        "Profile": "👤",
    }
    user_name = st.session_state.get("user_name") or "User"
    initial = user_name.strip()[:1].upper() or "U"

    with st.container(key="topnav"):
        nav_logo, nav_menu, nav_user, nav_out = st.columns(
            [1.55, 5.6, 0.45, 1.0], vertical_alignment="center", gap="small"
        )
        with nav_logo:
            st.markdown(nav_logo_html(64, "white"), unsafe_allow_html=True)
        with nav_menu:
            page = st.radio(
                "Main navigation",
                list(nav_items.keys()),
                format_func=lambda name: f"{nav_items[name]}  {name}",
                horizontal=True,
                label_visibility="collapsed",
                key="main_navigation",
            )
        with nav_user:
            st.markdown(
                f"<div class='nav-avatar' title='{user_name}'>{initial}</div>",
                unsafe_allow_html=True,
            )
        with nav_out:
            if st.button("Log out", use_container_width=True):
                try:
                    if getattr(st.user, "is_logged_in", False):
                        st.logout()
                except Exception:
                    pass
                logout_user()

    st.markdown("<div class='nav-spacer'></div>", unsafe_allow_html=True)
    user_id = st.session_state.get("user_id", "")

    if page == "Dashboard":
        render_dashboard_page(user_id)
    elif page == "Transactions":
        render_transactions_page(user_id)
    elif page == "Budget":
        render_budget_page(user_id)
    elif page == "AI Assistant":
        render_assistant_page(user_id)
    elif page == "Insights":
        render_insights_page(user_id)
    elif page == "Profile":
        render_profile_page(user_id)


if __name__ == "__main__":
    main()
