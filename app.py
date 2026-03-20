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

def plot_bar(f, col, top_n=3):
    summary = f.groupby(col)["Disbursed AMT"].sum().sort_values(ascending=False)
    colors = [ "#FFD700" if i<top_n else base_colors[i%len(base_colors)] for i in range(len(summary))]
    fig = go.Figure(go.Bar(
        x=summary.index,
        y=summary.values/100000,
        text=[f"{v/100000:.2f}L" for v in summary.values],
        textposition="auto",
        marker_color=colors
    ))
    fig.update_layout(yaxis_title="Amount (L)", template="plotly_white", height=400)
    return fig

def plot_line_trend(df, col="Disb Month"):
    trend = df.groupby(col)["Disbursed AMT"].sum()
    fig = go.Figure(go.Scatter(x=trend.index, y=trend.values/100000, mode="lines+markers", line=dict(color="#636EFA")))
    fig.update_layout(yaxis_title="Amount (L)", template="plotly_white", height=400)
    return fig

# -----------------------------
# Sidebar Filters
# -----------------------------
st.sidebar.title("Dashboard Filters")
dashboard_type = st.sidebar.radio("Select Dashboard", ["Single Manager", "Comparison"])

managers = sorted(df["Manager"].dropna().unique())
months = sorted(df["Disb Month"].dropna().unique())

selected_managers = st.sidebar.multiselect("Select Manager(s)", managers, default=managers[:1])
selected_months = st.sidebar.multiselect("Select Month(s)", months, default=months[:1])

# -----------------------------
# SINGLE DASHBOARD
# -----------------------------
if dashboard_type=="Single Manager" and selected_managers and selected_months:
    selected_manager = selected_managers[0]
    selected_month = selected_months[0]
    st.header(f"📊 {selected_manager} - {selected_month} Dashboard")
    f = df[(df["Manager"]==selected_manager)&(df["Disb Month"]==selected_month)]
    
    if f.empty:
        st.warning("No data available")
    else:
        total_disb,total_rev,avg_payout,txn_count,avg_disb,top_bank,top_campaign,top_caller = calc_metrics(f)

        # KPI Cards with arrows
        last_month = months[max(0, months.index(selected_month)-1)]
        f_prev = df[(df["Manager"]==selected_manager)&(df["Disb Month"]==last_month)]
        prev_disb = f_prev["Disbursed AMT"].sum() if not f_prev.empty else 0
        growth = (total_disb-prev_disb)/prev_disb*100 if prev_disb else 0
        arrow = "🔺" if growth>=0 else "🔻"
        
        kpi_col1,kpi_col2,kpi_col3 = st.columns(3)
        kpi_col1.markdown(f"<b>Total Disbursed</b><br>{format_inr(total_disb)} {arrow} {abs(growth):.1f}%", unsafe_allow_html=True)
        kpi_col2.markdown(f"<b>Total Revenue</b><br>{format_inr(total_rev)}", unsafe_allow_html=True)
        kpi_col3.markdown(f"<b>Avg Payout %</b><br>{avg_payout:.2f}%", unsafe_allow_html=True)

        # Tabs
        tab1,tab2,tab3 = st.tabs(["🏦 Bank-wise","📢 Campaign-wise","📞 Caller-wise"])
        with tab1: st.plotly_chart(plot_bar(f,"Bank"), use_container_width=True)
        with tab2:
            summary = f.groupby("Campaign")["Disbursed AMT"].sum()
            colors = [base_colors[i%len(base_colors)] for i in range(len(summary))]
            fig = go.Figure(go.Pie(labels=summary.index, values=summary.values/100000, hole=0.4, marker=dict(colors=colors)))
            st.plotly_chart(fig, use_container_width=True)
        with tab3: st.plotly_chart(plot_bar(f,"Caller"), use_container_width=True)

        # Trend
        st.subheader("📈 Monthly Trend")
        st.plotly_chart(plot_line_trend(df[df["Manager"]==selected_manager]), use_container_width=True)

# -----------------------------
# COMPARISON DASHBOARD
# -----------------------------
if dashboard_type=="Comparison" and len(selected_managers)>=2 and len(selected_months)>=2:
    manager1, manager2 = selected_managers[:2]
    month1, month2 = selected_months[:2]
    st.header(f"📊 Comparison: {manager1} vs {manager2}")
    f1 = df[(df["Manager"]==manager1)&(df["Disb Month"]==month1)]
    f2 = df[(df["Manager"]==manager2)&(df["Disb Month"]==month2)]
    
    if f1.empty and f2.empty:
        st.warning("No data for selected managers/months")
    else:
        # KPIs side by side
        d1,r1,p1,txn1,avg1,top_bank1,top_camp1,top_call1 = calc_metrics(f1)
        d2,r2,p2,txn2,avg2,top_bank2,top_camp2,top_call2 = calc_metrics(f2)
        col1,col2,col3 = st.columns(3)
        col1.markdown(f"<b>{manager1} Total Disbursed</b><br>{format_inr(d1)}", unsafe_allow_html=True)
        col2.markdown(f"<b>{manager2} Total Disbursed</b><br>{format_inr(d2)}", unsafe_allow_html=True)
        col3.markdown(f"<b>Avg Payout %</b><br>{p1:.2f}% vs {p2:.2f}%", unsafe_allow_html=True)

        # Charts
        tab1,tab2,tab3 = st.tabs(["🏦 Bank-wise","📢 Campaign-wise","📞 Caller-wise"])
        with tab1:
            keys = sorted(set(f1["Bank"]).union(set(f2["Bank"])))
            fig = go.Figure()
            for k in keys:
                fig.add_bar(x=[k], y=[f1.groupby("Bank")["Disbursed AMT"].sum().get(k,0)/100000], name=manager1, marker_color="#636EFA", width=0.4)
                fig.add_bar(x=[k], y=[f2.groupby("Bank")["Disbursed AMT"].sum().get(k,0)/100000], name=manager2, marker_color="#EF553B", width=0.4)
            fig.update_layout(barmode='group', yaxis_title="Amount (L)", template="plotly_white", height=450)
            st.plotly_chart(fig, use_container_width=True)
