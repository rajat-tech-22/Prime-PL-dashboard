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
    return df

main_sheet_url = "https://docs.google.com/spreadsheets/d/1I1ql5NwFafbWXYkVOvv0yvMM9GKnJ5954R4zif2owGI/export?format=csv"
df = load_data(main_sheet_url)

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
    total_disb = f["Disbursed AMT"].sum() if "Disbursed AMT" in f.columns else 0
    total_rev = f["Total_Revenue"].sum() if "Total_Revenue" in f.columns else 0
    avg_payout = (total_rev/total_disb)*100 if total_disb else 0
    txn_count = len(f)
    avg_disb = total_disb/txn_count if txn_count else 0
    top_bank = f.groupby("Bank")["Disbursed AMT"].sum().idxmax() if "Bank" in f.columns and not f.empty else "N/A"
    top_campaign = f.groupby("Campaign")["Disbursed AMT"].sum().idxmax() if "Campaign" in f.columns and not f.empty else "N/A"
    top_caller = f.groupby("Caller")["Disbursed AMT"].sum().idxmax() if "Caller" in f.columns and not f.empty else "N/A"
    return total_disb,total_rev,avg_payout,txn_count,avg_disb,top_bank,top_campaign,top_caller

def plot_bar(f, col, top_value, manager_name, key_val):
    if col not in f.columns or f.empty:
        return None
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
# Dashboard Selection
# -----------------------------
dashboard_type = st.sidebar.radio(
    "Select Dashboard",
    ["All Managers", "Single Manager", "Comparison", "New Dashboard"]
)

# -----------------------------
# Filters for All Managers
# -----------------------------
if dashboard_type == "All Managers":
    st.header("📊 Enterprise Overview")
    verticals = ["All"] + sorted(df["Vertical"].dropna().unique())
    months = sorted(df["Disb Month"].dropna().unique())
    selected_vertical = st.sidebar.selectbox("Business Vertical", verticals)
    selected_month = st.sidebar.selectbox("Month", months, index=len(months)-1)
    filtered_for_campaigns = df.copy()
    if selected_vertical != "All":
        filtered_for_campaigns = filtered_for_campaigns[filtered_for_campaigns["Vertical"]==selected_vertical]
    if selected_month:
        filtered_for_campaigns = filtered_for_campaigns[filtered_for_campaigns["Disb Month"]==selected_month]
    campaigns_available = sorted(filtered_for_campaigns["Campaign"].dropna().unique())
    selected_campaigns = st.sidebar.multiselect("Campaigns", campaigns_available, default=campaigns_available)
    filtered_df = filtered_for_campaigns[filtered_for_campaigns["Campaign"].isin(selected_campaigns)]

    # Table
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

    # Bank chart
    bank_summary = filtered_df.groupby("Bank")["Disbursed AMT"].sum()
    if not bank_summary.empty:
        top_bank = bank_summary.idxmax()
        bank_colors = get_colors(bank_summary.index, top_bank)
        fig_bank = go.Figure(go.Bar(
            x=bank_summary.index,
            y=bank_summary.values/100000,
            text=[f"{v/100000:.2f}L" for v in bank_summary.values],
            textposition="auto",
            marker_color=bank_colors,
            name="Banks"
        ))
        fig_bank.update_layout(yaxis_title="Amount (L)", template="plotly_white", height=400, title="Bank-wise Disbursed Amount")
        st.plotly_chart(fig_bank, use_container_width=True)

# -----------------------------
# Single Manager Dashboard
# -----------------------------
elif dashboard_type == "Single Manager":
    st.header("📈 Single Manager Insights")
    managers = sorted(df["Manager"].dropna().unique())
    selected_manager = st.sidebar.selectbox("Select Manager", managers)
    months = sorted(df["Disb Month"].dropna().unique())
    selected_month = st.sidebar.selectbox("Month", months, index=len(months)-1)
    filtered_for_campaigns = df[(df["Manager"]==selected_manager) & (df["Disb Month"]==selected_month)]
    campaigns_available = sorted(filtered_for_campaigns["Campaign"].dropna().unique())
    selected_campaigns = st.sidebar.multiselect("Campaigns", campaigns_available, default=campaigns_available)
    f = filtered_for_campaigns[filtered_for_campaigns["Campaign"].isin(selected_campaigns)]

    if f.empty:
        st.warning("No data available")
    else:
        total_disb,total_rev,avg_payout,txn_count,avg_disb,top_bank,top_campaign,top_caller = calc_metrics(f)
        col1,col2,col3,col4 = st.columns(4)
        with col1: colored_metric("Total Disbursed", format_inr(total_disb), "#636EFA")
        with col2: colored_metric("Total Revenue", format_inr(total_rev), "#00CC96")
        with col3: colored_metric("Avg Payout %", f"{avg_payout:.2f}%", "#EF553B")
        with col4: colored_metric("Transactions", txn_count, "#FFA15A")
        if "Bank" in f.columns:
            st.plotly_chart(plot_bar(f,"Bank",top_bank,selected_manager,"bank1"), use_container_width=True)
        if "Caller" in f.columns:
            st.plotly_chart(plot_bar(f,"Caller",top_caller,selected_manager,"caller1"), use_container_width=True)
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
elif dashboard_type == "Comparison":
    st.header("⚖️ Manager Benchmark")
    managers = sorted(df["Manager"].dropna().unique())
    selected_manager1 = st.sidebar.selectbox("First Manager", managers)
    selected_manager2 = st.sidebar.selectbox("Second Manager", managers)
    months = sorted(df["Disb Month"].dropna().unique())
    selected_month1 = st.sidebar.selectbox("Month for First Manager", months, index=len(months)-1)
    selected_month2 = st.sidebar.selectbox("Month for Second Manager", months, index=len(months)-1)

    f1 = df[(df["Manager"]==selected_manager1) & (df["Disb Month"]==selected_month1)]
    f2 = df[(df["Manager"]==selected_manager2) & (df["Disb Month"]==selected_month2)]

    d1,r1,p1,txn1,avg1,top_bank1,top_camp1,top_caller1 = calc_metrics(f1)
    d2,r2,p2,txn2,avg2,top_bank2,top_camp2,top_caller2 = calc_metrics(f2)

    # Cards
    col1, col2 = st.columns(2)
    with col1: colored_metric(selected_manager1, f"Disb: {format_inr(d1)}\nRev: {format_inr(r1)}\nAvg Payout: {p1:.2f}%\nTxns: {txn1}", "#636EFA")
    with col2: colored_metric(selected_manager2, f"Disb: {format_inr(d2)}\nRev: {format_inr(r2)}\nAvg Payout: {p2:.2f}%\nTxns: {txn2}", "#00CC96")

    # Charts
    if "Bank" in f1.columns:
        st.plotly_chart(plot_bar(f1,"Bank",top_bank1,selected_manager1,"bank_cmp1"), use_container_width=True)
    if "Bank" in f2.columns:
        st.plotly_chart(plot_bar(f2,"Bank",top_bank2,selected_manager2,"bank_cmp2"), use_container_width=True)
    if "Caller" in f1.columns:
        st.plotly_chart(plot_bar(f1,"Caller",top_caller1,selected_manager1,"caller_cmp1"), use_container_width=True)
    if "Caller" in f2.columns:
        st.plotly_chart(plot_bar(f2,"Caller",top_caller2,selected_manager2,"caller_cmp2"), use_container_width=True)

    st.markdown("### 📄 Data - Manager 1")
    st.dataframe(f1, use_container_width=True, height=300)
    st.download_button("Download CSV", f1.to_csv(index=False), "manager1.csv", "text/csv")
    st.markdown("### 📄 Data - Manager 2")
    st.dataframe(f2, use_container_width=True, height=300)
    st.download_button("Download CSV", f2.to_csv(index=False), "manager2.csv", "text/csv")

# -----------------------------
# New Dashboard
# -----------------------------
elif dashboard_type == "New Dashboard":
    st.header("🆕 New Dashboard")
    new_sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS75v4-MSF1c-OHa_i2vROq5s11dPo_t470t9cux3LetgsnZdtbMUqgVvg/pub?gid=1311906253&single=true&output=csv"
    df_new = load_data(new_sheet_url)

    if df_new.empty:
        st.warning("No data available in New Dashboard sheet")
        st.stop()

    # Filters
    new_verticals = ["All"] + sorted(df_new["Vertical"].dropna().unique()) if "Vertical" in df_new.columns else ["All"]
    new_months = sorted(df_new["Disb Month"].dropna().unique()) if "Disb Month" in df_new.columns else []
    selected_vertical = st.sidebar.selectbox("Business Vertical (New)", new_verticals)
    selected_month = st.sidebar.selectbox("Month (New)", new_months) if new_months else None

    # Filter data
    filtered_df = df_new.copy()
    if "Vertical" in df_new.columns and selected_vertical != "All":
        filtered_df = filtered_df[filtered_df["Vertical"]==selected_vertical]
    if "Disb Month" in df_new.columns and selected_month:
        filtered_df = filtered_df[filtered_df["Disb Month"]==selected_month]

    if filtered_df.empty:
        st.warning("No data available for selected filters")
    else:
        # Metrics cards
        total_disb,total_rev,avg_payout,txn_count,avg_disb,top_bank,top_campaign,top_caller = calc_metrics(filtered_df)
        col1,col2,col3,col4 = st.columns(4)
        with col1: colored_metric("Total Disbursed", format_inr(total_disb), "#636EFA")
        with col2: colored_metric("Total Revenue", format_inr(total_rev), "#00CC96")
        with col3: colored_metric("Avg Payout %", f"{avg_payout:.2f}%", "#EF553B")
        with col4: colored_metric("Transactions", txn_count, "#FFA15A")

        # Charts
        if "Bank" in df_new.columns:
            st.plotly_chart(plot_bar(filtered_df,"Bank",top_bank,"New Dashboard","bank_new"), use_container_width=True)
        if "Caller" in df_new.columns:
            st.plotly_chart(plot_bar(filtered_df,"Caller",top_caller,"New Dashboard","caller_new"), use_container_width=True)

        # Data Table
        st.markdown("### 📄 Data")
        st.dataframe(filtered_df, use_container_width=True, height=400)
        st.download_button("Download CSV", filtered_df.to_csv(index=False), "new_dashboard.csv", "text/csv")
