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
    # Strip spaces aur lower case column names
    df.columns = df.columns.str.strip()
    # Rename sheet columns to match code
    if 'Campaign Name' in df.columns:
        df.rename(columns={"Campaign Name":"Campaign"}, inplace=True)
    if 'Disbursed Amount' in df.columns:
        df.rename(columns={"Disbursed Amount":"Disbursed AMT"}, inplace=True)
    if 'Total Revenue' not in df.columns:
        df["Total_Revenue"] = df["Disbursed AMT"]  # agar revenue na ho
    df.replace("null", None, inplace=True)
    return df

# First main dashboard sheet
df = load_data("https://docs.google.com/spreadsheets/d/1I1ql5NwFafbWXYkVOvv0yvMM9GKnJ5954R4zif2owGI/export?format=csv")
# Campaign Performance sheet
df_campaign = load_data("https://docs.google.com/spreadsheets/d/e/2PACX-1vRfDuP8FJ8yxoZxPPiKYrxWyP1Brlq7hmyxrkp81_oURiPrCJHqup7Ru8wFoE-pWMEZjZIuH_VBM5_i/pub?gid=2057712936&single=true&output=csv")

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
    top_bank = f.groupby("Bank")["Disbursed AMT"].sum().idxmax() if not f.empty and "Bank" in f.columns else "N/A"
    top_campaign = f.groupby("Campaign")["Disbursed AMT"].sum().idxmax() if not f.empty else "N/A"
    top_caller = f.groupby("Caller")["Disbursed AMT"].sum().idxmax() if not f.empty and "Caller" in f.columns else "N/A"
    return total_disb,total_rev,avg_payout,txn_count,avg_disb,top_bank,top_campaign,top_caller

def plot_bar(f, col, top_value, manager_name, key_val):
    if col not in f.columns:
        return go.Figure()
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
# Dashboard Tabs
# -----------------------------
tab1, tab2, tab3, tab4 = st.tabs(["All Managers","Single Manager","Comparison","Campaign Performance"])

# -----------------------------
# Tab 1: All Managers
# -----------------------------
with tab1:
    st.header("📊 Enterprise Overview")
    verticals = ["All"] + sorted(df["Vertical"].dropna().unique())
    months = sorted(df["Disb Month"].dropna().unique())
    selected_vertical = st.selectbox("Business Vertical", verticals)
    selected_month = st.selectbox("Select Month", months)
    filtered = df.copy()
    if selected_vertical != "All":
        filtered = filtered[filtered["Vertical"]==selected_vertical]
    if selected_month:
        filtered = filtered[filtered["Disb Month"]==selected_month]
    campaigns_available = sorted(filtered["Campaign"].dropna().unique())
    selected_campaigns = st.multiselect("Campaigns", campaigns_available, default=campaigns_available)
    filtered = filtered[filtered["Campaign"].isin(selected_campaigns)]
    # Aggregated table
    agg_df = filtered.groupby(["Vertical","Manager"]).agg(
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

# -----------------------------
# Tab 2: Single Manager
# -----------------------------
with tab2:
    st.header("📈 Single Manager Insights")
    managers = sorted(df["Manager"].dropna().unique())
    months = sorted(df["Disb Month"].dropna().unique())
    selected_manager = st.selectbox("Select Manager", managers)
    selected_month = st.selectbox("Select Month", months)
    filtered = df[(df["Manager"]==selected_manager)&(df["Disb Month"]==selected_month)]
    campaigns_available = sorted(filtered["Campaign"].dropna().unique())
    selected_campaigns = st.multiselect("Campaigns", campaigns_available, default=campaigns_available)
    filtered = filtered[filtered["Campaign"].isin(selected_campaigns)]
    if filtered.empty:
        st.warning("No data available")
    else:
        total_disb,total_rev,avg_payout,txn_count,avg_disb,top_bank,top_campaign,top_caller = calc_metrics(filtered)
        col1,col2,col3,col4 = st.columns(4)
        with col1: colored_metric("Total Disbursed", format_inr(total_disb), "#636EFA")
        with col2: colored_metric("Total Revenue", format_inr(total_rev), "#00CC96")
        with col3: colored_metric("Avg Payout %", f"{avg_payout:.2f}%", "#EF553B")
        with col4: colored_metric("Transactions", txn_count, "#FFA15A")
        st.plotly_chart(plot_bar(filtered,"Bank",top_bank,selected_manager,key_val="bank1"), use_container_width=True)
        st.plotly_chart(plot_bar(filtered,"Caller",top_caller,selected_manager,key_val="caller1"), use_container_width=True)
        summary = filtered.groupby("Campaign")["Disbursed AMT"].sum()
        fig = go.Figure(go.Pie(labels=summary.index, values=summary.values/100000, hole=0.4))
        fig.update_layout(title="Campaign Distribution")
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("### 📝 Insights")
        st.write(f"Top Bank: {top_bank}")
        st.write(f"Top Campaign: {top_campaign}")
        st.write(f"Top Caller: {top_caller}")
        st.write(f"Transactions: {txn_count}")
        st.write(f"Avg Disbursed: {format_inr(avg_disb)}")
        st.markdown("### 📄 Data")
        st.dataframe(filtered, use_container_width=True, height=400)

# -----------------------------
# Tab 3: Comparison
# -----------------------------
with tab3:
    st.header("⚖️ Manager Benchmark")
    managers = sorted(df["Manager"].dropna().unique())
    months = sorted(df["Disb Month"].dropna().unique())
    col1, col2 = st.columns(2)
    with col1:
        selected_manager1 = st.selectbox("Manager 1", managers, key="m1")
        selected_month1 = st.selectbox("Month 1", months, key="mm1")
    with col2:
        selected_manager2 = st.selectbox("Manager 2", managers, key="m2")
        selected_month2 = st.selectbox("Month 2", months, key="mm2")
    f1 = df[(df["Manager"]==selected_manager1)&(df["Disb Month"]==selected_month1)]
    f2 = df[(df["Manager"]==selected_manager2)&(df["Disb Month"]==selected_month2)]
    d1,r1,p1,txn1,avg1,top_bank1,top_camp1,top_caller1 = calc_metrics(f1)
    d2,r2,p2,txn2,avg2,top_bank2,top_camp2,top_caller2 = calc_metrics(f2)
    col1,col2 = st.columns(2)
    with col1:
        colored_metric(selected_manager1, f"Disb: {format_inr(d1)}\nRev: {format_inr(r1)}\nAvg Payout: {p1:.2f}%\nTxn: {txn1}", "#636EFA")
    with col2:
        colored_metric(selected_manager2, f"Disb: {format_inr(d2)}\nRev: {format_inr(r2)}\nAvg Payout: {p2:.2f}%\nTxn: {txn2}", "#00CC96")
    st.plotly_chart(plot_bar(f1,"Bank",top_bank1,selected_manager1,key_val="bank_cmp1"), use_container_width=True)
    st.plotly_chart(plot_bar(f2,"Bank",top_bank2,selected_manager2,key_val="bank_cmp2"), use_container_width=True)
    st.plotly_chart(plot_bar(f1,"Caller",top_caller1,selected_manager1,key_val="caller_cmp1"), use_container_width=True)
    st.plotly_chart(plot_bar(f2,"Caller",top_caller2,selected_manager2,key_val="caller_cmp2"), use_container_width=True)

# -----------------------------
# Tab 4: Campaign Performance
# -----------------------------
with tab4:
    st.header("📊 Campaign Performance")
    campaigns = sorted(df_campaign["Campaign"].dropna().unique())
    months = sorted(df_campaign["Disb Month"].dropna().unique())
    selected_campaigns = st.multiselect("Campaigns", campaigns, default=campaigns)
    selected_months = st.multiselect("Months", months, default=months)
    filtered = df_campaign[(df_campaign["Campaign"].isin(selected_campaigns)) & (df_campaign["Disb Month"].isin(selected_months))]
    if not filtered.empty:
        summary = filtered.groupby(["Manager","Campaign"]).agg(
            Total_Disbursed=("Disbursed AMT","sum"),
            Disb_Count=("Disbursed AMT","count")
        ).reset_index()
        st.dataframe(summary, use_container_width=True, height=400)
    else:
        st.warning("No data available for selected filters")
