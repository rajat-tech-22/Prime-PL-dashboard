import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from streamlit_autorefresh import st_autorefresh

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(page_title="Manager Dashboard", layout="wide")
st_autorefresh(interval=60*1000, key="refresh")

# -----------------------------
# Load Data
# -----------------------------
@st.cache_data(ttl=60)
def load_data():
    url = "https://docs.google.com/spreadsheets/d/1I1ql5NwFafbWXYkVOvv0yvMM9GKnJ5954R4zif2owGI/export?format=csv"
    df = pd.read_csv(url)
    df.replace("null", None, inplace=True)
    return df

df = load_data()

# -----------------------------
# Helper Functions
# -----------------------------
def format_inr(number):
    if number is None or number == 0:
        return "₹0"
    s = str(int(number))
    last3 = s[-3:]
    rest = s[:-3]
    parts = []
    while len(rest) > 2:
        parts.append(rest[-2:])
        rest = rest[:-2]
    if rest:
        parts.append(rest)
    parts.reverse()
    return "₹" + ",".join(parts) + "," + last3

base_colors = ["#636EFA","#EF553B","#00CC96","#AB63FA","#FFA15A","#19D3F3","#FF6692","#B6E880"]

def get_colors(index_list, top_value):
    colors = []
    for i, val in enumerate(index_list):
        if val == top_value:
            colors.append("#FFD700")
        else:
            colors.append(base_colors[i % len(base_colors)])
    return colors

def calc_metrics(f):
    total_disb = f["Disbursed AMT"].sum()
    total_rev = f["Total_Revenue"].sum()
    avg_payout = (total_rev/total_disb)*100 if total_disb else 0
    txn_count = len(f)
    avg_disb = total_disb/txn_count if txn_count else 0
    top_bank = f.groupby("Bank")["Disbursed AMT"].sum().idxmax() if not f.empty else "N/A"
    top_campaign = f.groupby("Campaign")["Disbursed AMT"].sum().idxmax() if not f.empty else "N/A"
    top_caller = f.groupby("Caller")["Disbursed AMT"].sum().idxmax() if not f.empty else "N/A"
    return total_disb,total_rev,avg_payout,txn_count,avg_disb,top_bank,top_campaign,top_caller

def plot_bar(f, col, top_value, manager_name, key_val):
    summary = f.groupby(col)["Disbursed AMT"].sum()
    colors = get_colors(summary.index, top_value)
    fig = go.Figure(go.Bar(
        x=summary.index,
        y=summary.values/100000,
        text=[f"{v/100000:.2f}L" for v in summary.values],
        textposition="auto",
        marker_color=colors,
        name=manager_name
    ))
    fig.update_layout(
        yaxis_title="Amount (L)",
        template="plotly_white",
        height=400,
        title=f"{manager_name} - {col} Summary"
    )
    return fig

def colored_metric(label, value, color="#000000"):
    st.markdown(f"""
        <div style="background-color:{color}; padding:20px; border-radius:10px; text-align:center; color:white; margin-bottom:10px;">
            <h4 style="margin:0">{label}</h4>
            <h2 style="margin:0">{value}</h2>
        </div>
        """, unsafe_allow_html=True)

# -----------------------------
# Sidebar Filters (Interactive but safe)
# -----------------------------
st.sidebar.title("📊 Dashboard Filters")
dashboard_type = st.sidebar.radio("Select Dashboard", ["All Managers", "Single Manager", "Comparison"])

verticals = ["All"] + sorted(df["Vertical"].dropna().unique())
months = sorted(df["Disb Month"].dropna().unique())
managers = sorted(df["Manager"].dropna().unique())
latest_month_index = len(months)-1

# Default filtered dfs
filtered_df = df.copy()
filtered_df1 = df.copy()
filtered_df2 = df.copy()

# -----------------------------
# All Managers Filters
# -----------------------------
if dashboard_type == "All Managers":
    with st.sidebar.expander("Filters", expanded=True):
        selected_month = st.selectbox("Select Month", months, index=latest_month_index)
        selected_vertical = st.selectbox("Business Vertical", verticals)
        if selected_vertical != "All":
            filtered_df = filtered_df[filtered_df["Vertical"]==selected_vertical]
        if selected_month:
            filtered_df = filtered_df[filtered_df["Disb Month"]==selected_month]
        campaigns_available = sorted(filtered_df["Campaign"].dropna().unique())
        selected_campaigns = st.multiselect("Campaigns", campaigns_available, default=campaigns_available)
        if selected_campaigns:
            filtered_df = filtered_df[filtered_df["Campaign"].isin(selected_campaigns)]

# -----------------------------
# Single Manager Filters
# -----------------------------
elif dashboard_type == "Single Manager":
    with st.sidebar.expander("Filters", expanded=True):
        selected_manager = st.selectbox("Select Manager", managers)
        selected_month = st.selectbox("Select Month", months, index=latest_month_index)
        filtered_df = df[df["Manager"]==selected_manager]
        if selected_month:
            filtered_df = filtered_df[filtered_df["Disb Month"]==selected_month]
        campaigns_available = sorted(filtered_df["Campaign"].dropna().unique())
        selected_campaigns = st.multiselect("Campaigns", campaigns_available, default=campaigns_available)
        if selected_campaigns:
            filtered_df = filtered_df[filtered_df["Campaign"].isin(selected_campaigns)]

# -----------------------------
# Comparison Filters
# -----------------------------
elif dashboard_type == "Comparison":
    with st.sidebar.expander("Filters", expanded=True):
        selected_manager1 = st.selectbox("Select First Manager", managers)
        selected_month1 = st.selectbox("Month for First Manager", months, index=latest_month_index)
        selected_manager2 = st.selectbox("Select Second Manager", managers)
        selected_month2 = st.selectbox("Month for Second Manager", months, index=latest_month_index)
        filtered_df1 = df[(df["Manager"]==selected_manager1) & (df["Disb Month"]==selected_month1)]
        filtered_df2 = df[(df["Manager"]==selected_manager2) & (df["Disb Month"]==selected_month2)]

# -----------------------------
# Dashboard content remains exactly as before
# -----------------------------
# All Managers, Single Manager, Comparison logic untouched
