import streamlit as st
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
from streamlit_autorefresh import st_autorefresh
import os
import time
from datetime import datetime, timedelta, timezone

# ─────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────
st.set_page_config(
    page_title="Prime PL Dashboard",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)
st_autorefresh(interval=60 * 1000, key="refresh")

# ─────────────────────────────────────────
# GLOBAL CSS (PROFESSIONAL THEME)
# ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif !important; }

/* Login Container Styles */
.login-page {
    display: flex; max-width: 900px; margin: 60px auto; border-radius: 24px;
    overflow: hidden; box-shadow: 0 20px 40px -10px rgba(0,0,0,0.15);
    background: #ffffff; border: 1px solid #e2e8f0;
}
.login-left {
    width: 45%; background: #0f172a; padding: 48px; color: white;
    display: flex; flex-direction: column; justify-content: space-between;
}
.login-right {
    width: 55%; padding: 48px; display: flex; flex-direction: column; justify-content: center;
}
.login-title { font-size: 28px; font-weight: 800; color: #0f172a; margin-bottom: 8px; }
.login-sub { font-size: 14px; color: #64748b; margin-bottom: 32px; }

/* Input field overrides */
.stTextInput > div > div > input { border-radius: 10px !important; padding: 12px 16px !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# AUTH LOGIC
# ─────────────────────────────────────────
USERNAME = os.getenv("APP_USERNAME", "Mymoneymantra")
PASSWORD = os.getenv("APP_PASSWORD", "Prime110")

if "login" not in st.session_state: st.session_state.login = False
if "attempts" not in st.session_state: st.session_state.attempts = 0
if "lock_time" not in st.session_state: st.session_state.lock_time = None

if not st.session_state.login:
    _, col_center, _ = st.columns([0.1, 0.8, 0.1])
    with col_center:
        st.markdown('''
        <div class="login-page">
          <div class="login-left">
            <div>
                <div style="font-size: 24px; font-weight: 800; margin-bottom: 12px;">Prime PL</div>
                <div style="font-size: 14px; color: #94a3b8; line-height: 1.6;">Welcome back to the MyMoneyMantra performance dashboard.</div>
            </div>
            <div style="margin-top: 40px; font-size: 12px; color: #475569;">SECURE ACCESS PORTAL &bull; V 2.0</div>
          </div>
          <div class="login-right">
            <div class="login-title">Sign In</div>
            <div class="login-sub">Enter your credentials to continue</div>
        ''', unsafe_allow_html=True)

        u = st.text_input("Username", placeholder="Username")
        p = st.text_input("Password", type="password", placeholder="••••••••")

        if st.button("Authenticate", use_container_width=True):
            if u == USERNAME and p == PASSWORD:
                st.session_state.login = True
                st.rerun()
            else:
                st.error("Invalid credentials.")
        st.markdown('</div></div>', unsafe_allow_html=True)
    st.stop()

# ─────────────────────────────────────────
# MAIN DASHBOARD (ONLY RUNS AFTER LOGIN)
# ─────────────────────────────────────────
st.sidebar.markdown("## 💼 Prime PL")
dashboard_type = st.sidebar.radio("Navigation", ["🏠 Overview", "👤 Single Manager"])

if dashboard_type == "🏠 Overview":
    st.title("Overview Dashboard")
    st.write("Welcome to your dashboard!")
    # ... Baki pura dashboard code yaha rahega ...

# (Note: Yaha aap baki code paste kar sakte hain jo aapne pehle share kiya tha)
