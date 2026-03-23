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

def plot_bar(f, col, top_value, manager_name, key_name):
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
    fig.update_layout(title=f"{manager_name} - {col} Summary",
                      yaxis_title="Amount (L)",
                      template="plotly_white", height=400)
    return fig

# -----------------------------
# Sidebar Filters
# -----------------------------
st.sidebar.title("Filters")
dashboard_type = st.sidebar.radio("Select Dashboard", ["All Managers", "Single Manager", "Comparison"])

managers = sorted(df["Manager"].dropna().unique())
months = sorted(df["Disb Month"].dropna().unique())

selected_month = st.sidebar.selectbox("Select Month", months)

if dashboard_type in ["Single Manager", "Comparison"]:
    selected_manager1 = st.sidebar.selectbox("Select Manager 1", managers)
if dashboard_type=="Comparison":
    selected_manager2 = st.sidebar.selectbox("Select Manager 2", managers, index=1)

# -----------------------------
# ALL MANAGERS DASHBOARD
# -----------------------------
if dashboard_type=="All Managers":
    st.header("📊 All Managers Dashboard")
    filtered_df = df[df["Disb Month"]==selected_month]

    agg_df = filtered_df.groupby(["Vertical","Manager"]).agg(
        Total_Disbursed=("Disbursed AMT","sum"),
        Total_Revenue=("Total_Revenue","sum"),
        Transactions=("Manager","count")
    ).reset_index()

    agg_df["Avg_Payout"] = (agg_df["Total_Revenue"]/agg_df["Total_Disbursed"]*100).round(2)
    agg_df.sort_values("Vertical", inplace=True)

    st.dataframe(agg_df.style.background_gradient(subset=["Total_Disbursed","Total_Revenue","Avg_Payout"], cmap="YlGnBu"))

    st.download_button(
        label="Download CSV",
        data=agg_df.to_csv(index=False),
        file_name=f"all_managers_{selected_month}.csv",
        mime="text/csv"
    )

# -----------------------------
# SINGLE DASHBOARD
# -----------------------------
if dashboard_type=="Single Manager":
    st.header(f"📊 {selected_manager1} - {selected_month} Dashboard")
    f = df[(df["Manager"]==selected_manager1)&(df["Disb Month"]==selected_month)]

    if f.empty:
        st.warning("No data available")
    else:
        total_disb,total_rev,avg_payout,txn_count,avg_disb,top_bank,top_campaign,top_caller = calc_metrics(f)

        # KPI Cards
        col1,col2,col3 = st.columns(3)
        col1.metric("Total Disbursed", format_inr(total_disb))
        col2.metric("Total Revenue", format_inr(total_rev))
        col3.metric("Avg Payout %", f"{avg_payout:.2f}%")

        # Charts
        st.plotly_chart(plot_bar(f,"Bank",top_bank,selected_manager1,"sm_bank"), width='stretch')
        st.plotly_chart(plot_bar(f,"Caller",top_caller,selected_manager1,"sm_caller"), width='stretch')

        # Campaign Pie
        summary = f.groupby("Campaign")["Disbursed AMT"].sum()
        fig = go.Figure(go.Pie(
            labels=summary.index,
            values=summary.values/100000,
            hole=0.4
        ))
        fig.update_layout(title=f"{selected_manager1} - Campaign Distribution")
        st.plotly_chart(fig, width='stretch')

        # Summary
        st.markdown("### 📝 Insights")
        summary_df = pd.DataFrame({
            "Metric":["Top Bank","Top Campaign","Top Caller","Transactions","Avg Disbursed"],
            "Value":[top_bank,top_campaign,top_caller,txn_count,format_inr(avg_disb)]
        })
        st.table(summary_df)

# -----------------------------
# COMPARISON DASHBOARD
# -----------------------------
if dashboard_type=="Comparison":
    st.header("📊 Comparison Dashboard")

    if selected_manager1 == selected_manager2:
        st.warning("Select different managers")
        st.stop()

    f1 = df[(df["Manager"]==selected_manager1)&(df["Disb Month"]==selected_month)]
    f2 = df[(df["Manager"]==selected_manager2)&(df["Disb Month"]==selected_month)]

    d1,r1,p1,txn1,avg1,top_bank1,top_camp1,top_caller1 = calc_metrics(f1)
    d2,r2,p2,txn2,avg2,top_bank2,top_camp2,top_caller2 = calc_metrics(f2)

    # KPI cards
    col1,col2,col3 = st.columns(3)
    col1.metric(f"{selected_manager1} Total Disb", format_inr(d1))
    col2.metric(f"{selected_manager2} Total Disb", format_inr(d2))
    col3.metric("Avg Payout %", f"{p1:.2f}% vs {p2:.2f}%")

    # Charts
    st.plotly_chart(plot_bar(f1,"Bank",top_bank1,selected_manager1,"comp_bank1"), width='stretch')
    st.plotly_chart(plot_bar(f2,"Bank",top_bank2,selected_manager2,"comp_bank2"), width='stretch')

    # Summary table
    summary_df = pd.DataFrame({
        "Metric":["Top Bank","Top Campaign","Top Caller","Transactions","Avg Disbursed"],
        selected_manager1:[top_bank1,top_camp1,top_caller1,txn1,format_inr(avg1)],
        selected_manager2:[top_bank2,top_camp2,top_caller2,txn2,format_inr(avg2)]
    })
    st.table(summary_df)
