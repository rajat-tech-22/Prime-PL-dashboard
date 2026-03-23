import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from streamlit_autorefresh import st_autorefresh
import numpy as np

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(page_title="Manager Dashboard", layout="wide")
st_autorefresh(interval=60*1000, key="refresh")  # Auto-refresh every 60 seconds

# -----------------------------
# Load Data from Google Sheets
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
    return total_disb, total_rev, avg_payout, txn_count, avg_disb, top_bank, top_campaign, top_caller

def plot_bar(f, col, top_value, manager_name):
    summary = f.groupby(col)["Disbursed AMT"].sum()
    colors = get_colors(summary.index, top_value)
    fig = go.Figure(go.Bar(
        x=summary.index,
        y=summary.values/100000,
        text=[f"{v/100000:.2f}L" for v in summary.values],
        textposition="auto",
        marker_color=colors,
        name=manager_name,
        width=0.5
    ))
    fig.update_layout(yaxis_title="Amount (L)", template="plotly_white", height=400)
    return fig

def plot_sparkline(series):
    fig = go.Figure(go.Scatter(y=series, mode="lines+markers", line=dict(width=2, color="#636EFA")))
    fig.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=60, xaxis=dict(visible=False), yaxis=dict(visible=False))
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
# Single Manager Dashboard
# -----------------------------
if dashboard_type=="Single Manager":
    st.header(f"📊 {selected_manager1} - {selected_month1} Dashboard")

    f = df[(df["Manager"]==selected_manager1) & (df["Disb Month"]==selected_month1)]

    if f.empty:
        st.warning("No data available")
    else:
        total_disb, total_rev, avg_payout, txn_count, avg_disb, top_bank, top_campaign, top_caller = calc_metrics(f)

        # KPI Cards with Sparklines
        kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
        with kpi_col1:
            st.markdown(f"**💰 Total Disbursed**\n{format_inr(total_disb)}")
            st.plotly_chart(plot_sparkline(f["Disbursed AMT"].cumsum()), use_container_width=True)
        with kpi_col2:
            st.markdown(f"**📈 Total Revenue**\n{format_inr(total_rev)}")
            st.plotly_chart(plot_sparkline(f["Total_Revenue"].cumsum()), use_container_width=True)
        with kpi_col3:
            st.markdown(f"**🧾 Avg Payout %**\n{avg_payout:.2f}%")
            st.plotly_chart(plot_sparkline([avg_payout]*len(f)), use_container_width=True)

        # Charts
        st.subheader("Charts")
        st.plotly_chart(plot_bar(f,"Bank",top_bank,selected_manager1), use_container_width=True)
        st.plotly_chart(plot_bar(f,"Caller",top_caller,selected_manager1), use_container_width=True)

        # Campaign Pie
        summary = f.groupby("Campaign")["Disbursed AMT"].sum()
        fig = go.Figure(go.Pie(labels=summary.index, values=summary.values/100000, hole=0.4))
        st.plotly_chart(fig, use_container_width=True)

        # Insights
        st.subheader("📝 Summary & Insights")
        st.write(f"Top Bank: {top_bank}")
        st.write(f"Top Campaign: {top_campaign}")
        st.write(f"Top Caller: {top_caller}")
        st.write(f"Transactions: {txn_count}")
        st.write(f"Avg Disbursed: {format_inr(avg_disb)}")

# -----------------------------
# Comparison Dashboard
# -----------------------------
if dashboard_type=="Comparison":
    st.header("📊 Comparison Dashboard")
    if selected_manager1 == selected_manager2:
        st.warning("Select different managers")
        st.stop()

    f1 = df[(df["Manager"]==selected_manager1) & (df["Disb Month"]==selected_month1)]
    f2 = df[(df["Manager"]==selected_manager2) & (df["Disb Month"]==selected_month2)]

    d1,r1,p1,txn1,avg1,top_bank1,top_camp1,top_caller1 = calc_metrics(f1)
    d2,r2,p2,txn2,avg2,top_bank2,top_camp2,top_caller2 = calc_metrics(f2)

    # KPI Cards with Deltas
    col1,col2,col3 = st.columns(3)
    col1.metric(f"{selected_manager1} Disbursed", format_inr(d1), delta=format_inr(d1-d2))
    col2.metric(f"{selected_manager2} Disbursed", format_inr(d2), delta=format_inr(d2-d1))
    col3.metric(f"Payout %", f"{p1:.2f}%", delta=f"{p1-p2:.2f}%")

    # Charts
    st.subheader("Bank-wise Comparison")
    keys = sorted(set(f1["Bank"]).union(set(f2["Bank"])))
    fig_bank = go.Figure()
    for k in keys:
        fig_bank.add_bar(x=[k], y=[f1.groupby("Bank")["Disbursed AMT"].sum().get(k,0)/100000], name=selected_manager1, marker_color="#636EFA", width=0.4)
        fig_bank.add_bar(x=[k], y=[f2.groupby("Bank")["Disbursed AMT"].sum().get(k,0)/100000], name=selected_manager2, marker_color="#EF553B", width=0.4)
    fig_bank.update_layout(barmode='group', yaxis_title="Amount (L)", template="plotly_white", height=400)
    st.plotly_chart(fig_bank, use_container_width=True)

    st.subheader("Caller-wise Comparison")
    keys = sorted(set(f1["Caller"]).union(set(f2["Caller"])))
    fig_caller = go.Figure()
    for k in keys:
        fig_caller.add_bar(x=[k], y=[f1.groupby("Caller")["Disbursed AMT"].sum().get(k,0)/100000], name=selected_manager1, marker_color="#636EFA", width=0.4)
        fig_caller.add_bar(x=[k], y=[f2.groupby("Caller")["Disbursed AMT"].sum().get(k,0)/100000], name=selected_manager2, marker_color="#EF553B", width=0.4)
    fig_caller.update_layout(barmode='group', yaxis_title="Amount (L)", template="plotly_white", height=400)
    st.plotly_chart(fig_caller, use_container_width=True)

    # Summary Insights
    st.subheader("📝 Comparison Insights")
    st.write(f"{selected_manager1} - Top Bank: {top_bank1}, Top Campaign: {top_camp1}, Top Caller: {top_caller1}")
    st.write(f"{selected_manager2} - Top Bank: {top_bank2}, Top Campaign: {top_camp2}, Top Caller: {top_caller2}")

    # Top Performer Highlight
    winner = selected_manager1 if d1>d2 else selected_manager2
    st.success(f"🏆 Top Performer: {winner}")
