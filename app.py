import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from streamlit_autorefresh import st_autorefresh
import numpy as np

# -----------------------------
# Page Config & Auto-refresh
# -----------------------------
st.set_page_config(page_title="Manager Dashboard 2.0", layout="wide")
st_autorefresh(interval=60*1000, key="refresh_2")

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

def calc_metrics(f):
    total_disb = f["Disbursed AMT"].sum()
    total_rev = f["Total_Revenue"].sum()
    avg_payout = (total_rev/total_disb)*100 if total_disb else 0
    txn_count = len(f)
    avg_disb = total_disb/txn_count if txn_count else 0
    top_bank = f.groupby("Bank")["Disbursed AMT"].sum().idxmax() if not f.empty else "N/A"
    top_campaign = f.groupby("Campaign")["Disbursed AMT"].sum().idxmax() if not f.empty else "N/A"
    top_caller = f.groupby("Caller")["Disbursed AMT"].sum().idxmax() if not f.empty else "N/A"
    trends = f["Disbursed AMT"].rolling(3).sum().fillna(0).tolist()
    return total_disb, total_rev, avg_payout, txn_count, avg_disb, top_bank, top_campaign, top_caller, trends

def sparkline(fig, data, color="#FFFFFF"):
    fig.add_trace(go.Scatter(y=data, mode="lines+markers",
                             line=dict(color=color, width=2),
                             marker=dict(size=3),
                             showlegend=False))
    return fig

# -----------------------------
# Sidebar Filters
# -----------------------------
st.sidebar.title("Dashboard 2.0")
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
    st.header(f"📊 {selected_manager1} - {selected_month1}")

    f = df[(df["Manager"]==selected_manager1) & (df["Disb Month"]==selected_month1)]
    if f.empty:
        st.warning("No data available")
    else:
        total_disb, total_rev, avg_payout, txn_count, avg_disb, top_bank, top_campaign, top_caller, trends = calc_metrics(f)

        # Colorful KPI Cards
        kpi_colors = ["#FF6B6B", "#4ECDC4", "#FFD93D"]
        icons = ["💰", "📈", "🧾"]
        kpi_values = [total_disb, total_rev, avg_payout]
        kpi_labels = ["Total Disbursed", "Total Revenue", "Avg Payout %"]

        cols = st.columns(3)
        for i, col in enumerate(cols):
            with col:
                st.markdown(f"""
                    <div style="background-color:{kpi_colors[i]}; padding:20px; border-radius:15px; color:white; text-align:center;">
                        <h3>{icons[i]} {kpi_labels[i]}</h3>
                        <h2>{format_inr(kpi_values[i]) if i<2 else f'{kpi_values[i]:.2f}%'} </h2>
                    </div>
                    """, unsafe_allow_html=True)
                # Mini sparkline inside card
                fig = go.Figure()
                sparkline(fig, trends, color="white")
                fig.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=50, xaxis=dict(visible=False), yaxis=dict(visible=False))
                st.plotly_chart(fig, use_container_width=True)

        # Charts in expander
        with st.expander("Charts"):
            fig_bank = go.Figure()
            for bank, val in f.groupby("Bank")["Disbursed AMT"].sum().items():
                fig_bank.add_bar(x=[bank], y=[val/100000], text=[f"{val/100000:.2f}L"], textposition="auto")
            fig_bank.update_layout(template="plotly_white", yaxis_title="Amount (L)")
            st.plotly_chart(fig_bank, use_container_width=True)

            fig_campaign = go.Figure()
            for camp, val in f.groupby("Campaign")["Disbursed AMT"].sum().items():
                fig_campaign.add_bar(x=[camp], y=[val/100000], text=[f"{val/100000:.2f}L"], textposition="auto")
            fig_campaign.update_layout(template="plotly_white", yaxis_title="Amount (L)")
            st.plotly_chart(fig_campaign, use_container_width=True)

        # Insights
        with st.expander("Insights"):
            st.markdown(f"- **Top Bank:** {top_bank}")
            st.markdown(f"- **Top Campaign:** {top_campaign}")
            st.markdown(f"- **Top Caller:** {top_caller}")
            st.markdown(f"- **Transactions:** {txn_count}")
            st.markdown(f"- **Avg Disbursed:** {format_inr(avg_disb)}")

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

    d1,r1,p1,txn1,avg1,top_bank1,top_camp1,top_caller1,trends1 = calc_metrics(f1)
    d2,r2,p2,txn2,avg2,top_bank2,top_camp2,top_caller2,trends2 = calc_metrics(f2)

    # KPI Cards with Deltas
    kpi_colors = ["#FF6B6B", "#4ECDC4", "#FFD93D"]
    labels = ["Total Disbursed", "Total Revenue", "Avg Payout %"]
    values1 = [d1,r1,p1]
    values2 = [d2,r2,p2]
    cols = st.columns(3)
    for i, col in enumerate(cols):
        with col:
            delta = values1[i]-values2[i]
            arrow = "⬆️" if delta>0 else "⬇️"
            st.markdown(f"""
                <div style="background-color:{kpi_colors[i]}; padding:20px; border-radius:15px; color:white; text-align:center;">
                    <h3>{labels[i]}</h3>
                    <h2>{format_inr(values1[i]) if i<2 else f'{values1[i]:.2f}%'} {arrow} {abs(delta):.2f}</h2>
                </div>
                """, unsafe_allow_html=True)
            # Mini sparkline
            fig = go.Figure()
            sparkline(fig, trends1 if i==0 else trends2, color="white")
            fig.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=50, xaxis=dict(visible=False), yaxis=dict(visible=False))
            st.plotly_chart(fig, use_container_width=True)

    # Charts
    with st.expander("Charts Comparison"):
        # Bank comparison
        keys = sorted(set(f1["Bank"]).union(f2["Bank"]))
        fig_bank = go.Figure()
        for k in keys:
            fig_bank.add_bar(x=[k], y=[f1.groupby("Bank")["Disbursed AMT"].sum().get(k,0)/100000], name=selected_manager1)
            fig_bank.add_bar(x=[k], y=[f2.groupby("Bank")["Disbursed AMT"].sum().get(k,0)/100000], name=selected_manager2)
        fig_bank.update_layout(barmode='group', template="plotly_white", yaxis_title="Amount (L)")
        st.plotly_chart(fig_bank, use_container_width=True)

        # Campaign comparison
        keys = sorted(set(f1["Campaign"]).union(f2["Campaign"]))
        fig_camp = go.Figure()
        for k in keys:
            fig_camp.add_bar(x=[k], y=[f1.groupby("Campaign")["Disbursed AMT"].sum().get(k,0)/100000], name=selected_manager1)
            fig_camp.add_bar(x=[k], y=[f2.groupby("Campaign")["Disbursed AMT"].sum().get(k,0)/100000], name=selected_manager2)
        fig_camp.update_layout(barmode='group', template="plotly_white", yaxis_title="Amount (L)")
        st.plotly_chart(fig_camp, use_container_width=True)

    # Insights
    with st.expander("Insights"):
        st.markdown(f"- **{selected_manager1} Top Bank:** {top_bank1}, Top Campaign: {top_camp1}, Top Caller: {top_caller1}")
        st.markdown(f"- **{selected_manager2} Top Bank:** {top_bank2}, Top Campaign: {top_camp2}, Top Caller: {top_caller2}")

    winner = selected_manager1 if d1>d2 else selected_manager2
    st.success(f"🏆 Top Performer: {winner}")
