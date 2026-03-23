import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from streamlit_autorefresh import st_autorefresh

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(page_title="Manager Dashboard", layout="wide")

# 🔄 Auto Refresh every 60 sec
st_autorefresh(interval=60 * 1000, key="refresh")

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
    return total_disb,total_rev,avg_payout,txn_count,avg_disb,top_bank,top_campaign,top_caller

def plot_bar(f, col, top_value, manager_name, key_suffix):
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
    st.plotly_chart(fig, use_container_width=True, key=f"{key_suffix}_{col}")

def sparkline(data, color="#FFFFFF"):
    fig = go.Figure(go.Scatter(
        y=data,
        mode='lines+markers',
        line=dict(color=color, width=2),
        marker=dict(size=4),
    ))
    fig.update_layout(
        margin=dict(l=0,r=0,t=0,b=0),
        height=50,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False)
    )
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

        # KPI Cards with mini sparklines
        kpi_labels = ["Total Disbursed","Total Revenue","Avg Payout %"]
        kpi_values = [total_disb,total_rev,avg_payout]
        kpi_colors = ["#636EFA","#EF553B","#00CC96"]
        icons = ["💰","📈","⚡"]

        cols = st.columns(3)
        for i, col_obj in enumerate(cols):
            with col_obj:
                st.markdown(f"""
                    <div style="background-color:{kpi_colors[i]}; padding:20px; border-radius:15px; color:white; text-align:center;">
                        <h3>{icons[i]} {kpi_labels[i]}</h3>
                        <h2>{format_inr(kpi_values[i]) if i<2 else f'{kpi_values[i]:.2f}%'} </h2>
                    </div>
                    """, unsafe_allow_html=True)
                # Mini sparkline
                trend_data = f["Disbursed AMT"].rolling(3).sum() if i==0 else f["Total_Revenue"].rolling(3).sum() if i==1 else f["Total_Revenue"].pct_change().fillna(0)
                st.plotly_chart(sparkline(trend_data), use_container_width=True, key=f"kpi_spark_{i}")

        # Charts
        plot_bar(f,"Bank",top_bank,selected_manager1,"single")
        plot_bar(f,"Caller",top_caller,selected_manager1,"single")

        # Campaign Pie
        summary = f.groupby("Campaign")["Disbursed AMT"].sum()
        fig_pie = go.Figure(go.Pie(
            labels=summary.index,
            values=summary.values/100000,
            hole=0.4
        ))
        st.plotly_chart(fig_pie, use_container_width=True, key="single_campaign_pie")

        # Summary
        st.markdown("### 📝 Insights")
        st.write(f"Top Bank: {top_bank}")
        st.write(f"Top Campaign: {top_campaign}")
        st.write(f"Top Caller: {top_caller}")
        st.write(f"Transactions: {txn_count}")
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

    d1,r1,p1,_,_,top_bank1,top_camp1,top_caller1 = calc_metrics(f1)
    d2,r2,p2,_,_,top_bank2,top_camp2,top_caller2 = calc_metrics(f2)

    col1,col2,col3 = st.columns(3)
    col1.metric(selected_manager1, format_inr(d1))
    col2.metric(selected_manager2, format_inr(d2))
    col3.metric("Payout %", f"{p1:.2f}% vs {p2:.2f}%")

    # Charts
    plot_bar(f1,"Bank",top_bank1,selected_manager1,"comp1")
    plot_bar(f1,"Caller",top_caller1,selected_manager1,"comp1")
    plot_bar(f2,"Bank",top_bank2,selected_manager2,"comp2")
    plot_bar(f2,"Caller",top_caller2,selected_manager2,"comp2")

    # Campaign Pies
    summary1 = f1.groupby("Campaign")["Disbursed AMT"].sum()
    fig_camp1 = go.Figure(go.Pie(labels=summary1.index, values=summary1.values/100000, hole=0.4))
    st.plotly_chart(fig_camp1, use_container_width=True, key="comp_camp1")

    summary2 = f2.groupby("Campaign")["Disbursed AMT"].sum()
    fig_camp2 = go.Figure(go.Pie(labels=summary2.index, values=summary2.values/100000, hole=0.4))
    st.plotly_chart(fig_camp2, use_container_width=True, key="comp_camp2")

    # Winner
    winner = selected_manager1 if d1 > d2 else selected_manager2
    st.success(f"🏆 Top Performer: {winner}")
