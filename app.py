import streamlit as st
import pandas as pd
import plotly.graph_objs as go
import time
from datetime import datetime, timezone, timedelta

# Page Config
st.set_page_config(page_title="Prime PL Dashboard", layout="wide")

# ─────────────────────────────────────────
# CSS STYLING
# ─────────────────────────────────────────
st.markdown("""
<style>
    /* Modern Login Container */
    .login-container { display: flex; width: 900px; height: 520px; margin: 50px auto; background: white; border-radius: 20px; box-shadow: 0 20px 40px rgba(0,0,0,0.15); overflow: hidden; }
    .left-pane { width: 45%; background: #0b1739; padding: 50px; color: white; display: flex; flex-direction: column; justify-content: space-between; }
    .right-pane { width: 55%; padding: 60px; display: flex; flex-direction: column; justify-content: center; }
    .stat-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
    .stat-box { background: rgba(255,255,255,0.05); padding: 12px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.1); }
    .stat-val { font-size: 18px; font-weight: 700; color: white; }
    .stat-lbl { font-size: 9px; color: #7b9cdb; text-transform: uppercase; letter-spacing: 1px; }
    .stTextInput > div > div > input { border-radius: 8px !important; border: 1px solid #e2e8f0 !important; padding: 12px !important; }
    .stButton > button { background: #0b1739 !important; color: white !important; width: 100%; border-radius: 8px !important; font-weight: 600 !important; height: 45px !important; }
</style>
""", unsafe_allow_html=True)

# Auth Logic
if "login" not in st.session_state: st.session_state.login = False

if not st.session_state.login:
    st.markdown("""
    <div class="login-container">
        <div class="left-pane">
            <div>
                <h3 style="color:white; margin:0;">MyMoneyMantra</h3>
                <p style="color:#7b9cdb; font-size:12px; margin-bottom:30px;">PRIME PL DASHBOARD</p>
                <h1 style="font-size:26px; line-height:1.2;">Smart Loans,<br><span style="color:#3b82f6;">Smarter Insights</span></h1>
            </div>
            <div class="stat-grid">
                <div class="stat-box"><div class="stat-val">12.4 Cr</div><div class="stat-lbl">Monthly Disbursed</div></div>
                <div class="stat-box"><div class="stat-val">98.2 %</div><div class="stat-lbl">Target Achievement</div></div>
                <div class="stat-box"><div class="stat-val">6 Mgrs</div><div class="stat-lbl">Active Managers</div></div>
                <div class="stat-box"><div class="stat-val">2.74 %</div><div class="stat-lbl">Avg Payout %</div></div>
            </div>
        </div>
        <div class="right-pane">
            <h2 style="color:#0f172a; margin-bottom:5px;">Welcome back</h2>
            <p style="color:#64748b; margin-bottom:30px;">Sign in to MyMoneyMantra Prime PL</p>
    """, unsafe_allow_html=True)
    
    u = st.text_input("USERNAME")
    p = st.text_input("PASSWORD", type="password")
    if st.button("Sign In"):
        if u == "Mymoneymantra" and p == "Prime110":
            st.session_state.login = True
            st.rerun()
        else:
            st.error("Invalid credentials")
    
    st.markdown("</div></div>", unsafe_allow_html=True)
    st.stop()

# ─────────────────────────────────────────
# DASHBOARD CONTENT
# ─────────────────────────────────────────
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["🏠 Overview", "👤 Single Manager"])
if st.sidebar.button("Logout"):
    st.session_state.login = False
    st.rerun()

st.title(page)
if page == "🏠 Overview":
    st.write("Welcome to the main performance overview.")
    # Add your charts/tables here
elif page == "👤 Single Manager":
    st.write("View individual manager metrics.")
