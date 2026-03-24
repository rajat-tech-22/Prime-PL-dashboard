import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from streamlit_autorefresh import st_autorefresh

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(page_title="Manager Dashboard", layout="wide")
st_autorefresh(interval=60*1000, key="refresh")  # Auto-refresh every 60s

# -----------------------------
# Load Data
# -----------------------------
@st.cache_data(ttl=60)
def load_data(url):
    df = pd.read_csv(url)
    df.replace("null", None, inplace=True)
    # Ensure columns exist to prevent KeyError
    for col in ["Vertical", "Manager", "Disb Month", "Campaign", "Bank", "Caller", "Disbursed AMT", "Total_Revenue"]:
        if col not in df.columns:
            df[col] = None
    return df

df1_url = "https://docs.google.com/spreadsheets/d/1I1ql5NwFafbWXYkVOvv0yvMM9GKnJ5954R4zif2owGI/export?format=csv"
df2_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRfDuP8FJ8yxoZxPPiKYrxWyP1Brlq7hmyxrkp81_oURiPrCJHqup7Ru8wFoE-pWMEZjZIuH_VBM5_i/pub?gid=2057712936&single=true&output=csv"

df1 = load_data(df1_url)
df2 = load_data(df2_url)

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

def plot_bar(f, col, top_value, manager_name, key_val):
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

def colored_metric(label, value, color="#000000"):
    st.markdown(f"""
        <div style="background-color:{color}; padding:20px; border-radius:10px; text-align:center; color:white; margin-bottom:10px;">
            <h4 style="margin:0">{label}</h4>
            <h2 style="margin:0">{value}</h2>
        </div>
        """, unsafe_allow_html=True)

# -----------------------------
# Sidebar Filters
# -----------------------------
st.sidebar.title("Filters")
dashboard_type = st.sidebar.radio("Select Dashboard", ["All Managers", "Single Manager", "Comparison", "Campaign Performance"])

# -----------------------------
# ALL DASHBOARD FILTERS
# -----------------------------
months1 = sorted(df1["Disb Month"].dropna().unique())
months2 = sorted(df2["Disb Month"].dropna().unique())

if dashboard_type == "All Managers":
    selected_month = st.sidebar.selectbox("Select Month", months1, index=len(months1)-1)
    selected_vertical = st.sidebar.selectbox("Business Vertical", ["All"] + sorted(df1["Vertical"].dropna().unique()))
    filtered_for_campaigns = df1.copy()
    if selected_vertical != "All":
        filtered_for_campaigns = filtered_for_campaigns[filtered_for_campaigns["Vertical"]==selected_vertical]
    if selected_month:
        filtered_for_campaigns = filtered_for_campaigns[filtered_for_campaigns["Disb Month"]==selected_month]
    campaigns_available = sorted(filtered_for_campaigns["Campaign"].dropna().unique())
    selected_campaigns = st.sidebar.multiselect("Campaigns", campaigns_available, default=campaigns_available)

elif dashboard_type == "Single Manager":
    managers = sorted(df1["Manager"].dropna().unique())
    selected_manager = st.sidebar.selectbox("Select Manager", managers)
    selected_month = st.sidebar.selectbox("Select Month", months1, index=len(months1)-1)
    filtered_for_campaigns = df1[(df1["Manager"]==selected_manager)]
    if selected_month:
        filtered_for_campaigns = filtered_for_campaigns[filtered_for_campaigns["Disb Month"]==selected_month]
    campaigns_available = sorted(filtered_for_campaigns["Campaign"].dropna().unique())
    selected_campaigns = st.sidebar.multiselect("Campaigns", campaigns_available, default=campaigns_available)

elif dashboard_type == "Comparison":
    managers = sorted(df1["Manager"].dropna().unique())
    selected_manager1 = st.sidebar.selectbox("Select First Manager", managers)
    selected_month1 = st.sidebar.selectbox("Month for First Manager", months1, index=len(months1)-1)
    selected_manager2 = st.sidebar.selectbox("Select Second Manager", managers)
    selected_month2 = st.sidebar.selectbox("Month for Second Manager", months1, index=len(months1)-1)

elif dashboard_type == "Campaign Performance":
    campaigns_available = sorted(df2["Campaign"].dropna().unique())
    selected_campaigns = st.sidebar.multiselect("Select Campaign(s)", campaigns_available, default=campaigns_available)
    selected_month_cp = st.sidebar.selectbox("Select Month", months2, index=len(months2)-1)

# -----------------------------
# DASHBOARDS
# -----------------------------

# 1. All Managers
if dashboard_type == "All Managers":
    st.header("📊 Enterprise Overview")
    filtered_df = df1.copy()
    if selected_vertical != "All":
        filtered_df = filtered_df[filtered_df["Vertical"]==selected_vertical]
    if selected_month:
        filtered_df = filtered_df[filtered_df["Disb Month"]==selected_month]
    if selected_campaigns:
        filtered_df = filtered_df[filtered_df["Campaign"].isin(selected_campaigns)]
    
    agg_df = filtered_df.groupby(["Vertical","Manager"]).agg(
        Total_Disbursed=("Disbursed AMT","sum"),
        Total_Revenue=("Total_Revenue","sum"),
        Transactions=("Manager","count")
    ).reset_index()
    agg_df["Avg_Payout"] = (agg_df["Total_Revenue"]/agg_df["Total_Disbursed"]*100).round(2)
    agg_df.sort_values(["Vertical","Total_Disbursed"], ascending=[True,False], inplace=True)
    agg_df["Total_Disbursed"] = agg_df["Total_Disbursed"].apply(format_inr)
    agg_df["Total_Revenue"] = agg_df["Total_Revenue"].apply(format_inr)

    st.dataframe(agg_df, use_container_width=True, height=500)

# 2. Single Manager
elif dashboard_type == "Single Manager":
    st.header(f"📈 Insights - {selected_manager}")
    f = df1[(df1["Manager"]==selected_manager)&(df1["Disb Month"]==selected_month)]
    if selected_campaigns:
        f = f[f["Campaign"].isin(selected_campaigns)]
    if f.empty:
        st.warning("No data available")
    else:
        total_disb,total_rev,avg_payout,txn_count,avg_disb,top_bank,top_campaign,top_caller = calc_metrics(f)
        col1,col2,col3,col4 = st.columns(4)
        with col1: colored_metric("Total Disbursed", format_inr(total_disb), "#636EFA")
        with col2: colored_metric("Total Revenue", format_inr(total_rev), "#00CC96")
        with col3: colored_metric("Avg Payout %", f"{avg_payout:.2f}%", "#EF553B")
        with col4: colored_metric("Transactions", txn_count, "#FFA15A")
        st.plotly_chart(plot_bar(f,"Bank",top_bank,selected_manager,key_val="bank1"), use_container_width=True)
        st.plotly_chart(plot_bar(f,"Caller",top_caller,selected_manager,key_val="caller1"), use_container_width=True)

# 3. Comparison
elif dashboard_type == "Comparison":
    st.header("⚖️ Manager Benchmark")
    f1 = df1[(df1["Manager"]==selected_manager1)&(df1["Disb Month"]==selected_month1)]
    f2 = df1[(df1["Manager"]==selected_manager2)&(df1["Disb Month"]==selected_month2)]
    d1,r1,p1,txn1,avg1,top_bank1,top_camp1,top_caller1 = calc_metrics(f1)
    d2,r2,p2,txn2,avg2,top_bank2,top_camp2,top_caller2 = calc_metrics(f2)
    
    col1,col2 = st.columns(2)
    with col1: colored_metric(selected_manager1, f"Disb: {format_inr(d1)}\nRev: {format_inr(r1)}\nAvg: {p1:.2f}%\nTxn: {txn1}", "#636EFA")
    with col2: colored_metric(selected_manager2, f"Disb: {format_inr(d2)}\nRev: {format_inr(r2)}\nAvg: {p2:.2f}%\nTxn: {txn2}", "#00CC96")

# 4. Campaign Performance
elif dashboard_type == "Campaign Performance":
    st.header("📊 Campaign Performance")
    f = df2.copy()
    if selected_month_cp:
        f = f[f["Disb Month"]==selected_month_cp]
    if selected_campaigns:
        f = f[f["Campaign"].isin(selected_campaigns)]
    if f.empty:
        st.warning("No data available")
    else:
        cp_agg = f.groupby("Manager").agg(
            Total_Disbursed=("Disbursed AMT","sum"),
            Total_Count=("Disbursed AMT","count")
        ).reset_index()
        st.dataframe(cp_agg, use_container_width=True, height=400)
