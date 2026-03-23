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
# Sidebar Multi-Select Filters
# -----------------------------
st.sidebar.title("Filters")
dashboard_type = st.sidebar.radio("Select Dashboard", ["All Managers", "Single Manager", "Comparison"])

verticals = sorted(df["Vertical"].dropna().unique())
months = sorted(df["Disb Month"].dropna().unique())
managers = sorted(df["Manager"].dropna().unique())
campaigns = sorted(df["Campaign"].dropna().unique())

# Multi-select filters
selected_verticals = st.sidebar.multiselect("Choose Business Verticals", ["All"]+verticals, default=["All"])
selected_months = st.sidebar.multiselect("Choose Months", months, default=months)
selected_managers = st.sidebar.multiselect("Choose Managers", managers, default=managers)
selected_campaigns = st.sidebar.multiselect("Choose Campaigns", ["All"]+campaigns, default=["All"])

# -----------------------------
# Function to filter DataFrame based on selections
# -----------------------------
def filter_df(df):
    filtered = df.copy()
    if "All" not in selected_verticals:
        filtered = filtered[filtered["Vertical"].isin(selected_verticals)]
    if selected_months:
        filtered = filtered[filtered["Disb Month"].isin(selected_months)]
    if "All" not in selected_managers:
        filtered = filtered[filtered["Manager"].isin(selected_managers)]
    if "All" not in selected_campaigns:
        filtered = filtered[filtered["Campaign"].isin(selected_campaigns)]
    return filtered

# -----------------------------
# ALL MANAGERS DASHBOARD
# -----------------------------
if dashboard_type=="All Managers":
    st.header("📊 Enterprise Overview")
    filtered_df = filter_df(df)

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
    st.download_button("Download CSV", agg_df.to_csv(index=False), "all_managers.csv", "text/csv")

    # Bank-wise chart
    bank_summary = filtered_df.groupby("Bank")["Disbursed AMT"].sum()
    if not bank_summary.empty:
        top_bank = bank_summary.idxmax()
        fig_bank = go.Figure(go.Bar(
            x=bank_summary.index,
            y=bank_summary.values/100000,
            text=[f"{v/100000:.2f}L" for v in bank_summary.values],
            textposition="auto",
            marker_color=get_colors(bank_summary.index, top_bank),
            name="Banks"
        ))
        fig_bank.update_layout(yaxis_title="Amount (L)", template="plotly_white", height=400, title="Bank-wise Disbursed Amount")
        st.plotly_chart(fig_bank, use_container_width=True)

# -----------------------------
# SINGLE MANAGER DASHBOARD
# -----------------------------
if dashboard_type=="Single Manager":
    st.header("📈 Manager Insights")
    filtered_df = filter_df(df)
    if filtered_df.empty:
        st.warning("No data available")
    else:
        for manager in selected_managers:
            f = filtered_df[filtered_df["Manager"]==manager]
            if f.empty:
                st.warning(f"No data for {manager}")
                continue
            total_disb,total_rev,avg_payout,txn_count,avg_disb,top_bank,top_campaign,top_caller = calc_metrics(f)
            st.subheader(f"Manager: {manager}")

            col1,col2,col3,col4 = st.columns(4)
            with col1: colored_metric("Total Disbursed", format_inr(total_disb), "#636EFA")
            with col2: colored_metric("Total Revenue", format_inr(total_rev), "#00CC96")
            with col3: colored_metric("Avg Payout %", f"{avg_payout:.2f}%", "#EF553B")
            with col4: colored_metric("Transactions", txn_count, "#FFA15A")

            st.plotly_chart(plot_bar(f,"Bank",top_bank,manager,key_val=f"{manager}_bank"), use_container_width=True)
            st.plotly_chart(plot_bar(f,"Caller",top_caller,manager,key_val=f"{manager}_caller"), use_container_width=True)

# -----------------------------
# COMPARISON DASHBOARD
# -----------------------------
if dashboard_type=="Comparison":
    st.header("⚖️ Manager Benchmark")
    filtered_df = filter_df(df)
    if len(selected_managers)<2:
        st.warning("Select at least 2 managers to compare")
    else:
        f1 = filtered_df[filtered_df["Manager"]==selected_managers[0]]
        f2 = filtered_df[filtered_df["Manager"]==selected_managers[1]]

        d1,r1,p1,txn1,avg1,top_bank1,top_camp1,top_caller1 = calc_metrics(f1)
        d2,r2,p2,txn2,avg2,top_bank2,top_camp2,top_caller2 = calc_metrics(f2)

        col1,col2,col3,col4 = st.columns(4)
        with col1: colored_metric(selected_managers[0], format_inr(d1), "#636EFA")
        with col2: colored_metric(selected_managers[1], format_inr(d2), "#00CC96")
        with col3: colored_metric("Total Revenue", f"{format_inr(r1)} vs {format_inr(r2)}", "#EF553B")
        with col4: colored_metric("Avg Payout %", f"{p1:.2f}% vs {p2:.2f}%", "#FFA15A")

        st.plotly_chart(plot_bar(f1,"Bank",top_bank1,selected_managers[0],key_val="cmp_bank1"), use_container_width=True)
        st.plotly_chart(plot_bar(f2,"Bank",top_bank2,selected_managers[1],key_val="cmp_bank2"), use_container_width=True)
