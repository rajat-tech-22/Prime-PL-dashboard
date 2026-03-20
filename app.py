import streamlit as st
import pandas as pd
import plotly.graph_objs as go
import numpy as np

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(page_title="Pro Manager Dashboard", layout="wide")

# -----------------------------
# Dark Mode Toggle
# -----------------------------
dark_mode = st.sidebar.checkbox("🌙 Dark Mode")
bg_color = "#0E1117" if dark_mode else "white"
text_color = "white" if dark_mode else "black"
st.markdown(f"""
<style>
body {{background-color:{bg_color}; color:{text_color}}}
.stDownloadButton button {{background-color:#4CAF50; color:white}}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Load Data
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("data.csv")
    df.replace("null", None, inplace=True)
    df["Disbursed AMT"] = pd.to_numeric(df["Disbursed AMT"], errors='coerce').fillna(0)
    df["Total_Revenue"] = pd.to_numeric(df["Total_Revenue"], errors='coerce').fillna(0)
    return df

df = load_data()

# -----------------------------
# Helper Functions
# -----------------------------
colors = ["#636EFA","#EF553B","#00CC96","#AB63FA","#FFA15A","#19D3F3","#FF6692","#B6E880"]

def format_inr(x):
    if x == 0 or x is None: return "₹0"
    s = str(int(x))
    last3 = s[-3:]
    rest = s[:-3]
    parts = []
    while len(rest) > 2:
        parts.append(rest[-2:])
        rest = rest[:-2]
    if rest: parts.append(rest)
    parts.reverse()
    return "₹" + ",".join(parts) + "," + last3

def calc_metrics(f):
    total_disb = f["Disbursed AMT"].sum()
    total_rev = f["Total_Revenue"].sum()
    avg_payout = (total_rev/total_disb)*100 if total_disb else 0
    txn_count = len(f)
    avg_disb = total_disb/txn_count if txn_count else 0
    top_bank = f.groupby("Bank")["Disbursed AMT"].sum().idxmax() if not f.empty else "N/A"
    bottom_bank = f.groupby("Bank")["Disbursed AMT"].sum().idxmin() if not f.empty else "N/A"
    top_campaign = f.groupby("Campaign")["Disbursed AMT"].sum().idxmax() if not f.empty else "N/A"
    top_caller = f.groupby("Caller")["Disbursed AMT"].sum().idxmax() if not f.empty else "N/A"
    return total_disb, total_rev, avg_payout, txn_count, avg_disb, top_bank, bottom_bank, top_campaign, top_caller

def plot_bar(f, col, highlight=None):
    g = f.groupby(col)["Disbursed AMT"].sum()
    fig = go.Figure(go.Bar(
        x=g.index,
        y=g.values/100000,
        text=[f"{v/100000:.2f}L" for v in g.values],
        textposition="auto",
        marker_color=[("#FFD700" if i==highlight else colors[j%len(colors)]) for j,i in enumerate(g.index)]
    ))
    fig.update_layout(yaxis_title="Amount (L)", template="plotly_white", height=400)
    return fig

def plot_pie(f, col):
    g = f.groupby(col)["Disbursed AMT"].sum()
    fig = go.Figure(go.Pie(
        labels=g.index,
        values=g.values/100000,
        hole=0.4,
        marker=dict(colors=[colors[i%len(colors)] for i in range(len(g))])
    ))
    return fig

def sparkline(values):
    fig = go.Figure(go.Scatter(y=values, mode='lines', line=dict(width=2,color="#636EFA")))
    fig.update_layout(height=40, margin=dict(l=0,r=0,t=0,b=0), xaxis=dict(visible=False), yaxis=dict(visible=False))
    return fig

# -----------------------------
# Sidebar Filters
# -----------------------------
st.sidebar.title("Filters")
dashboard_type = st.sidebar.radio("Dashboard Mode", ["Single Manager", "Comparison"])
managers = sorted(df["Manager"].dropna().unique())
months = sorted(df["Disb Month"].dropna().unique())

selected_manager1 = st.sidebar.selectbox("Manager 1", managers)
selected_month1 = st.sidebar.selectbox("Month 1", months)
if dashboard_type=="Comparison":
    selected_manager2 = st.sidebar.selectbox("Manager 2", managers, index=1)
    selected_month2 = st.sidebar.selectbox("Month 2", months, index=1)

# -----------------------------
# Dashboard Rendering
# -----------------------------
def render_dashboard(f, manager, month):
    st.subheader(f"📊 {manager} - {month}")
    if f.empty:
        st.warning("No data available")
        return
    d,r,p,txn,avg,top_bank,bottom_bank,top_camp,top_call = calc_metrics(f)
    
    # KPI Cards with Sparklines
    c1,c2,c3 = st.columns(3)
    c1.metric("Total Disbursed", format_inr(d))
    c1.plotly_chart(sparkline(f.groupby("Disb Month")["Disbursed AMT"].sum()), use_container_width=True)
    c2.metric("Total Revenue", format_inr(r))
    c2.plotly_chart(sparkline(f.groupby("Disb Month")["Total_Revenue"].sum()), use_container_width=True)
    c3.metric("Avg Payout %", f"{p:.2f}%")
    
    # Insights
    st.markdown(f"**Top Bank:** {top_bank} | **Bottom Bank:** {bottom_bank} | **Top Campaign:** {top_camp} | **Top Caller:** {top_call}")
    
    # Charts
    tab1,tab2,tab3 = st.tabs(["Bank","Campaign","Caller"])
    with tab1: st.plotly_chart(plot_bar(f,"Bank",highlight=top_bank))
    with tab2: st.plotly_chart(plot_pie(f,"Campaign"))
    with tab3: st.plotly_chart(plot_bar(f,"Caller",highlight=top_call))
    
    # Trend
    st.subheader("📈 Trend Over Months")
    trend = df.groupby("Disb Month")["Disbursed AMT"].sum().reset_index()
    fig = go.Figure(go.Scatter(x=trend["Disb Month"], y=trend["Disbursed AMT"]/100000, mode="lines+markers"))
    st.plotly_chart(fig)
    
    # Raw Data
    st.subheader("📄 Raw Data")
    st.dataframe(f)
    csv = f.to_csv(index=False).encode("utf-8")
    st.download_button(f"Download {manager}_{month}", data=csv, file_name=f"{manager}_{month}.csv", mime="text/csv")

# Render Dashboards
if dashboard_type=="Single Manager":
    f = df[(df["Manager"]==selected_manager1)&(df["Disb Month"]==selected_month1)]
    render_dashboard(f, selected_manager1, selected_month1)
if dashboard_type=="Comparison":
    f1 = df[(df["Manager"]==selected_manager1)&(df["Disb Month"]==selected_month1)]
    f2 = df[(df["Manager"]==selected_manager2)&(df["Disb Month"]==selected_month2)]
    col1,col2 = st.columns(2)
    with col1: render_dashboard(f1, selected_manager1, selected_month1)
    with col2: render_dashboard(f2, selected_manager2, selected_month2)
