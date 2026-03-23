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
# Sidebar Filters
# -----------------------------
st.sidebar.title("Dashboard Options")
dashboard_type = st.sidebar.radio("Select Dashboard", ["All Managers", "Single Manager", "Comparison"])
months = sorted(df["Disb Month"].dropna().unique())
selected_month = st.sidebar.selectbox("Select Month", months)

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

def plot_bar(f, col, top_value, manager_name):
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
    fig.update_layout(title=f"{manager_name} - {col} Disbursement", yaxis_title="Amount (L)", template="plotly_white", height=400)
    return fig

# -----------------------------
# ALL MANAGERS DASHBOARD
# -----------------------------
if dashboard_type=="All Managers":
    st.header(f"📊 All Managers Dashboard - {selected_month}")
    filtered_df = df[df["Disb Month"]==selected_month]

    # Aggregate per manager
    agg_df = filtered_df.groupby("Manager").agg(
        Total_Disbursed=("Disbursed AMT","sum"),
        Total_Revenue=("Total_Revenue","sum"),
        Transactions=("Manager","count")
    ).reset_index()
    agg_df["Avg_Payout_%"] = (agg_df["Total_Revenue"]/agg_df["Total_Disbursed"]*100).round(2)
    agg_df = agg_df.sort_values(by="Total_Disbursed", ascending=False)
    agg_df.insert(0, "No", range(1, len(agg_df)+1))

    # Display interactive table
    st.dataframe(agg_df.style.format({
        "Total_Disbursed":"₹{:,.0f}",
        "Total_Revenue":"₹{:,.0f}",
        "Avg_Payout_%":"{:.2f}%"
    }), width='stretch')

    # Download CSV
    csv_all = agg_df.to_csv(index=False).encode('utf-8')
    st.download_button("Download All Managers Data CSV", csv_all, file_name=f"all_managers_{selected_month}.csv", mime='text/csv')

# -----------------------------
# SINGLE MANAGER DASHBOARD
# -----------------------------
if dashboard_type=="Single Manager":
    st.header("📊 Single Manager Dashboard")
    managers = sorted(df["Manager"].dropna().unique())
    selected_manager = st.sidebar.selectbox("Select Manager", managers)

    f = df[(df["Manager"]==selected_manager)&(df["Disb Month"]==selected_month)]
    if f.empty:
        st.warning("No data available")
    else:
        total_disb,total_rev,avg_payout,txn_count,avg_disb,top_bank,top_campaign,top_caller = calc_metrics(f)

        # KPI Cards
        col1,col2,col3,col4 = st.columns(4)
        col1.metric("Total Disbursed", format_inr(total_disb))
        col2.metric("Total Revenue", format_inr(total_rev))
        col3.metric("Transactions", txn_count)
        col4.metric("Avg Payout %", f"{avg_payout:.2f}%")

        # Charts
        st.plotly_chart(plot_bar(f,"Bank",top_bank,selected_manager), width='stretch', use_container_width=None, key="sm_bank")
        st.plotly_chart(plot_bar(f,"Caller",top_caller,selected_manager), width='stretch', use_container_width=None, key="sm_caller")

        # Campaign Pie
        summary = f.groupby("Campaign")["Disbursed AMT"].sum()
        fig = go.Figure(go.Pie(labels=summary.index, values=summary.values/100000, hole=0.4))
        fig.update_layout(title=f"{selected_manager} - Campaign Distribution")
        st.plotly_chart(fig, width='stretch', use_container_width=None, key="sm_pie")

        # Summary Insights
        st.markdown("### 📝 Insights")
        st.write(f"Top Bank: {top_bank}")
        st.write(f"Top Campaign: {top_campaign}")
        st.write(f"Top Caller: {top_caller}")
        st.write(f"Transactions: {txn_count}")
        st.write(f"Avg Disbursed: {format_inr(avg_disb)}")

        # Download CSV
        csv_single = f.to_csv(index=False).encode('utf-8')
        st.download_button("Download Single Manager Data CSV", csv_single, file_name=f"{selected_manager}_{selected_month}.csv", mime='text/csv')

# -----------------------------
# COMPARISON DASHBOARD
# -----------------------------
if dashboard_type=="Comparison":
    st.header("📊 Comparison Dashboard")
    managers = sorted(df["Manager"].dropna().unique())
    selected_manager1 = st.sidebar.selectbox("Select Manager 1", managers, index=0)
    selected_manager2 = st.sidebar.selectbox("Select Manager 2", managers, index=1)

    if selected_manager1 == selected_manager2:
        st.warning("Select different managers")
        st.stop()

    f1 = df[(df["Manager"]==selected_manager1)&(df["Disb Month"]==selected_month)]
    f2 = df[(df["Manager"]==selected_manager2)&(df["Disb Month"]==selected_month)]

    d1,r1,p1,txn1,avg1,top_bank1,top_camp1,top_caller1 = calc_metrics(f1)
    d2,r2,p2,txn2,avg2,top_bank2,top_camp2,top_caller2 = calc_metrics(f2)

    # Side-by-side KPI Cards
    col1,col2,col3,col4 = st.columns(4)
    col1.metric(selected_manager1, format_inr(d1))
    col2.metric(selected_manager2, format_inr(d2))
    col3.metric("Transactions", f"{txn1} vs {txn2}")
    delta = p1 - p2
    delta_text = f"{p1:.2f}% vs {p2:.2f}% ({'▲' if delta>0 else '▼'})"
    col4.metric("Avg Payout %", delta_text)

    # Charts
    st.plotly_chart(plot_bar(f1,"Bank",top_bank1,selected_manager1), width='stretch', use_container_width=None, key="cmp_bank1")
    st.plotly_chart(plot_bar(f2,"Bank",top_bank2,selected_manager2), width='stretch', use_container_width=None, key="cmp_bank2")

    st.plotly_chart(plot_bar(f1,"Caller",top_caller1,selected_manager1), width='stretch', use_container_width=None, key="cmp_caller1")
    st.plotly_chart(plot_bar(f2,"Caller",top_caller2,selected_manager2), width='stretch', use_container_width=None, key="cmp_caller2")

    # Campaign Pie
    summary1 = f1.groupby("Campaign")["Disbursed AMT"].sum()
    summary2 = f2.groupby("Campaign")["Disbursed AMT"].sum()
    fig1 = go.Figure(go.Pie(labels=summary1.index, values=summary1.values/100000, hole=0.4))
    fig1.update_layout(title=f"{selected_manager1} - Campaign Distribution")
    st.plotly_chart(fig1, width='stretch', use_container_width=None, key="cmp_pie1")

    fig2 = go.Figure(go.Pie(labels=summary2.index, values=summary2.values/100000, hole=0.4))
    fig2.update_layout(title=f"{selected_manager2} - Campaign Distribution")
    st.plotly_chart(fig2, width='stretch', use_container_width=None, key="cmp_pie2")

    # Summary Insights
    st.markdown("### 📝 Insights")
    st.write(f"**{selected_manager1}**: Top Bank: {top_bank1}, Top Campaign: {top_camp1}, Top Caller: {top_caller1}, Avg Disb: {format_inr(avg1)}")
    st.write(f"**{selected_manager2}**: Top Bank: {top_bank2}, Top Campaign: {top_camp2}, Top Caller: {top_caller2}, Avg Disb: {format_inr(avg2)}")

    # Download CSVs
    csv_cmp1 = f1.to_csv(index=False).encode('utf-8')
    csv_cmp2 = f2.to_csv(index=False).encode('utf-8')
    st.download_button(f"Download {selected_manager1} CSV", csv_cmp1, file_name=f"{selected_manager1}_{selected_month}.csv", mime='text/csv')
    st.download_button(f"Download {selected_manager2} CSV", csv_cmp2, file_name=f"{selected_manager2}_{selected_month}.csv", mime='text/csv')
