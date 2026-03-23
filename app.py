import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from streamlit_autorefresh import st_autorefresh

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(page_title="Manager Dashboard", layout="wide")
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

def plot_bar(f, col, manager_name, key):
    summary = f.groupby(col)["Disbursed AMT"].sum()
    colors = ["#636EFA","#EF553B","#00CC96","#AB63FA","#FFA15A","#19D3F3","#FF6692","#B6E880"]
    fig = go.Figure(go.Bar(
        x=summary.index,
        y=summary.values/100000,
        text=[f"{v/100000:.2f}L" for v in summary.values],
        textposition="auto",
        marker_color=[colors[i%len(colors)] for i in range(len(summary))],
        name=manager_name,
        width=0.5
    ))
    fig.update_layout(title=f"{manager_name} - {col} Summary", yaxis_title="Amount (L)", template="plotly_white", height=400)
    st.plotly_chart(fig, use_container_width=True, key=key)

# -----------------------------
# KPI card function
# -----------------------------
def kpi_card(title, value, subtitle="", color="#636EFA"):
    st.markdown(
        f"""
        <div style="
            background-color:{color};
            padding:20px;
            border-radius:10px;
            text-align:center;
            color:white;
            font-family:sans-serif;
            margin-bottom:10px;
        ">
            <h4 style="margin:0">{title}</h4>
            <h2 style="margin:5px 0">{value}</h2>
            <small>{subtitle}</small>
        </div>
        """, unsafe_allow_html=True
    )

# -----------------------------
# Sidebar Filters
# -----------------------------
st.sidebar.title("Dashboard")
dashboard_type = st.sidebar.radio("Select Dashboard", ["All Managers", "Single Manager", "Comparison"])
months = sorted(df["Disb Month"].dropna().unique())
selected_month = st.sidebar.selectbox("Select Month", months)

managers = sorted(df["Manager"].dropna().unique())
selected_manager1 = st.sidebar.selectbox("Manager 1", managers)
if dashboard_type=="Comparison":
    selected_manager2 = st.sidebar.selectbox("Manager 2", managers, index=1)

# -----------------------------
# ALL MANAGERS DASHBOARD
# -----------------------------
if dashboard_type=="All Managers":
    st.header("📊 All Managers Dashboard")
    filtered_df = df[df["Disb Month"]==selected_month]

    # Aggregate by Vertical and Manager
    agg_df = filtered_df.groupby(["Vertical","Manager"]).agg(
        Total_Disbursed=("Disbursed AMT","sum"),
        Total_Revenue=("Total_Revenue","sum"),
        Transactions=("Manager","count")
    ).reset_index()

    # Colorful table
    st.dataframe(agg_df.style.background_gradient(cmap='Blues', subset=["Total_Disbursed","Total_Revenue","Transactions"]))

    # Download button
    st.download_button("Download Data", agg_df.to_csv(index=False), "all_managers.csv", "text/csv")

# -----------------------------
# SINGLE MANAGER DASHBOARD
# -----------------------------
if dashboard_type=="Single Manager":
    st.header(f"📊 {selected_manager1} Dashboard - {selected_month}")
    f = df[(df["Manager"]==selected_manager1) & (df["Disb Month"]==selected_month)]

    if f.empty:
        st.warning("No data available")
    else:
        total_disb,total_rev,avg_payout,txn_count,avg_disb,top_bank,top_campaign,top_caller = calc_metrics(f)

        # Colorful KPI cards
        col1,col2,col3,col4 = st.columns(4)
        with col1: kpi_card("Total Disbursed", format_inr(total_disb), f"{txn_count} Txn", "#1f77b4")
        with col2: kpi_card("Total Revenue", format_inr(total_rev), "", "#ff7f0e")
        with col3: kpi_card("Avg Payout %", f"{avg_payout:.2f}%", "", "#2ca02c")
        with col4: kpi_card("Avg Disbursed", format_inr(avg_disb), "", "#d62728")

        # Charts
        plot_bar(f,"Bank",selected_manager1,"bank_single")
        plot_bar(f,"Caller",selected_manager1,"caller_single")

        # Campaign Pie
        summary = f.groupby("Campaign")["Disbursed AMT"].sum()
        fig = go.Figure(go.Pie(labels=summary.index, values=summary.values/100000, hole=0.4))
        fig.update_layout(title=f"{selected_manager1} - Campaign Distribution")
        st.plotly_chart(fig, use_container_width=True, key="campaign_single")

        # Summary
        st.markdown("### 📝 Insights")
        st.write(f"Top Bank: {top_bank}")
        st.write(f"Top Campaign: {top_campaign}")
        st.write(f"Top Caller: {top_caller}")

# -----------------------------
# COMPARISON DASHBOARD
# -----------------------------
if dashboard_type=="Comparison":
    st.header(f"📊 Comparison Dashboard - {selected_month}")
    f1 = df[(df["Manager"]==selected_manager1) & (df["Disb Month"]==selected_month)]
    f2 = df[(df["Manager"]==selected_manager2) & (df["Disb Month"]==selected_month)]

    d1,r1,p1,txn1,avg1,top_bank1,top_camp1,top_caller1 = calc_metrics(f1)
    d2,r2,p2,txn2,avg2,top_bank2,top_camp2,top_caller2 = calc_metrics(f2)

    # Colorful KPI cards side-by-side
    col1,col2,col3,col4 = st.columns(4)
    with col1: kpi_card(f"{selected_manager1} Disbursed", format_inr(d1), f"{txn1} Txn", "#1f77b4")
    with col2: kpi_card(f"{selected_manager2} Disbursed", format_inr(d2), f"{txn2} Txn", "#ff7f0e")
    with col3: kpi_card(f"{selected_manager1} Revenue", format_inr(r1), "", "#2ca02c")
    with col4: kpi_card(f"{selected_manager2} Revenue", format_inr(r2), "", "#d62728")

    col5,col6,col7,col8 = st.columns(4)
    with col5: kpi_card(f"{selected_manager1} Avg Payout %", f"{p1:.2f}%", "", "#9467bd")
    with col6: kpi_card(f"{selected_manager2} Avg Payout %", f"{p2:.2f}%", "", "#8c564b")
    with col7: kpi_card(f"{selected_manager1} Avg Disbursed", format_inr(avg1), "", "#e377c2")
    with col8: kpi_card(f"{selected_manager2} Avg Disbursed", format_inr(avg2), "", "#7f7f7f")

    # Charts
    plot_bar(f1,"Bank",selected_manager1,"bank_comp1")
    plot_bar(f2,"Bank",selected_manager2,"bank_comp2")
    plot_bar(f1,"Caller",selected_manager1,"caller_comp1")
    plot_bar(f2,"Caller",selected_manager2,"caller_comp2")
