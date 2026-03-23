import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from streamlit_autorefresh import st_autorefresh

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(page_title="Manager Dashboard", layout="wide")

# Auto refresh every 60 sec
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
        name=manager_name
    ))
    fig.update_layout(
        yaxis_title="Amount (L)",
        template="plotly_white",
        height=400,
        title=f"{manager_name} - {col} Summary"
    )
    return fig

# -----------------------------
# Sidebar Filters
# -----------------------------
st.sidebar.title("Filters")
dashboard_type = st.sidebar.radio("Select Dashboard", ["All Managers", "Single Manager", "Comparison"])

verticals = sorted(df["Vertical"].dropna().unique())
managers = sorted(df["Manager"].dropna().unique())
months = sorted(df["Disb Month"].dropna().unique())

selected_vertical = st.sidebar.selectbox("Select Vertical", ["All"] + verticals)
selected_manager1 = st.sidebar.selectbox("Select Manager 1", managers)
selected_month1 = st.sidebar.selectbox("Select Month 1", months)

if dashboard_type=="Comparison":
    selected_manager2 = st.sidebar.selectbox("Select Manager 2", managers, index=1)
    selected_month2 = st.sidebar.selectbox("Select Month 2", months, index=1)

# -----------------------------
# ALL MANAGERS DASHBOARD
# -----------------------------
if dashboard_type=="All Managers":
    st.header("📊 All Managers Dashboard")
    filtered_df = df.copy()
    if selected_vertical != "All":
        filtered_df = filtered_df[filtered_df["Vertical"]==selected_vertical]
    if selected_month1:
        filtered_df = filtered_df[filtered_df["Disb Month"]==selected_month1]

    # Aggregate by Vertical + Manager
    agg_df = filtered_df.groupby(["Vertical","Manager"]).agg(
        Total_Disbursed=("Disbursed AMT","sum"),
        Total_Revenue=("Total_Revenue","sum"),
        Transactions=("Manager","count")
    ).reset_index()
    agg_df["Avg_Payout"] = (agg_df["Total_Revenue"]/agg_df["Total_Disbursed"]*100).round(2)

    # Sort by Vertical
    agg_df.sort_values(["Vertical","Total_Disbursed"], ascending=[True,False], inplace=True)

    # Add color column
    agg_df["color"] = ["#FDEBD0" if x%2==0 else "#D6EAF8" for x in range(len(agg_df))]

    # Display as interactive table
    st.markdown("### Manager-wise Performance Table")
    for i,row in agg_df.iterrows():
        st.markdown(f"""
        <div style='background-color:{row.color};padding:10px;border-radius:5px;margin-bottom:2px'>
        <b>Vertical:</b> {row.Vertical} | <b>Manager:</b> {row.Manager} | 
        <b>Total Disbursed:</b> {format_inr(row.Total_Disbursed)} | 
        <b>Total Revenue:</b> {format_inr(row.Total_Revenue)} | 
        <b>Avg Payout %:</b> {row.Avg_Payout} | 
        <b>Transactions:</b> {row.Transactions}
        </div>
        """, unsafe_allow_html=True)
    
    # Download CSV
    st.download_button(
        label="Download CSV",
        data=agg_df.drop(columns="color").to_csv(index=False),
        file_name="all_managers.csv",
        mime="text/csv"
    )

# -----------------------------
# SINGLE MANAGER DASHBOARD
# -----------------------------
if dashboard_type=="Single Manager":
    st.header(f"📊 {selected_manager1} - {selected_month1} Dashboard")

    f = df[(df["Manager"]==selected_manager1)&(df["Disb Month"]==selected_month1)]
    if selected_vertical != "All":
        f = f[f["Vertical"]==selected_vertical]

    if f.empty:
        st.warning("No data available")
    else:
        total_disb,total_rev,avg_payout,txn_count,avg_disb,top_bank,top_campaign,top_caller = calc_metrics(f)

        # KPI Cards
        col1,col2,col3,col4 = st.columns(4)
        col1.metric("Total Disbursed", format_inr(total_disb))
        col2.metric("Total Revenue", format_inr(total_rev))
        col3.metric("Avg Payout %", f"{avg_payout:.2f}%")
        col4.metric("Transactions", txn_count)

        # Charts
        st.plotly_chart(plot_bar(f,"Bank",top_bank,selected_manager1,"bank_chart"), width='stretch')
        st.plotly_chart(plot_bar(f,"Caller",top_caller,selected_manager1,"caller_chart"), width='stretch')

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
    if selected_vertical != "All":
        f1 = f1[f1["Vertical"]==selected_vertical]
        f2 = f2[f2["Vertical"]==selected_vertical]

    d1,r1,p1,txn1,avg1,top_bank1,top_camp1,top_caller1 = calc_metrics(f1)
    d2,r2,p2,txn2,avg2,top_bank2,top_camp2,top_caller2 = calc_metrics(f2)

    # KPI Cards side by side
    col1,col2,col3,col4 = st.columns(4)
    col1.metric(f"{selected_manager1} - Total Disbursed", format_inr(d1))
    col2.metric(f"{selected_manager2} - Total Disbursed", format_inr(d2))
    col3.metric(f"{selected_manager1} - Avg Payout %", f"{p1:.2f}%")
    col4.metric(f"{selected_manager2} - Avg Payout %", f"{p2:.2f}%")

    col1,col2,col3,col4 = st.columns(4)
    col1.metric(f"{selected_manager1} - Transactions", txn1)
    col2.metric(f"{selected_manager2} - Transactions", txn2)
    col3.metric(f"{selected_manager1} - Avg Disbursed", format_inr(avg1))
    col4.metric(f"{selected_manager2} - Avg Disbursed", format_inr(avg2))

    # Charts
    st.plotly_chart(plot_bar(f1,"Bank",top_bank1,selected_manager1,"bank1_chart"), width='stretch')
    st.plotly_chart(plot_bar(f2,"Bank",top_bank2,selected_manager2,"bank2_chart"), width='stretch')
