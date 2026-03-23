import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Manager Dashboard", layout="wide")
st_autorefresh(interval=60*1000, key="refresh")  # Auto-refresh every 60s

# -----------------------------
# Load Data
# -----------------------------
@st.cache_data(ttl=60)
def load_data():
    url = "https://docs.google.com/spreadsheets/d/1I1ql5NwFafbWXYkVOvv0yvMM9GKnJ5954R4zif2owGI/export?format=csv"
    df = pd.read_csv(url)
    df.replace("null", None, inplace=True)
    df.columns = df.columns.str.strip()
    for col in ["Manager","Disb Month","Bank","Caller","Campaign"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
    for col in ["Disbursed AMT","Total_Revenue"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
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
    return total_disb,total_rev,avg_payout,txn_count,avg_disb,top_bank,top_campaign,top_caller

def plot_sparkline(values):
    if len(values) < 2:
        values = values + [values[-1] if values else 0]
    trend_color = "green" if values[-1] >= values[0] else "red"
    fig = go.Figure(go.Scatter(
        y=values,
        mode="lines+markers",
        line=dict(color=trend_color, width=2),
        marker=dict(size=4),
        hoverinfo="y+text",
        text=[f"{v:,.0f}" for v in values]
    ))
    fig.update_layout(
        margin=dict(l=0,r=0,t=0,b=0),
        height=50,
        xaxis=dict(showgrid=False, visible=False),
        yaxis=dict(showgrid=False, visible=False)
    )
    return fig

def kpi_card(title, value, trend_values=None, delta=None):
    spark_html = ""
    if trend_values is not None and len(trend_values)>1:
        spark_fig = plot_sparkline(trend_values)
        spark_fig_html = spark_fig.to_html(include_plotlyjs='cdn', full_html=False)
        spark_html = f"<div style='height:60px'>{spark_fig_html}</div>"
    if delta is not None:
        color = "green" if delta >= 0 else "red"
        arrow = "▲" if delta >= 0 else "▼"
        delta_html = f"<span style='color:{color}; font-size:18px;'>{arrow} {abs(delta):,.0f}</span>"
    else:
        delta_html = ""
    st.markdown(f"""
        <div style='border:1px solid #ddd; padding:10px; border-radius:10px; text-align:center;'>
            <h4 style='margin:0'>{title}</h4>
            <h2 style='margin:0'>{value}</h2>
            {delta_html}
            {spark_html}
        </div>
        """, unsafe_allow_html=True)

def plot_bar(f, col, title):
    summary = f.groupby(col)["Disbursed AMT"].sum()
    fig = go.Figure(go.Bar(
        x=summary.index,
        y=summary.values/100000,
        text=[f"{v/100000:.2f}L" for v in summary.values],
        textposition="auto",
        marker_color="skyblue"
    ))
    fig.update_layout(title=title, yaxis_title="Amount (L)", template="plotly_white", height=400)
    return fig

def plot_pie(f, col, title):
    summary = f.groupby(col)["Disbursed AMT"].sum()
    fig = go.Figure(go.Pie(labels=summary.index, values=summary.values/100000, hole=0.4))
    fig.update_layout(title=title, template="plotly_white", height=400)
    return fig

# -----------------------------
# Sidebar Filters
# -----------------------------
st.sidebar.title("Dashboard")
dashboard_type = st.sidebar.radio("Select One", ["Single Manager", "Comparison"])
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
        total_disb,total_rev,avg_payout,txn_count,avg_disb,top_bank,top_campaign,top_caller = calc_metrics(f)

        # KPI Cards with dynamic sparklines
        col1,col2,col3,col4 = st.columns(4)
        with col1: kpi_card("Total Disbursed", format_inr(total_disb), trend_values=f["Disbursed AMT"].tolist())
        with col2: kpi_card("Total Revenue", format_inr(total_rev), trend_values=f["Total_Revenue"].tolist())
        with col3: kpi_card("Avg Payout %", f"{avg_payout:.2f}%", trend_values=(f["Total_Revenue"]/f["Disbursed AMT"]*100).tolist())
        with col4: kpi_card("Transactions", txn_count, trend_values=[1]*txn_count)

        st.plotly_chart(plot_bar(f,"Bank","Disbursed Amount by Bank"), use_container_width=True)
        st.plotly_chart(plot_bar(f,"Caller","Disbursed Amount by Caller"), use_container_width=True)
        st.plotly_chart(plot_pie(f,"Campaign","Disbursed Amount by Campaign"), use_container_width=True)

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

    d1,r1,p1,txn1,avg1,top_bank1,top_camp1,top_caller1 = calc_metrics(f1)
    d2,r2,p2,txn2,avg2,top_bank2,top_camp2,top_caller2 = calc_metrics(f2)

    col1,col2,col3,col4 = st.columns(4)
    with col1: kpi_card("Total Disbursed", format_inr(d1), trend_values=f1["Disbursed AMT"].tolist(), delta=d1-d2)
    with col2: kpi_card("Total Revenue", format_inr(r1), trend_values=f1["Total_Revenue"].tolist(), delta=r1-r2)
    with col3: kpi_card("Avg Payout %", f"{p1:.2f}%", trend_values=(f1["Total_Revenue"]/f1["Disbursed AMT"]*100).tolist(), delta=p1-p2)
    with col4: kpi_card("Transactions", txn1, trend_values=[1]*txn1, delta=txn1-txn2)

    st.plotly_chart(plot_bar(f1,"Bank",f"{selected_manager1} - Disbursed by Bank"), use_container_width=True)
    st.plotly_chart(plot_bar(f2,"Bank",f"{selected_manager2} - Disbursed by Bank"), use_container_width=True)
    st.plotly_chart(plot_pie(f1,"Campaign",f"{selected_manager1} - Campaign Breakdown"), use_container_width=True)
    st.plotly_chart(plot_pie(f2,"Campaign",f"{selected_manager2} - Campaign Breakdown"), use_container_width=True)

    winner = selected_manager1 if d1 > d2 else selected_manager2
    st.success(f"🏆 Top Performer: {winner}")
