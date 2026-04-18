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
import streamlit as st

# CSS ko yahan update karein
st.markdown("""
<style>
    .login-container { 
        display: flex; width: 900px; height: 520px; margin: 50px auto; 
        background: white; border-radius: 20px; box-shadow: 0 20px 40px rgba(0,0,0,0.15); 
        overflow: hidden; 
    }
    .left-pane { width: 45%; background: #0b1739; padding: 50px; color: white; }
    .right-pane { width: 55%; padding: 40px; display: flex; flex-direction: column; justify-content: center; }
    
    /* Input box ke liye styling fix */
    .stTextInput { width: 100% !important; }
    .stTextInput > div > div > input { 
        border-radius: 8px !important; border: 1px solid #e2e8f0 !important; 
        padding: 10px !important; margin-bottom: 10px;
    }
    
    /* Button fix */
    .stButton > button { background: #0b1739 !important; color: white !important; width: 100%; border-radius: 8px !important; }
</style>
""", unsafe_allow_html=True)

# Main Login Logic
if not st.session_state.get("login", False):
    # Outer div for card
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    # Left Column (Hardcoded HTML)
    st.markdown('<div class="left-pane">...Left Pane Content...</div>', unsafe_allow_html=True)
    
    # Right Column (Using Streamlit Columns)
    with st.container():
        # CSS pane ke liye hum alag se logic use karenge taaki input card ke bahar na nikle
        st.markdown('<div class="right-pane">', unsafe_allow_html=True)
        st.subheader("Welcome back")
        st.write("Sign in to MyMoneyMantra Prime PL")
        
        # Yahan inputs seedhe display honge
        u = st.text_input("Username", placeholder="Enter your username")
        p = st.text_input("Password", type="password", placeholder="Enter your password")
        
        if st.button("Sign In"):
            if u == "Mymoneymantra" and p == "Prime110":
                st.session_state.login = True
                st.rerun()
            else:
                st.error("Invalid credentials")
        st.markdown('</div>', unsafe_allow_html=True)
        
    st.markdown('</div>', unsafe_allow_html=True)
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
