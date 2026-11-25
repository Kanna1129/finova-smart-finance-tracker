import streamlit as st

def apply_custom_css():
    """Applies comprehensive modern fintech CSS styling across Finova."""
    custom_css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Main container layout */
    .block-container {
        padding-top: 4rem !important;
        padding-bottom: 3rem !important;
        max-width: 1350px !important;
    }

    /* Background tone */
    .stApp {
        background-color: #F6F7FC;
    }

    /* Hero Banner Header */
    .finova-header {
        background: linear-gradient(135deg, #22C7B8 0%, #6D5CE8 50%, #5145CD 100%);
        padding: 1.8rem 2.2rem;
        border-radius: 16px;
        color: white;
        margin-bottom: 1.8rem;
        box-shadow: 0 12px 30px -8px rgba(5, 150, 105, 0.35);
        position: relative;
        overflow: hidden;
    }

    .finova-header::after {
        content: "";
        position: absolute;
        top: -50%;
        right: -10%;
        width: 300px;
        height: 300px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 50%;
        pointer-events: none;
    }

    .finova-header h1 {
        color: #FFFFFF !important;
        font-weight: 800;
        font-size: 2.2rem;
        margin: 0;
        letter-spacing: -0.5px;
    }

    .finova-header p {
        color: #DDD6FE !important;
        font-size: 1.05rem;
        margin-top: 0.4rem;
        margin-bottom: 0;
        font-weight: 500;
    }

    /* Native Bordered Container -> Styled Fintech Card */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #FFFFFF !important;
        border-radius: 16px !important;
        border: 1px solid #E2E8F0 !important;
        padding: 1.5rem !important;
        box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.03), 0 2px 6px -1px rgba(0, 0, 0, 0.02) !important;
        margin-bottom: 1.5rem !important;
        transition: transform 0.2s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.2s ease !important;
    }

    [data-testid="stVerticalBlockBorderWrapper"]:hover {
        box-shadow: 0 10px 25px -3px rgba(0, 0, 0, 0.06), 0 4px 10px -2px rgba(0, 0, 0, 0.03) !important;
    }

    /* Form Container styling */
    [data-testid="stForm"] {
        border: 1px solid #F1F5F9 !important;
        border-radius: 12px !important;
        padding: 1.2rem !important;
        background-color: #FAFAFA !important;
    }

    /* Metric KPI Cards */
    .kpi-card-v2 {
        background: #FFFFFF;
        border-radius: 16px;
        padding: 1.3rem 1.5rem;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 15px -3px rgba(0, 0, 0, 0.04);
        position: relative;
        overflow: hidden;
        transition: all 0.25s ease;
    }

    .kpi-card-v2:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 25px -5px rgba(0, 0, 0, 0.08);
    }

    .kpi-card-v2.income { border-top: 4px solid #3B82F6; }
    .kpi-card-v2.expense { border-top: 4px solid #EF4444; }
    .kpi-card-v2.balance { border-top: 4px solid #6D5CE8; }
    .kpi-card-v2.savings { border-top: 4px solid #22C7B8; }

    .kpi-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.6rem;
    }

    .kpi-title {
        font-size: 0.85rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        color: #68738F;
    }

    .kpi-icon {
        font-size: 1.4rem;
        padding: 0.4rem 0.6rem;
        border-radius: 10px;
    }

    .kpi-icon.income { background: #DBEAFE; color: #1D4ED8; }
    .kpi-icon.expense { background: #FEF2F2; color: #EF4444; }
    .kpi-icon.balance { background: #F1EEFF; color: #6D5CE8; }
    .kpi-icon.savings { background: #E9FBF8; color: #22C7B8; }

    .kpi-amount {
        font-size: 1.85rem;
        font-weight: 800;
        color: #111A35;
        letter-spacing: -0.5px;
    }

    .kpi-amount.income { color: #1D4ED8; }
    .kpi-amount.expense { color: #DC2626; }
    .kpi-amount.balance { color: #5145CD; }
    .kpi-amount.savings { color: #22C7B8; }

    /* Custom Streamlit Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background-color: #F1F5F9;
        padding: 0.4rem;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
    }

    .stTabs [data-baseweb="tab"] {
        height: 42px;
        white-space: pre;
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.92rem;
        color: #68738F;
        padding: 0 1.2rem;
        border: none !important;
        background-color: transparent;
    }

    .stTabs [aria-selected="true"] {
        background-color: #FFFFFF !important;
        color: #6D5CE8 !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08) !important;
    }

    /* Custom Buttons Styling */
    .stButton button {
        border-radius: 10px !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        padding: 0.55rem 1.4rem !important;
        transition: all 0.2s ease !important;
    }

    .stButton button[kind="primary"] {
        background: linear-gradient(135deg, #6D5CE8 0%, #8B7CF6 100%) !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(5, 150, 105, 0.25) !important;
    }

    .stButton button[kind="primary"]:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 16px rgba(5, 150, 105, 0.35) !important;
    }

    /* Budget alert boxes */
    .budget-warning {
        background-color: #FFFBEB;
        color: #B45309;
        padding: 0.75rem 1.2rem;
        border-radius: 10px;
        font-weight: 600;
        font-size: 0.9rem;
        margin-top: 0.6rem;
        border-left: 4px solid #F59E0B;
        box-shadow: 0 2px 6px rgba(245, 158, 11, 0.1);
    }

    .budget-exceeded {
        background-color: #FEF2F2;
        color: #991B1B;
        padding: 0.75rem 1.2rem;
        border-radius: 10px;
        font-weight: 600;
        font-size: 0.9rem;
        margin-top: 0.6rem;
        border-left: 4px solid #EF4444;
        box-shadow: 0 2px 6px rgba(239, 68, 68, 0.1);
    }

    /* SIDEBAR & NAVIGATION STYLING */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E2E8F0 !important;
    }

    [data-testid="stSidebar"] [data-testid="stSidebarNav"] {
        padding-top: 0.5rem;
    }

    .user-profile-banner {
        background: linear-gradient(135deg, #F1EEFF 0%, #E9FBF8 100%);
        border: 1px solid #DDD6FE;
        border-radius: 14px;
        padding: 1rem;
        display: flex;
        align-items: center;
        gap: 0.85rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 4px 12px rgba(5, 150, 105, 0.05);
    }

    .user-avatar-circle {
        width: 44px;
        height: 44px;
        border-radius: 12px;
        background: linear-gradient(135deg, #6D5CE8 0%, #22C7B8 100%);
        color: #FFFFFF;
        font-weight: 800;
        font-size: 1.15rem;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 10px rgba(5, 150, 105, 0.3);
        flex-shrink: 0;
    }

    .user-details {
        overflow: hidden;
    }

    .user-name-title {
        font-size: 0.95rem;
        font-weight: 700;
        color: #111A35;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        margin: 0;
    }

    .user-status-tag {
        font-size: 0.75rem;
        font-weight: 600;
        color: #8B7CF6;
        display: flex;
        align-items: center;
        gap: 0.3rem;
        margin-top: 0.15rem;
    }

    .online-dot {
        width: 7px;
        height: 7px;
        background-color: #8B7CF6;
        border-radius: 50%;
        display: inline-block;
        box-shadow: 0 0 8px #8B7CF6;
    }

    .nav-section-label {
        font-size: 0.72rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #94A3B8;
        margin: 1.2rem 0 0.5rem 0.4rem;
    }

    [data-testid="stSidebar"] div[role="radiogroup"] {
        gap: 0.45rem !important;
    }

    [data-testid="stSidebar"] div[role="radiogroup"] label {
        background-color: #F6F7FC !important;
        border: 1px solid #F1F5F9 !important;
        border-radius: 12px !important;
        padding: 0.7rem 1.1rem !important;
        margin-bottom: 0.2rem !important;
        cursor: pointer !important;
        transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1) !important;
        display: flex !important;
        align-items: center !important;
        position: relative !important;
    }

    [data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child {
        display: none !important;
    }

    [data-testid="stSidebar"] div[role="radiogroup"] label p {
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        color: #475569 !important;
        margin: 0 !important;
        transition: color 0.2s ease !important;
    }

    [data-testid="stSidebar"] div[role="radiogroup"] label:hover {
        background-color: #F1EEFF !important;
        border-color: #C4B5FD !important;
        transform: translateX(4px) !important;
    }

    [data-testid="stSidebar"] div[role="radiogroup"] label:hover p {
        color: #6D5CE8 !important;
    }

    [data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked),
    [data-testid="stSidebar"] div[role="radiogroup"] label[aria-checked="true"] {
        background: linear-gradient(135deg, #6D5CE8 0%, #8B7CF6 100%) !important;
        border-color: #6D5CE8 !important;
        box-shadow: 0 6px 18px rgba(5, 150, 105, 0.28) !important;
        transform: translateX(4px) !important;
    }

    [data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p,
    [data-testid="stSidebar"] div[role="radiogroup"] label[aria-checked="true"] p {
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }

    .univ-footer {
        background: #F6F7FC;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 1.1rem;
        text-align: center;
        margin-top: 1.8rem;
    }

    .univ-footer strong {
        color: #1B2545;
        font-size: 0.88rem;
        display: block;
        margin-bottom: 0.2rem;
    }

    .univ-footer p {
        color: #68738F;
        font-size: 0.78rem;
        margin: 0.15rem 0;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Finova landing page and top navigation */
    .intro-copy { padding: 2.4rem 0 1.3rem; }
    .intro-eyebrow { color:#6D5CE8; font-size:.76rem; font-weight:800; letter-spacing:2px; margin-bottom:1rem; }
    .intro-copy h1 { color:#111A35; font-size:3.25rem; line-height:1.08; letter-spacing:-1.8px; font-weight:800; margin:0 0 1.1rem; }
    .intro-copy h1 span { color:#6D5CE8; }
    .intro-copy p { color:#68738F; font-size:1.08rem; line-height:1.8; max-width:540px; margin-bottom:1.5rem; }
    .intro-preview { background:linear-gradient(145deg,#17213D,#28365D); color:white; border-radius:24px; padding:2rem; min-height:365px; box-shadow:0 22px 55px rgba(23,33,61,.18); margin:1.3rem 0; }
    .preview-top { display:flex; justify-content:space-between; color:#C8D0E8; font-size:.72rem; font-weight:800; letter-spacing:1.4px; }
    .live-pill { color:#70E0D1; }
    .preview-label { color:#C8D0E8; font-size:.9rem; margin-top:2.2rem; }
    .preview-amount { color:#fff; font-size:2.5rem; font-weight:800; letter-spacing:-1px; }
    .preview-change { color:#70E0D1; font-size:.9rem; font-weight:700; margin-top:.3rem; }
    .preview-change span { color:#AAB5D0; font-weight:400; }
    .preview-stats { display:flex; gap:1rem; margin-top:2rem; }
    .preview-stats div { flex:1; background:rgba(255,255,255,.08); border:1px solid rgba(255,255,255,.1); border-radius:13px; padding:.9rem; }
    .preview-stats small { display:block; color:#AAB5D0; font-size:.68rem; margin-bottom:.35rem; }
    .preview-stats strong { font-size:1.05rem; }
    .preview-chart { height:80px; display:flex; align-items:end; gap:12px; margin-top:1.4rem; }
    .preview-chart div { flex:1; border-radius:7px 7px 2px 2px; background:linear-gradient(180deg,#22C7B8,#6D5CE8); }
    .preview-foot { color:#AAB5D0; font-size:.78rem; margin-top:.8rem; }
    .intro-section-title { color:#17213D; font-size:1.45rem; font-weight:800; text-align:center; margin:2.3rem 0 1.2rem; }
    .feature-card { background:#fff; border:1px solid #E8EAF3; border-radius:17px; padding:1.35rem; min-height:155px; box-shadow:0 7px 24px rgba(23,33,61,.04); }
    .feature-icon { width:42px; height:42px; display:grid; place-items:center; background:#F1EEFF; border-radius:12px; font-size:1.25rem; }
    .feature-card h3 { color:#17213D; font-size:1rem; margin:.9rem 0 .4rem; }
    .feature-card p { color:#68738F; font-size:.86rem; line-height:1.55; margin:0; }
    .intro-footer { text-align:center; color:#929BB1; font-size:.7rem; font-weight:800; letter-spacing:1.5px; margin:2.4rem 0 1rem; }
    .nav-divider { height:1px; background:#E7E9F2; margin:.5rem 0 1.5rem; }
    .or-divider { display:flex; align-items:center; gap:12px; color:#929BB1; font-size:.72rem; font-weight:700; margin:.8rem 0; }
    .or-divider:before,.or-divider:after { content:""; height:1px; background:#E5E7F0; flex:1; }
    [data-testid="stRadio"] [role="radiogroup"] { gap:.2rem; }
    [data-testid="stRadio"] label { font-weight:650; }

    /* ===== Top navigation: deep-purple gradient bar, glass pill menu ===== */
    /* neutralise the generic white "card" wrapper so it doesn't box the navbar in */
    [data-testid="stVerticalBlockBorderWrapper"]:has(> .st-key-topnav) {
        background: transparent !important; border: none !important; box-shadow: none !important;
        padding: 0 !important; margin: 0 !important;
        position: sticky !important; top: .6rem; z-index: 999;
    }
    div.st-key-topnav {
        position: sticky !important; top: .6rem; z-index: 999;
        background: linear-gradient(120deg, #1F1450 0%, #3A25A0 45%, #6D5CE8 100%) !important;
        border: 1px solid rgba(255,255,255,.14) !important;
        border-radius: 22px !important;
        padding: .7rem 1.3rem !important;
        margin: 0 0 .4rem 0 !important;
        box-shadow: 0 18px 40px rgba(58,37,160,.38), inset 0 1px 0 rgba(255,255,255,.18) !important;
        overflow: hidden;
    }
    div.st-key-topnav:hover { transform: none !important; }
    div.st-key-topnav::before {
        content: ""; position: absolute; left: 0; right: 0; top: 0; height: 3px;
        background: linear-gradient(90deg, #22C7B8, #B58CF5, #22C7B8);
        background-size: 200% 100%; animation: finovaShine 6s linear infinite;
    }
    div.st-key-topnav::after {
        content: ""; position: absolute; right: -60px; top: -90px; width: 260px; height: 260px; border-radius: 50%;
        background: radial-gradient(circle, rgba(181,140,245,.45), transparent 70%); pointer-events: none;
    }
    @keyframes finovaShine { to { background-position: -200% 0; } }

    div.st-key-topnav .nav-logo { display: inline-block; line-height: 0; transition: transform .25s ease; }
    div.st-key-topnav .nav-logo:hover { transform: scale(1.04); }
    div.st-key-topnav .nav-logo img { filter: drop-shadow(0 4px 14px rgba(255,255,255,.18)); }

    div.st-key-topnav [data-testid="stRadio"] [role="radiogroup"] {
        gap: .2rem !important; flex-wrap: nowrap; justify-content: flex-start;
        background: rgba(255,255,255,.10); border: 1px solid rgba(255,255,255,.16);
        padding: .3rem; border-radius: 16px; width: fit-content !important; margin: 0 auto; max-width: 100%;
        overflow-x: auto; scrollbar-width: none;
    }
    div.st-key-topnav [data-testid="stRadio"] label {
        margin: 0 !important; padding: .5rem .85rem !important; border-radius: 12px; cursor: pointer; flex: 0 0 auto;
        transition: background .2s ease, box-shadow .2s ease, transform .2s ease; white-space: nowrap;
    }
    div.st-key-topnav [data-testid="stRadio"] label :is(div, span):not(:has(p)):not([data-testid]) { display: none !important; }
    div.st-key-topnav [data-testid="stRadio"] label > div:first-child:not(:has(p)) { display: none !important; }
    div.st-key-topnav [data-testid="stRadio"] label [data-testid="stMarkdownContainer"] { margin: 0 !important; }
    div.st-key-topnav [data-testid="stRadio"] label p {
        font-size: .88rem !important; font-weight: 700 !important; color: #DCD3FF !important; white-space: nowrap; margin: 0 !important;
        transition: color .2s ease;
    }
    div.st-key-topnav [data-testid="stRadio"] label:hover {
        background: rgba(255,255,255,.18); transform: translateY(-2px);
        box-shadow: 0 8px 18px rgba(15,8,60,.28);
    }
    div.st-key-topnav [data-testid="stRadio"] label:hover p { color: #fff !important; }
    div.st-key-topnav [data-testid="stRadio"] label:active { transform: scale(.95); }
    div.st-key-topnav [data-testid="stRadio"] label:has(input:checked) {
        background: #FFFFFF; box-shadow: 0 10px 24px rgba(15,8,60,.35), 0 0 0 3px rgba(181,140,245,.35);
        transform: translateY(-1px);
    }
    div.st-key-topnav [data-testid="stRadio"] label:has(input:checked) p { color: #4B2FC4 !important; }

    div.st-key-topnav .nav-avatar {
        width: 42px; height: 42px; border-radius: 50%; margin-left: auto;
        display: grid; place-items: center; color: #4B2FC4; font-weight: 800; font-size: 1.05rem;
        background: #fff; box-shadow: 0 0 0 3px rgba(255,255,255,.3), 0 6px 14px rgba(15,8,60,.3);
        transition: transform .2s ease; cursor: default;
    }
    div.st-key-topnav .nav-avatar:hover { transform: scale(1.1) rotate(-4deg); }
    div.st-key-topnav .stButton button {
        border-radius: 12px !important; font-weight: 700 !important; color: #fff !important;
        background: rgba(255,255,255,.14) !important; border: 1.5px solid rgba(255,255,255,.4) !important;
        padding: .5rem 1rem !important; transition: all .2s ease !important;
    }
    div.st-key-topnav .stButton button:hover {
        color: #4B2FC4 !important; background: #fff !important; transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(15,8,60,.3) !important;
    }
    div.st-key-topnav .stButton button p, div.st-key-topnav .stButton button div { color: #fff !important; font-weight: 700 !important; }
    div.st-key-topnav .stButton button:hover p, div.st-key-topnav .stButton button:hover div { color: #4B2FC4 !important; }
    div.st-key-topnav .stButton button:active { transform: scale(.96); }
    .nav-spacer { height: 1rem; }

    /* section content slides in whenever a new section is opened */
    @keyframes finovaIn { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: none; } }
    .finova-header, .kpi-header { animation: finovaIn .5s ease both; }

    @media (max-width: 850px) {
      div.st-key-topnav { position: static !important; }
      .intro-copy h1 { font-size:2.5rem; }
      .intro-preview { min-height:300px; }
    }

    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

def render_header(title: str, subtitle: str):
    """Renders sleek top hero banner header."""
    st.markdown(
        f"""
        <div class="finova-header">
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_kpi_card(title: str, amount: float, kpi_type: str, icon_symbol: str, is_percent: bool = False):
    """Renders a styled KPI metric card."""
    formatted_val = f"{amount:.1f}%" if is_percent else f"₹{amount:,.2f}"
    st.markdown(
        f"""
        <div class="kpi-card-v2 {kpi_type}">
            <div class="kpi-header">
                <span class="kpi-title">{title}</span>
                <span class="kpi-icon {kpi_type}">{icon_symbol}</span>
            </div>
            <div class="kpi-amount {kpi_type}">{formatted_val}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_sidebar_user_profile(user_name: str, user_id: str):
    """Renders sleek glassmorphic user profile card in sidebar."""
    initials = "".join([part[0].upper() for part in user_name.split()[:2]]) if user_name else "FN"
    st.sidebar.markdown(
        f"""
        <div class="user-profile-banner">
            <div class="user-avatar-circle">{initials}</div>
            <div class="user-details">
                <div class="user-name-title">{user_name}</div>
                <div class="user-status-tag">
                    <span class="online-dot"></span> Active Session
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_footer():
    """Renders sleek app footer badge in sidebar."""
    st.sidebar.markdown(
        """
        <div class="univ-footer">
            <strong>Finova – Smart Finance Tracker</strong>
            <p style="color: #6D5CE8; font-weight: 700; margin-top: 0.3rem;">AI-Powered Personal Finance</p>
        </div>
        """,
        unsafe_allow_html=True
    )
