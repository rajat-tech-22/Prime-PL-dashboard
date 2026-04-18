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
import streamlit as st

def login_ui():
    st.markdown("""
    <style>
    /* Main wrapper to remove sidebar and top padding */
    .stApp { background-color: #f0f2f6; }
    
    .login-card {
        display: flex;
        width: 800px;
        height: 500px;
        margin: 50px auto;
        background: white;
        border-radius: 20px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.1);
        overflow: hidden;
    }
    
    .left-pane {
        width: 40%;
        background: #0b1739;
        padding: 40px;
        color: white;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    
    .right-pane {
        width: 60%;
        padding: 60px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .stat-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 10px;
    }
    
    .stat-box {
        background: rgba(255,255,255,0.05);
        padding: 10px;
        border-radius: 10px;
    }
    
    .stat-val { font-size: 18px; font-weight: 700; }
    .stat-lbl { font-size: 10px; color: #7b9cdb; text-transform: uppercase; }
    
    </style>
    
    <div class="login-card">
        <div class="left-pane">
            <div>
                <h2 style="color:white;">MyMoneyMantra</h2>
                <p style="color:#7b9cdb; font-size:14px;">PRIME PL DASHBOARD</p>
                <h1 style="font-size:24px; margin-top:20px;">Smart Loans, <br>Smarter Insights</h1>
            </div>
            <div class="stat-grid">
                <div class="stat-box"><div class="stat-val">12.4 Cr</div><div class="stat-lbl">Monthly Disbursed</div></div>
                <div class="stat-box"><div class="stat-val">98.2 %</div><div class="stat-lbl">Target Achievement</div></div>
            </div>
        </div>
        <div class="right-pane">
            <h2 style="color:#0b1739;">Welcome back</h2>
            <p style="color:#64748b;">Sign in to MyMoneyMantra Prime PL</p>
            </div>
    </div>
    """, unsafe_allow_html=True)

# App mein use karne ka tarika:
login_ui()

# Ab Streamlit ke inputs ko 'right-pane' mein adjust karne ke liye column use karein:
col1, col2 = st.columns([0.4, 0.6]) # Left pane ke liye space chhod kar
with col2:
    # Yaha aapke existing st.text_input aur login button aayenge
    username = st.text_input("USERNAME")
    password = st.text_input("PASSWORD", type="password")
    if st.button("Sign In"):
        # Login logic
        pass
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
