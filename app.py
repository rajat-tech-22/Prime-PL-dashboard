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
def load_data(url):
    df = pd.read_csv(url)
    df.replace("null", None, inplace=True)
    return df

# Primary dashboard sheet
df1_url = "https://docs.google.com/spreadsheets/d/1I1ql5NwFafbWXYkVOvv0yvMM9GKnJ5954R4zif2owGI/export?format=csv"
df = load_data(df1_url)

# Campaign Performance sheet
df2_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRfDuP8FJ8yxoZxPPiKYrxWyP1Brlq7hmyxrkp81_oURiPrCJHqup7Ru8wFoE-pWMEZjZIuH_VBM5_i/pub?gid=2057712936&single=true&output=csv"
df_campaign = load_data(df2_url)

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

verticals = ["All"] + sorted(df["Vertical"].dropna().unique())
months = sorted(df["Disb Month"].dropna().unique())
managers = sorted(df["Manager"].dropna().unique())

# Latest month default
latest_month_index = len(months)-1

# -----------------------------
# Dashboard Filters
# -----------------------------
if dashboard_type == "All Managers":
    selected_month = st.sidebar.selectbox("Select Month", months, index=latest_month_index)
    selected_vertical = st.sidebar.selectbox("Business Vertical", verticals)
    filtered_for_campaigns = df.copy()
    if selected_vertical != "All":
        filtered_for_campaigns = filtered_for_campaigns[filtered_for_campaigns["Vertical"]==selected_vertical]
    filtered_for_campaigns = filtered_for_campaigns[filtered_for_campaigns["Disb Month"]==selected_month]
    campaigns_available = sorted(filtered_for_campaigns["Campaign"].dropna().unique())
    selected_campaigns = st.sidebar.multiselect("Campaigns", campaigns_available, default=campaigns_available)

elif dashboard_type == "Single Manager":
    selected_manager = st.sidebar.selectbox("Select Manager", managers)
    selected_month = st.sidebar.selectbox("Select Month", months, index=latest_month_index)
    filtered_for_campaigns = df[(df["Manager"]==selected_manager)]
    filtered_for_campaigns = filtered_for_campaigns[filtered_for_campaigns["Disb Month"]==selected_month]
    campaigns_available = sorted(filtered_for_campaigns["Campaign"].dropna().unique())
    selected_campaigns = st.sidebar.multiselect("Campaigns", campaigns_available, default=campaigns_available)

elif dashboard_type == "Comparison":
    selected_manager1 = st.sidebar.selectbox("Select First Manager", managers)
    selected_month1 = st.sidebar.selectbox("Month for First Manager", months, index=latest_month_index)
    selected_manager2 = st.sidebar.selectbox("Select Second Manager", managers)
    selected_month2 = st.sidebar.selectbox("Month for Second Manager", months, index=latest_month_index)

elif dashboard_type == "Campaign Performance":
    campaigns = sorted(df_campaign["Campaign"].dropna().unique())
    months_campaign = sorted(df_campaign["Disb Month"].dropna().unique())
    selected_campaigns = st.sidebar.multiselect("Campaigns", campaigns, default=campaigns)
    selected_campaign_months = st.sidebar.multiselect("Months", months_campaign, default=months_campaign)

# -----------------------------
# All Managers Dashboard
# -----------------------------
if dashboard_type == "All Managers":
    st.header("📊 Enterprise Overview")
    filtered_df = df.copy()
    if selected_vertical != "All":
        filtered_df = filtered_df[filtered_df["Vertical"]==selected_vertical]
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
    st.download_button("Download CSV", agg_df.to_csv(index=False), "all_managers.csv", "text/csv")

    bank_summary = filtered_df.groupby("Bank")["Disbursed AMT"].sum()
    if not bank_summary.empty:
        top_bank = bank_summary.idxmax()
        bank_colors = get_colors(bank_summary.index, top_bank)
        fig_bank = go.Figure(go.Bar(
            x=bank_summary.index,
            y=bank_summary.values/100000,
            text=[f"{v/100000:.2f}L" for v in bank_summary.values],
            textposition="auto",
            marker_color=bank_colors
        ))
        fig_bank.update_layout(
            yaxis_title="Amount (L)",
            template="plotly_white",
            height=400,
            title="Bank-wise Disbursed Amount"
        )
        st.plotly_chart(fig_bank, use_container_width=True)

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
        col1,col2,col3,col4 = st.columns(4)
        with col1: colored_metric("Total Disbursed", format_inr(total_disb), "#636EFA")
        with col2: colored_metric("Total Revenue", format_inr(total_rev), "#00CC96")
        with col3: colored_metric("Avg Payout %", f"{avg_payout:.2f}%", "#EF553B")
        with col4: colored_metric("Transactions", txn_count, "#FFA15A")
        st.plotly_chart(plot_bar(f,"Bank",top_bank,selected_manager,key_val="bank1"), use_container_width=True)
        st.plotly_chart(plot_bar(f,"Caller",top_caller,selected_manager,key_val="caller1"), use_container_width=True)
        summary = f.groupby("Campaign")["Disbursed AMT"].sum()
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
        st.dataframe(f, use_container_width=True, height=400)
        st.download_button("Download CSV", f.to_csv(index=False), "single_manager.csv", "text/csv")

# -----------------------------
# Comparison Dashboard
# -----------------------------
if dashboard_type == "Comparison":
    st.header("⚖️ Manager Benchmark")
    if selected_manager1 == selected_manager2:
        st.warning("Select different managers")
        st.stop()
    f1 = df[(df["Manager"]==selected_manager1)&(df["Disb Month"]==selected_month1)]
    f2 = df[(df["Manager"]==selected_manager2)&(df["Disb Month"]==selected_month2)]

    d1,r1,p1,txn1,avg1,top_bank1,top_camp1,top_caller1 = calc_metrics(f1)
    d2,r2,p2,txn2,avg2,top_bank2,top_camp2,top_caller2 = calc_metrics(f2)

    # Cards
    col1,col2 = st.columns(2)
    with col1:
        colored_metric(selected_manager1, f"Disb: {format_inr(d1)}\nRev: {format_inr(r1)}\nAvg Payout: {p1:.2f}%\nCount: {txn1}", "#636EFA")
    with col2:
        colored_metric(selected_manager2, f"Disb: {format_inr(d2)}\nRev: {format_inr(r2)}\nAvg Payout: {p2:.2f}%\nCount: {txn2}", "#00CC96")

    st.plotly_chart(plot_bar(f1,"Bank",top_bank1,selected_manager1,key_val="bank_cmp1"), use_container_width=True)
    st.plotly_chart(plot_bar(f2,"Bank",top_bank2,selected_manager2,key_val="bank_cmp2"), use_container_width=True)
    st.plotly_chart(plot_bar(f1,"Caller",top_caller1,selected_manager1,key_val="caller_cmp1"), use_container_width=True)
    st.plotly_chart(plot_bar(f2,"Caller",top_caller2,selected_manager2,key_val="caller_cmp2"), use_container_width=True)

    st.markdown("### 📄 Data - Manager 1")
    st.dataframe(f1, use_container_width=True, height=300)
    st.download_button("Download CSV", f1.to_csv(index=False), "manager1.csv", "text/csv")

    st.markdown("### 📄 Data - Manager 2")
    st.dataframe(f2, use_container_width=True, height=300)
    st.download_button("Download CSV", f2.to_csv(index=False), "manager2.csv", "text/csv")

# -----------------------------
# Campaign Performance Dashboard
# -----------------------------
if dashboard_type == "Campaign Performance":
    st.header("📊 Campaign Performance Dashboard")
    filtered_campaign = df_campaign.copy()
    if selected_campaigns:
        filtered_campaign = filtered_campaign[filtered_campaign["Campaign"].isin(selected_campaigns)]
    if selected_campaign_months:
        filtered_campaign = filtered_campaign[filtered_campaign["Disb Month"].isin(selected_campaign_months)]

    if not filtered_campaign.empty:
        campaign_summary = filtered_campaign.groupby(["Disb Month","Manager"]).agg(
            Total_Disbursed=("Disbursed AMT","sum"),
            Disb_Count=("Disbursed AMT","count")
        ).reset_index()
        campaign_summary["Total_Disbursed_INR"] = campaign_summary["Total_Disbursed"].apply(format_inr)

        st.markdown("### 📄 Data Table")
        st.dataframe(campaign_summary, use_container_width=True, height=400)
        st.download_button("Download CSV", campaign_summary.to_csv(index=False), "campaign_performance.csv", "text/csv")

        # Stacked Bar Chart
        fig_campaign = go.Figure()
        months_sorted = sorted(filtered_campaign["Disb Month"].unique())
        managers_sorted = sorted(filtered_campaign["Manager"].unique())
        colors_map = {man: base_colors[i%len(base_colors)] for i, man in enumerate(managers_sorted)}

        for manager in managers_sorted:
            y_values = []
            for month in months_sorted:
                val = campaign_summary[(campaign_summary["Manager"]==manager)&(campaign_summary["Disb Month"]==month)]
                y_values.append(val["Total_Disbursed"].values[0]/100000 if not val.empty else 0)
            fig_campaign.add_trace(go.Bar(
                x=months_sorted,
                y=y_values,
                name=manager,
                marker_color=colors_map[manager],
                text=[f"{v:.2f}L" for v in y_values],
                textposition="auto"
            ))

        fig_campaign.update_layout(
            barmode='stack',
            yaxis_title="Disbursed Amount (L)",
            xaxis_title="Month",
            template="plotly_white",
            height=500,
            title=f"Campaign Performance: Manager-wise Trend"
        )
        st.plotly_chart(fig_campaign, use_container_width=True)
