import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from streamlit_autorefresh import st_autorefresh

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(page_title="Manager Dashboard", layout="wide")
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
    return ["#FFD700" if val == top_value else base_colors[i % len(base_colors)] for i, val in enumerate(index_list)]

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
    if f.empty:
        return go.Figure()

    summary = f.groupby(col)["Disbursed AMT"].sum()
    colors = get_colors(summary.index, top_value)

    fig = go.Figure(go.Bar(
        x=summary.index,
        y=summary.values/100000,
        text=[f"{v/100000:.2f}L" for v in summary.values],
        textposition="auto",
        marker_color=colors
    ))

    fig.update_layout(
        yaxis_title="Amount (L)",
        template="plotly_white",
        height=400,
        title=f"{manager_name} - {col} Summary"
    )
    return fig

def colored_metric(label, value, color="#000"):
    st.markdown(f"""
    <div style="background:{color}; padding:15px; border-radius:10px; text-align:center; color:white;">
        <h4>{label}</h4>
        <h2>{value}</h2>
    </div>
    """, unsafe_allow_html=True)

# -----------------------------
# Sidebar Filters (FIXED)
# -----------------------------
st.sidebar.title("Filters")

dashboard_type = st.sidebar.radio(
    "Select Dashboard",
    ["All Managers", "Single Manager", "Comparison"]
)

verticals = ["All"] + sorted(df["Vertical"].dropna().unique())
months = sorted(df["Disb Month"].dropna().unique())
managers = sorted(df["Manager"].dropna().unique())

latest_month_index = len(months)-1 if months else 0

# ALL MANAGERS
if dashboard_type == "All Managers":
    selected_month = st.sidebar.selectbox("Select Month", months, index=latest_month_index)
    selected_vertical = st.sidebar.selectbox("Business Vertical", verticals)

    temp_df = df.copy()

    if selected_vertical != "All":
        temp_df = temp_df[temp_df["Vertical"] == selected_vertical]

    if selected_month:
        temp_df = temp_df[temp_df["Disb Month"] == selected_month]

    campaigns_available = sorted(temp_df["Campaign"].dropna().unique())

    selected_campaigns = st.sidebar.multiselect(
        "Campaigns",
        campaigns_available,
        default=campaigns_available
    )

# SINGLE MANAGER
elif dashboard_type == "Single Manager":
    selected_manager = st.sidebar.selectbox("Select Manager", managers)
    selected_month = st.sidebar.selectbox("Select Month", months, index=latest_month_index)

    temp_df = df[df["Manager"] == selected_manager]

    if selected_month:
        temp_df = temp_df[temp_df["Disb Month"] == selected_month]

    campaigns_available = sorted(temp_df["Campaign"].dropna().unique())

    selected_campaigns = st.sidebar.multiselect(
        "Campaigns",
        campaigns_available,
        default=campaigns_available
    )

# COMPARISON
elif dashboard_type == "Comparison":
    col1, col2 = st.sidebar.columns(2)

    with col1:
        selected_manager1 = st.selectbox("Manager 1", managers)
        selected_month1 = st.selectbox("Month 1", months, index=latest_month_index)

    with col2:
        selected_manager2 = st.selectbox("Manager 2", managers)
        selected_month2 = st.selectbox("Month 2", months, index=latest_month_index)

# -----------------------------
# All Managers Dashboard
# -----------------------------
if dashboard_type == "All Managers":
    st.header("📊 Enterprise Overview")

    filtered_df = df.copy()

    if selected_vertical != "All":
        filtered_df = filtered_df[filtered_df["Vertical"] == selected_vertical]

    if selected_month:
        filtered_df = filtered_df[filtered_df["Disb Month"] == selected_month]

    if selected_campaigns:
        filtered_df = filtered_df[filtered_df["Campaign"].isin(selected_campaigns)]

    agg_df = filtered_df.groupby(["Vertical","Manager"]).agg(
        Total_Disbursed=("Disbursed AMT","sum"),
        Total_Revenue=("Total_Revenue","sum"),
        Transactions=("Manager","count")
    ).reset_index()

    agg_df["Avg_Payout"] = (agg_df["Total_Revenue"]/agg_df["Total_Disbursed"]*100).round(2)

    st.dataframe(agg_df, use_container_width=True)

# -----------------------------
# Single Manager Dashboard
# -----------------------------
if dashboard_type == "Single Manager":
    st.header(f"📈 Insights - {selected_manager}")

    f = df[(df["Manager"]==selected_manager)&(df["Disb Month"]==selected_month)]

    if selected_campaigns:
        f = f[f["Campaign"].isin(selected_campaigns)]

    if not f.empty:
        total_disb,total_rev,avg_payout,txn_count,avg_disb,top_bank,top_campaign,top_caller = calc_metrics(f)

        c1,c2,c3,c4 = st.columns(4)
        with c1: colored_metric("Disbursed", format_inr(total_disb), "#636EFA")
        with c2: colored_metric("Revenue", format_inr(total_rev), "#00CC96")
        with c3: colored_metric("Payout %", f"{avg_payout:.2f}%", "#EF553B")
        with c4: colored_metric("Txn", txn_count, "#FFA15A")

        st.plotly_chart(plot_bar(f,"Bank",top_bank,selected_manager), use_container_width=True)

        st.dataframe(f, use_container_width=True)

# -----------------------------
# Comparison Dashboard
# -----------------------------
if dashboard_type == "Comparison":
    st.header("⚖️ Manager Benchmark")

    f1 = df[(df["Manager"]==selected_manager1)&(df["Disb Month"]==selected_month1)]
    f2 = df[(df["Manager"]==selected_manager2)&(df["Disb Month"]==selected_month2)]

    d1 = f1["Disbursed AMT"].sum()
    d2 = f2["Disbursed AMT"].sum()

    c1,c2 = st.columns(2)
    with c1: colored_metric(selected_manager1, format_inr(d1), "#636EFA")
    with c2: colored_metric(selected_manager2, format_inr(d2), "#00CC96")
