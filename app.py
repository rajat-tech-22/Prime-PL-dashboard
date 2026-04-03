import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from streamlit_autorefresh import st_autorefresh
import os
import time
from datetime import datetime, timedelta, timezone

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="Manager Dashboard", layout="wide")
st_autorefresh(interval=60*1000, key="refresh")

# -----------------------------
# LOGIN CONFIG
# -----------------------------
USERNAME = os.getenv("APP_USERNAME", "Mymoneymantra")
PASSWORD = os.getenv("APP_PASSWORD", "Prime110")
MAX_ATTEMPTS = 4
LOCK_TIME = 43200

# -----------------------------
# SESSION
# -----------------------------
if "login" not in st.session_state:
    st.session_state.login = False
if "attempts" not in st.session_state:
    st.session_state.attempts = 0
if "lock_time" not in st.session_state:
    st.session_state.lock_time = None

# -----------------------------
# LOGIN PAGE
# -----------------------------
if not st.session_state.login:

    st.title("🔐 Login")

    if st.session_state.lock_time:
        elapsed = time.time() - st.session_state.lock_time
        if elapsed < LOCK_TIME:
            st.error("Login locked for 12 hours 🚫")
            st.stop()
        else:
            st.session_state.lock_time = None
            st.session_state.attempts = 0

    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        if u == USERNAME and p == PASSWORD:
            st.session_state.login = True
            st.rerun()
        else:
            st.session_state.attempts += 1
            if st.session_state.attempts >= MAX_ATTEMPTS:
                st.session_state.lock_time = time.time()
                st.error("Too many attempts 🚫")
            else:
                st.error("Invalid credentials ❌")

    st.stop()

# -----------------------------
# DATA LOAD
# -----------------------------
@st.cache_data(ttl=60)
def load_data():
    url = "https://docs.google.com/spreadsheets/d/1I1ql5NwFafbWXYkVOvv0yvMM9GKnJ5954R4zif2owGI/export?format=csv"
    return pd.read_csv(url)

df = load_data()

# -----------------------------
# DYNAMIC FILTER FUNCTION
# -----------------------------
def apply_dynamic_filters(df, key="main"):

    filtered_df = df.copy()
    st.sidebar.markdown("## 🔍 Filters")

    # Month
    months = sorted(filtered_df["Disb Month"].dropna().unique())
    selected_month = st.sidebar.selectbox("Month", months, index=len(months)-1, key=f"{key}_m")
    filtered_df = filtered_df[filtered_df["Disb Month"] == selected_month]

    # Vertical
    if "Vertical" in filtered_df.columns:
        verticals = ["All"] + sorted(filtered_df["Vertical"].dropna().unique())
        v = st.sidebar.selectbox("Vertical", verticals, key=f"{key}_v")
        if v != "All":
            filtered_df = filtered_df[filtered_df["Vertical"] == v]

    # Manager
    managers = ["All"] + sorted(filtered_df["Manager"].dropna().unique())
    m = st.sidebar.selectbox("Manager", managers, key=f"{key}_man")
    if m != "All":
        filtered_df = filtered_df[filtered_df["Manager"] == m]

    # Campaign
    campaigns = ["All"] + sorted(filtered_df["Campaign"].dropna().unique())
    c = st.sidebar.selectbox("Campaign", campaigns, key=f"{key}_c")
    if c != "All":
        filtered_df = filtered_df[filtered_df["Campaign"] == c]

    # Bank
    if "Bank" in filtered_df.columns:
        banks = ["All"] + sorted(filtered_df["Bank"].dropna().unique())
        b = st.sidebar.selectbox("Bank", banks, key=f"{key}_b")
        if b != "All":
            filtered_df = filtered_df[filtered_df["Bank"] == b]

    return filtered_df

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.title("📊 Dashboard")
dashboard_type = st.sidebar.radio("Select Dashboard", [
    "All Managers", "Single Manager", "Comparison", "Campaign Performance"
])

# Reset
if st.sidebar.button("🔄 Reset Filters"):
    st.session_state.clear()
    st.rerun()

# -----------------------------
# DASHBOARD: ALL MANAGERS
# -----------------------------
if dashboard_type == "All Managers":

    filtered_df = apply_dynamic_filters(df, "all")

    st.title("📊 All Managers")

    total = filtered_df["Disbursed AMT"].sum()
    rev = filtered_df["Total_Revenue"].sum()

    col1, col2 = st.columns(2)
    col1.metric("Total Disbursed", f"₹{int(total):,}")
    col2.metric("Revenue", f"₹{int(rev):,}")

    summary = filtered_df.groupby("Manager")["Disbursed AMT"].sum()

    fig = go.Figure(go.Bar(x=summary.index, y=summary.values))
    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# SINGLE MANAGER
# -----------------------------
elif dashboard_type == "Single Manager":

    filtered_df = apply_dynamic_filters(df, "single")

    st.title("👤 Single Manager")

    if filtered_df.empty:
        st.warning("No data")
    else:
        total = filtered_df["Disbursed AMT"].sum()
        st.metric("Total", f"₹{int(total):,}")

        fig = go.Figure(go.Bar(
            x=filtered_df["Campaign"],
            y=filtered_df["Disbursed AMT"]
        ))
        st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# COMPARISON
# -----------------------------
elif dashboard_type == "Comparison":

    st.sidebar.markdown("## 🔵 First")
    f1 = apply_dynamic_filters(df, "c1")

    st.sidebar.markdown("## 🔴 Second")
    f2 = apply_dynamic_filters(df, "c2")

    st.title("⚖️ Comparison")

    d1 = f1["Disbursed AMT"].sum()
    d2 = f2["Disbursed AMT"].sum()

    st.write("First:", d1)
    st.write("Second:", d2)

    fig = go.Figure()
    fig.add_bar(name="First", x=["Disb"], y=[d1])
    fig.add_bar(name="Second", x=["Disb"], y=[d2])

    st.plotly_chart(fig)

# -----------------------------
# CAMPAIGN PERFORMANCE
# -----------------------------
elif dashboard_type == "Campaign Performance":

    filtered_df = apply_dynamic_filters(df, "camp")

    st.title("📈 Campaign Performance")

    summary = filtered_df.groupby("Campaign")["Disbursed AMT"].sum()

    fig = go.Figure(go.Bar(x=summary.index, y=summary.values))
    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# LOGOUT
# -----------------------------
if st.sidebar.button("🚪 Logout"):
    st.session_state.login = False
    st.rerun()
