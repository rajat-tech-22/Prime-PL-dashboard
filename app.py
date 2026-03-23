import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from streamlit_autorefresh import st_autorefresh
import numpy as np

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(page_title="Manager Dashboard", layout="wide")

# Auto Refresh हर 60 sec
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
    if number is None or number==0:
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

def calc_metrics(f):
    total_disb = f["Disbursed AMT"].sum()
    total_rev = f["Total_Revenue"].sum()
    avg_payout = (total_rev/total_disb)*100 if total_disb else 0
    txn_count = len(f)
    avg_disb = total_disb/txn_count if txn_count else 0
    top_bank = f.groupby("Bank")["Disbursed AMT"].sum().idxmax() if not f.empty else "N/A"
    top_campaign = f.groupby("Campaign")["Disbursed AMT"].sum().idxmax() if not f.empty else "N/A"
    top_caller = f.groupby("Caller")["Disbursed AMT"].sum().idxmax() if not f.empty else "N/A"
    # Mini trend for sparklines
    spark_disb = f.groupby("Disb Month")["Disbursed AMT"].sum()
    return total_disb,total_rev,avg_payout,txn_count,avg_disb,top_bank,top_campaign,top_caller,spark_disb

def plot_bar(f, col, top_value, manager_name, key_suffix):
    summary = f.groupby(col)["Disbursed AMT"].sum()
    colors = ["#FFD700" if val==top_value else "#636EFA" for val in summary.index]
    fig = go.Figure(go.Bar(
        x=summary.index,
        y=summary.values/100000,
        text=[f"{v/100000:.2f}L" for v in summary.values],
        textposition="auto",
        marker_color=colors,
        name=manager_name,
        width=0.5
    ))
    fig.update_layout(title=f"{col} Disbursed Amount", yaxis_title="Amount (L)", template="plotly_white", height=400)
    return fig

def plot_sparkline(series):
    fig = go.Figure(go.Scatter(y=series.values, mode="lines+markers", line=dict(color="#19D3F3")))
    fig.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=80, xaxis=dict(showgrid=False, visible=False), yaxis=dict(showgrid=False, visible=False))
    return fig

# -----------------------------
# Sidebar Filters
# -----------------------------
st.sidebar.title("Dashboard")
dashboard_type = st.sidebar.radio("Select Dashboard", ["Single Manager", "Comparison"])
managers = sorted(df["Manager"].dropna().unique())
months = sorted(df["Disb Month"].dropna().unique())
selected_manager1 = st.sidebar.selectbox("Select Manager 1", managers)
selected_month1 = st.sidebar.selectbox("Select Month 1", months)

if dashboard_type=="Comparison":
    selected_manager2 = st.sidebar.selectbox("Select Manager 2", managers, index=1)
    selected_month2 = st.sidebar.selectbox("Select Month 2", months, index=1)

# -----------------------------
# SINGLE DASHBOARD
# -----------------------------
if dashboard_type=="Single Manager":
    st.header(f"📊 {selected_manager1} - {selected_month1} Dashboard")
    f = df[(df["Manager"]==selected_manager1)&(df["Disb Month"]==selected_month1)]
    if f.empty:
        st.warning("No data available")
    else:
        total_disb,total_rev,avg_payout,txn_count,avg_disb,top_bank,top_campaign,top_caller,spark_disb = calc_metrics(f)
        
        # KPI Cards with color + sparklines
        col1,col2,col3,col4 = st.columns(4)
        col1.metric("💰 Total Disbursed", format_inr(total_disb))
        col1.plotly_chart(plot_sparkline(spark_disb), use_container_width=True)
        
        col2.metric("💵 Total Revenue", format_inr(total_rev))
        col2.plotly_chart(plot_sparkline(f.groupby("Disb Month")["Total_Revenue"].sum()), use_container_width=True)
        
        col3.metric("📈 Avg Payout %", f"{avg_payout:.2f}%")
        col4.metric("📊 Transactions", txn_count)

        # Charts
        st.plotly_chart(plot_bar(f,"Bank",top_bank,selected_manager1,"bank_single"), use_container_width=True)
        st.plotly_chart(plot_bar(f,"Caller",top_caller,selected_manager1,"caller_single"), use_container_width=True)

        # Campaign Pie
        summary = f.groupby("Campaign")["Disbursed AMT"].sum()
        fig = go.Figure(go.Pie(labels=summary.index, values=summary.values/100000, hole=0.4))
        fig.update_layout(title="Campaign Distribution")
        st.plotly_chart(fig, use_container_width=True)

        # Summary
        st.markdown("### 📝 Insights")
        st.write(f"Top Bank: {top_bank}")
        st.write(f"Top Campaign: {top_campaign}")
        st.write(f"Top Caller: {top_caller}")
        st.write(f"Avg Disbursed: {format_inr(avg_disb)}")

# -----------------------------
# COMPARISON DASHBOARD
# -----------------------------
if dashboard_type=="Comparison":
    st.header("📊 Comparison Dashboard")
    if selected_manager1 == selected_manager2:
        st.warning("Select different managers")
        st.stop()

    f1 = df[(df["Manager"]==selected_manager1)&(df["Disb Month"]==selected_month1)]
    f2 = df[(df["Manager"]==selected_manager2)&(df["Disb Month"]==selected_month2)]
    
    d1,r1,p1,txn1,avg1,top_bank1,top_camp1,top_caller1,spark1 = calc_metrics(f1)
    d2,r2,p2,txn2,avg2,top_bank2,top_camp2,top_caller2,spark2 = calc_metrics(f2)

    # KPI Cards with sparklines
    col1,col2,col3,col4 = st.columns(4)
    col1.metric(f"{selected_manager1} Disbursed", format_inr(d1), delta=f"{format_inr(d1-d2)}", delta_color="normal")
    col1.plotly_chart(plot_sparkline(spark1), use_container_width=True)
    
    col2.metric(f"{selected_manager2} Disbursed", format_inr(d2), delta=f"{format_inr(d2-d1)}", delta_color="normal")
    col2.plotly_chart(plot_sparkline(spark2), use_container_width=True)
    
    col3.metric("Avg Payout %", f"{p1:.2f}% vs {p2:.2f}%", delta_color="off")
    col4.metric("Transactions", f"{txn1} vs {txn2}", delta_color="off")
    
    # Charts
    st.plotly_chart(plot_bar(f1,"Bank",top_bank1,selected_manager1,"bank1"), use_container_width=True)
    st.plotly_chart(plot_bar(f2,"Bank",top_bank2,selected_manager2,"bank2"), use_container_width=True)
    st.plotly_chart(plot_bar(f1,"Caller",top_caller1,selected_manager1,"caller1"), use_container_width=True)
    st.plotly_chart(plot_bar(f2,"Caller",top_caller2,selected_manager2,"caller2"), use_container_width=True)
    
    # Summary Table
    st.markdown("### 📝 Insights")
    summary_df = pd.DataFrame({
        "Metric": ["Top Bank", "Top Campaign", "Top Caller", "Avg Disbursed"],
        selected_manager1: [top_bank1, top_camp1, top_caller1, format_inr(avg1)],
        selected_manager2: [top_bank2, top_camp2, top_caller2, format_inr(avg2)]
    })
    st.table(summary_df)
