import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from streamlit_autorefresh import st_autorefresh
import numpy as np

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

def get_kpi_color(value, top_value=None):
    # Conditional coloring logic
    if top_value is not None:
        return "green" if value == top_value else "orange"
    else:
        if value > 0:
            return "green"
        elif value == 0:
            return "yellow"
        else:
            return "red"

base_colors = ["#636EFA","#EF553B","#00CC96","#AB63FA","#FFA15A","#19D3F3","#FF6692","#B6E880"]

def get_colors(index_list, top_value):
    colors = []
    for i, val in enumerate(index_list):
        colors.append("#FFD700" if val==top_value else base_colors[i % len(base_colors)])
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

def plot_bar(f, col, top_value, manager_name, key_id):
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
        title=f"{col} Wise Disbursed Amount - {manager_name}"
    )
    st.plotly_chart(fig, use_container_width=True, key=key_id)

# -----------------------------
# Sidebar Filters
# -----------------------------
st.sidebar.title("Dashboard")
dashboard_type = st.sidebar.radio("Select Dashboard", ["Single Manager", "Comparison"])
managers = sorted(df["Manager"].dropna().unique())
months = sorted(df["Disb Month"].dropna().unique())

selected_manager1 = st.sidebar.selectbox("Manager 1", managers)
selected_month1 = st.sidebar.selectbox("Month 1", months)

if dashboard_type=="Comparison":
    selected_manager2 = st.sidebar.selectbox("Manager 2", managers, index=1)
    selected_month2 = st.sidebar.selectbox("Month 2", months, index=1)

# -----------------------------
# SINGLE DASHBOARD
# -----------------------------
if dashboard_type=="Single Manager":
    st.header(f"📊 {selected_manager1} - {selected_month1} Dashboard")
    f = df[(df["Manager"]==selected_manager1)&(df["Disb Month"]==selected_month1)]

    if f.empty:
        st.warning("No data available")
    else:
        total_disb,total_rev,avg_payout,txn_count,avg_disb,top_bank,top_campaign,top_caller = calc_metrics(f)

        # KPI Cards with color
        col1,col2,col3,col4 = st.columns(4)
        col1.metric("💰 Total Disbursed", format_inr(total_disb), delta="", delta_color=get_kpi_color(total_disb))
        col2.metric("📈 Total Revenue", format_inr(total_rev), delta="", delta_color=get_kpi_color(total_rev))
        col3.metric("📊 Avg Payout %", f"{avg_payout:.2f}%", delta="", delta_color=get_kpi_color(avg_payout))
        col4.metric("📝 Transactions", txn_count, delta="", delta_color=get_kpi_color(txn_count))

        # Charts
        plot_bar(f,"Bank",top_bank,selected_manager1,"bank_chart")
        plot_bar(f,"Caller",top_caller,selected_manager1,"caller_chart")

        # Campaign Pie
        summary = f.groupby("Campaign")["Disbursed AMT"].sum()
        fig = go.Figure(go.Pie(
            labels=summary.index,
            values=summary.values/100000,
            hole=0.4,
            title="Campaign Distribution"
        ))
        st.plotly_chart(fig, use_container_width=True, key="campaign_pie")

        # Summary Cards
        st.markdown("### 📝 Summary Insights")
        st.success(f"Top Bank: {top_bank}")
        st.info(f"Top Campaign: {top_campaign}")
        st.warning(f"Top Caller: {top_caller}")
        st.info(f"Average Disbursed: {format_inr(avg_disb)}")

# -----------------------------
# COMPARISON DASHBOARD
# -----------------------------
if dashboard_type=="Comparison":
    st.header(f"📊 Comparison: {selected_manager1} vs {selected_manager2}")

    if selected_manager1==selected_manager2:
        st.warning("Select different managers")
        st.stop()

    f1 = df[(df["Manager"]==selected_manager1)&(df["Disb Month"]==selected_month1)]
    f2 = df[(df["Manager"]==selected_manager2)&(df["Disb Month"]==selected_month2)]

    d1,r1,p1,txn1,avg1,top_bank1,top_camp1,top_caller1 = calc_metrics(f1)
    d2,r2,p2,txn2,avg2,top_bank2,top_camp2,top_caller2 = calc_metrics(f2)

    # KPI Cards with conditional colors
    col1,col2,col3,col4 = st.columns(4)
    col1.metric(f"{selected_manager1} Total Disb", format_inr(d1), delta=f"{'▲' if d1>d2 else '▼'} {format_inr(abs(d1-d2))}", delta_color="inverse")
    col2.metric(f"{selected_manager2} Total Disb", format_inr(d2), delta="", delta_color=get_kpi_color(d2))
    col3.metric("Payout %", f"{p1:.2f}% vs {p2:.2f}%", delta=f"{'▲' if p1>p2 else '▼'} {abs(p1-p2):.2f}%", delta_color="inverse")
    col4.metric("Transactions", f"{txn1} vs {txn2}", delta_color=get_kpi_color(txn1))

    # Charts
    plot_bar(f1,"Bank",top_bank1,selected_manager1,"comp_bank_1")
    plot_bar(f2,"Bank",top_bank2,selected_manager2,"comp_bank_2")
    plot_bar(f1,"Caller",top_caller1,selected_manager1,"comp_caller_1")
    plot_bar(f2,"Caller",top_caller2,selected_manager2,"comp_caller_2")

    # Campaign Comparison
    fig = go.Figure()
    summary1 = f1.groupby("Campaign")["Disbursed AMT"].sum()
    summary2 = f2.groupby("Campaign")["Disbursed AMT"].sum()
    fig.add_trace(go.Bar(x=summary1.index, y=summary1.values/100000, name=selected_manager1, marker_color="#636EFA"))
    fig.add_trace(go.Bar(x=summary2.index, y=summary2.values/100000, name=selected_manager2, marker_color="#EF553B"))
    fig.update_layout(
        barmode='group',
        title="Campaign Comparison (Lacs)",
        yaxis_title="Amount (L)",
        template="plotly_white",
        height=400
    )
    st.plotly_chart(fig, use_container_width=True, key="campaign_comp")

    # Summary Cards
    st.markdown("### 📝 Summary Insights")
    st.success(f"{selected_manager1} Top Bank: {top_bank1}, Top Campaign: {top_camp1}, Top Caller: {top_caller1}")
    st.info(f"{selected_manager2} Top Bank: {top_bank2}, Top Campaign: {top_camp2}, Top Caller: {top_caller2}")
    st.warning(f"Avg Disbursed: {format_inr(avg1)} vs {format_inr(avg2)}")
