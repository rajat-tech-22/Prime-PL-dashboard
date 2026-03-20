import streamlit as st
import pandas as pd
import plotly.graph_objs as go

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(page_title="Manager Dashboard", layout="wide")

# -----------------------------
# Load CSV
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("data.csv")
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

def plot_bar(f, col, top_value, manager_name):
    summary = f.groupby(col)["Disbursed AMT"].sum()
    colors = []
    for val in summary.index:
        colors.append("#FFD700" if val==top_value else base_colors[list(summary.index).index(val)%len(base_colors)])
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

def delta_color(val):
    return "green" if val>=0 else "red"

def delta_str(val):
    sign = "+" if val>=0 else ""
    return f"{sign}{val:.2f}"

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
# SINGLE MANAGER DASHBOARD
# -----------------------------
if dashboard_type=="Single Manager":
    st.header(f"📊 {selected_manager1} - {selected_month1} Dashboard")
    f = df[(df["Manager"]==selected_manager1)&(df["Disb Month"]==selected_month1)]
    if f.empty:
        st.warning("No data available")
    else:
        total_disb,total_rev,avg_payout,txn_count,avg_disb,top_bank,top_campaign,top_caller = calc_metrics(f)

        # KPI Cards
        kpi_col1,kpi_col2,kpi_col3 = st.columns(3)
        kpi_col1.markdown(f"<div style='background:#BBDEFB;padding:20px;border-radius:12px;text-align:center'><b>Total Disbursed</b><br>{format_inr(total_disb)}</div>", unsafe_allow_html=True)
        kpi_col2.markdown(f"<div style='background:#FFE082;padding:20px;border-radius:12px;text-align:center'><b>Total Revenue</b><br>{format_inr(total_rev)}</div>", unsafe_allow_html=True)
        kpi_col3.markdown(f"<div style='background:#C8E6C9;padding:20px;border-radius:12px;text-align:center'><b>Avg Payout %</b><br>{avg_payout:.2f}%</div>", unsafe_allow_html=True)

        # Charts
        tab1,tab2,tab3 = st.tabs(["🏦 Bank-wise","📢 Campaign-wise","📞 Caller-wise"])
        with tab1: st.plotly_chart(plot_bar(f,"Bank",top_bank,selected_manager1), use_container_width=True)
        with tab2:
            summary = f.groupby("Campaign")["Disbursed AMT"].sum()
            colors = [base_colors[i%len(base_colors)] for i in range(len(summary))]
            fig = go.Figure(go.Pie(labels=summary.index, values=summary.values/100000, hole=0.4, marker=dict(colors=colors)))
            st.plotly_chart(fig, use_container_width=True)
        with tab3: st.plotly_chart(plot_bar(f,"Caller",top_caller,selected_manager1), use_container_width=True)

# -----------------------------
# COMPARISON DASHBOARD SIDE-BY-SIDE WITH KPI DELTA
# -----------------------------
if dashboard_type=="Comparison":
    f1 = df[(df["Manager"]==selected_manager1)&(df["Disb Month"]==selected_month1)]
    f2 = df[(df["Manager"]==selected_manager2)&(df["Disb Month"]==selected_month2)]

    col1,col2 = st.columns(2)

    # Calculate metrics
    if not f1.empty: d1,r1,p1,txn1,avg1,top_bank1,top_camp1,top_caller1 = calc_metrics(f1)
    if not f2.empty: d2,r2,p2,txn2,avg2,top_bank2,top_camp2,top_caller2 = calc_metrics(f2)

    # KPI delta function
    def kpi_with_delta(val1,val2,label,month):
        delta = val1-val2
        color = delta_color(delta)
        return f"<div style='background:#E0E0E0;padding:15px;border-radius:12px;text-align:center'><b>{label} ({month})</b><br>{format_inr(val1)} <span style='color:{color}'>({delta_str(delta)})</span></div>"

    # Manager 1 Column
    with col1:
        st.subheader(f"{selected_manager1} - {selected_month1}")
        if f1.empty:
            st.warning("No data")
        else:
            st.markdown(kpi_with_delta(d1,d2,"Total Disbursed",selected_month1), unsafe_allow_html=True)
            st.markdown(kpi_with_delta(r1,r2,"Total Revenue",selected_month1), unsafe_allow_html=True)
            st.markdown(kpi_with_delta(p1,p2,"Avg Payout %",selected_month1), unsafe_allow_html=True)
            st.plotly_chart(plot_bar(f1,"Bank",top_bank1,selected_manager1), use_container_width=True)
            summary = f1.groupby("Campaign")["Disbursed AMT"].sum()
            colors = [base_colors[i%len(base_colors)] for i in range(len(summary))]
            fig = go.Figure(go.Pie(labels=summary.index, values=summary.values/100000, hole=0.4, marker=dict(colors=colors)))
            st.plotly_chart(fig, use_container_width=True)
            st.plotly_chart(plot_bar(f1,"Caller",top_caller1,selected_manager1), use_container_width=True)

    # Manager 2 Column
    with col2:
        st.subheader(f"{selected_manager2} - {selected_month2}")
        if f2.empty:
            st.warning("No data")
        else:
            st.markdown(kpi_with_delta(d2,d1,"Total Disbursed",selected_month2), unsafe_allow_html=True)
            st.markdown(kpi_with_delta(r2,r1,"Total Revenue",selected_month2), unsafe_allow_html=True)
            st.markdown(kpi_with_delta(p2,p1,"Avg Payout %",selected_month2), unsafe_allow_html=True)
            st.plotly_chart(plot_bar(f2,"Bank",top_bank2,selected_manager2), use_container_width=True)
            summary = f2.groupby("Campaign")["Disbursed AMT"].sum()
            colors = [base_colors[i%len(base_colors)] for i in range(len(summary))]
            fig = go.Figure(go.Pie(labels=summary.index, values=summary.values/100000, hole=0.4, marker=dict(colors=colors)))
            st.plotly_chart(fig, use_container_width=True)
            st.plotly_chart(plot_bar(f2,"Caller",top_caller2,selected_manager2), use_container_width=True)
