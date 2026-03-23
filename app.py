import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from streamlit_autorefresh import st_autorefresh

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(page_title="Manager Dashboard", layout="wide")

# Auto-refresh every 60 sec
st_autorefresh(interval=60 * 1000, key="refresh")

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
# Sidebar Filters
# -----------------------------
st.sidebar.title("Dashboard Filters")
dashboard_type = st.sidebar.radio("Select Dashboard", ["All Managers", "Single Manager", "Comparison"])
months = sorted(df["Disb Month"].dropna().unique())
selected_month = st.sidebar.selectbox("Select Month", months)

managers = sorted(df["Manager"].dropna().unique())
if dashboard_type in ["Single Manager", "Comparison"]:
    selected_manager1 = st.sidebar.selectbox("Select Manager 1", managers)
    if dashboard_type=="Comparison":
        selected_manager2 = st.sidebar.selectbox("Select Manager 2", managers, index=1)

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
    while len(rest)>2:
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

base_colors = ["#636EFA","#EF553B","#00CC96","#AB63FA","#FFA15A","#19D3F3","#FF6692","#B6E880"]

def get_colors(index_list, top_value):
    colors = []
    for i,val in enumerate(index_list):
        if val==top_value:
            colors.append("#FFD700")
        else:
            colors.append(base_colors[i % len(base_colors)])
    return colors

def plot_bar(f, col, top_value, manager_name, key):
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
    fig.update_layout(title=f"{manager_name} - {col} Distribution", yaxis_title="Amount (L)", template="plotly_white", height=400)
    return fig

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
    agg_df["Avg_Payout_%"] = (agg_df["Total_Revenue"]/agg_df["Total_Disbursed"]*100).round(2)

    # Colorful KPI Cards
    st.subheader("Manager KPIs")
    for idx,row in agg_df.iterrows():
        col1,col2,col3,col4 = st.columns(4)
        col1.metric(f"💰 {row['Manager']} - Disbursed", format_inr(row["Total_Disbursed"]))
        col2.metric(f"📈 Revenue", format_inr(row["Total_Revenue"]))
        col3.metric(f"📝 Transactions", f"{row['Transactions']}")
        col4.metric(f"📊 Avg Payout %", f"{row['Avg_Payout_%']:.2f}%")

    # Interactive Table
    st.subheader("Aggregated Data Table")
    fig_table = go.Figure(data=[go.Table(
        header=dict(values=list(agg_df.columns),
                    fill_color='paleturquoise', align='left'),
        cells=dict(values=[agg_df[col] for col in agg_df.columns],
                   fill_color='lavender', align='left'))
    ])
    fig_table.update_layout(height=500)
    st.plotly_chart(fig_table, width='100%', use_container_width=True, key="all_managers_table")

    st.subheader("Data Preview & Download")
    st.dataframe(agg_df, use_container_width=True)
    st.download_button("Download Data", agg_df.to_csv(index=False), "all_managers.csv", "text/csv")

# -----------------------------
# SINGLE MANAGER DASHBOARD
# -----------------------------
if dashboard_type=="Single Manager":
    st.header(f"📊 {selected_manager1} - {selected_month} Dashboard")
    f = df[(df["Manager"]==selected_manager1)&(df["Disb Month"]==selected_month)]

    if f.empty:
        st.warning("No data available")
    else:
        total_disb,total_rev,avg_payout,txn_count,avg_disb,top_bank,top_campaign,top_caller = calc_metrics(f)
        # KPI Cards
        col1,col2,col3,col4 = st.columns(4)
        col1.metric("💰 Total Disbursed", format_inr(total_disb))
        col2.metric("📈 Total Revenue", format_inr(total_rev))
        col3.metric("📝 Transactions", txn_count)
        col4.metric("📊 Avg Payout %", f"{avg_payout:.2f}%")

        # Charts
        st.plotly_chart(plot_bar(f,"Bank",top_bank,selected_manager1,key="single_bank"), width='100%', use_container_width=True)
        st.plotly_chart(plot_bar(f,"Caller",top_caller,selected_manager1,key="single_caller"), width='100%', use_container_width=True)

        # Campaign Pie
        summary = f.groupby("Campaign")["Disbursed AMT"].sum()
        fig = go.Figure(go.Pie(labels=summary.index, values=summary.values/100000, hole=0.4))
        fig.update_layout(title=f"{selected_manager1} - Campaign Distribution")
        st.plotly_chart(fig, width='100%', use_container_width=True, key="single_campaign")

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
    if selected_manager1==selected_manager2:
        st.warning("Select different managers")
        st.stop()

    f1 = df[(df["Manager"]==selected_manager1)&(df["Disb Month"]==selected_month)]
    f2 = df[(df["Manager"]==selected_manager2)&(df["Disb Month"]==selected_month)]

    d1,r1,p1,txn1,_,top_bank1,top_camp1,top_caller1 = calc_metrics(f1)
    d2,r2,p2,txn2,_,top_bank2,top_camp2,top_caller2 = calc_metrics(f2)

    # KPI Cards side by side
    st.subheader("Manager Comparison KPIs")
    col1,col2,col3,col4 = st.columns(4)
    col1.metric(f"{selected_manager1} - Disbursed", format_inr(d1))
    col2.metric(f"{selected_manager2} - Disbursed", format_inr(d2))
    col3.metric(f"{selected_manager1} - Revenue", format_inr(r1))
    col4.metric(f"{selected_manager2} - Revenue", format_inr(r2))

    col1,col2,col3,col4 = st.columns(4)
    col1.metric(f"{selected_manager1} - Transactions", txn1)
    col2.metric(f"{selected_manager2} - Transactions", txn2)
    col3.metric(f"{selected_manager1} - Avg Payout %", f"{p1:.2f}%")
    col4.metric(f"{selected_manager2} - Avg Payout %", f"{p2:.2f}%")

    # Charts
    st.plotly_chart(plot_bar(f1,"Bank",top_bank1,selected_manager1,key="comp_bank1"), width='100%', use_container_width=True)
    st.plotly_chart(plot_bar(f2,"Bank",top_bank2,selected_manager2,key="comp_bank2"), width='100%', use_container_width=True)

    st.plotly_chart(plot_bar(f1,"Caller",top_caller1,selected_manager1,key="comp_caller1"), width='100%', use_container_width=True)
    st.plotly_chart(plot_bar(f2,"Caller",top_caller2,selected_manager2,key="comp_caller2"), width='100%', use_container_width=True)
