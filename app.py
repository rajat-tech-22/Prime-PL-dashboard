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
# 🔐 SIMPLE LOGIN SYSTEM
# -----------------------------
USERNAME = "PrimePL"
PASSWORD = "@1234"

if "login" not in st.session_state:
    st.session_state.login = False

if not st.session_state.login:
    st.title("🔐 Login")
    u = st.text_input("Username", value="PrimePL")
    p = st.text_input("Password", type="password")
    if st.button("Login"):
        if u == USERNAME and p == PASSWORD:
            st.session_state.login = True
            st.success("Login Successful ✅")
            st.rerun()
        else:
            st.error("Invalid Credentials ❌")
    st.stop()

# -----------------------------
# Sidebar & Global CSS
# -----------------------------
st.markdown("""
    <style>
    [data-testid="stSidebar"] {background-color: #0D918F; color: Black;}
    [data-testid="stSidebar"] .st-expander {background-color: #61FF5E; border-radius: 8px; margin-bottom: 10px;}
    .main {background-color: #f8f9fa;}
    </style>
""", unsafe_allow_html=True)

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

# -----------------------------
# Metrics Calculation
# -----------------------------
def calc_metrics(f):
    total_disb = f["Disbursed AMT"].sum()
    total_rev = f["Total_Revenue"].sum()
    avg_payout = (total_rev / total_disb) * 100 if total_disb else 0
    txn_count = len(f)
    avg_disb = total_disb / txn_count if txn_count else 0
    top_bank = f.groupby("Bank")["Disbursed AMT"].sum().idxmax() if not f.empty else "N/A"
    top_campaign = f.groupby("Campaign")["Disbursed AMT"].sum().idxmax() if not f.empty else "N/A"
    top_caller = f.groupby("Caller")["Disbursed AMT"].sum().idxmax() if not f.empty else "N/A"

    # Distinct Target sum by Month + Manager
    if "Target" in f.columns and "Disb Month" in f.columns and "Manager" in f.columns:
        grouped = f.groupby(["Disb Month","Manager"])["Target"].unique()
        unique_targets = set()
        for arr in grouped:
            unique_targets.update(arr)
        total_target = sum(unique_targets)
    else:
        total_target = 0

    return total_disb, total_rev, avg_payout, txn_count, avg_disb, top_bank, top_campaign, top_caller, total_target

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

# -----------------------------
# Card Functions
# -----------------------------
def colored_metric(label, value, color="#2596be"):
    st.markdown(f"""
        <div style="
            background-color: #EDC7E7;
            padding: 20px;
            border-radius: 12px;
            border-left: 6px solid {color};
            box-shadow: 2px 4px 10px rgba(0,0,0,0.08);
            text-align: left;
            margin-bottom: 15px;
        ">
            <p style="color: #6c757d; font-size: 13px; margin: 0; font-weight: 700; text-transform: uppercase; letter-spacing: 0.8px;">{label}</p>
            <h2 style="color: #212529; margin: 5px 0 0 0; font-size: 24px; font-weight: 800;">{value}</h2>
        </div>
        """, unsafe_allow_html=True)

def colored_metric_with_progress(label, value, target=None, color="#2596be"):
    progress_html = ""
    if target is not None and target > 0:
        percent = min(100, (value/target)*100)
        if percent >= 100:
            bar_color = "#28a745"  # Green
        elif percent >= 80:
            bar_color = "#ffc107"  # Yellow
        else:
            bar_color = "#dc3545"  # Red
        progress_html = f"""
            <div style="background-color: #e9ecef; border-radius: 8px; height: 12px; margin-top: 8px;">
                <div style="width: {percent}%; background-color: {bar_color}; height: 100%; border-radius: 8px;"></div>
            </div>
            <p style="font-size:12px; color:#495057; margin:0;">{percent:.1f}% of Target</p>
        """
    st.markdown(f"""
        <div style="
            background-color: #EDC7E7;
            padding: 20px;
            border-radius: 12px;
            border-left: 6px solid {color};
            box-shadow: 2px 4px 10px rgba(0,0,0,0.08);
            text-align: left;
            margin-bottom: 15px;
        ">
            <p style="color: #6c757d; font-size: 13px; margin: 0; font-weight: 700; text-transform: uppercase; letter-spacing: 0.8px;">{label}</p>
            <h2 style="color: #212529; margin: 5px 0 0 0; font-size: 24px; font-weight: 800;">{format_inr(value)}</h2>
            {progress_html}
        </div>
        """, unsafe_allow_html=True)

# -----------------------------
# Sidebar Filters
# -----------------------------
st.sidebar.title("📊 Filters")
dashboard_type = st.sidebar.radio("Dashboard", ["All Managers", "Single Manager", "Comparison", "Campaign Performance"])
verticals = ["All"] + sorted(df["Vertical"].dropna().unique())
months = sorted(df["Disb Month"].dropna().unique())
managers = sorted(df["Manager"].dropna().unique())
latest_month_index = len(months)-1

# -----------------------------
# All Managers Dashboard
# -----------------------------
if dashboard_type == "All Managers":
    selected_month = st.sidebar.selectbox("Select Month", months, index=latest_month_index)
    selected_vertical = st.sidebar.selectbox("Business Vertical", verticals)

    filtered_df = df.copy()
    if selected_vertical != "All":
        filtered_df = filtered_df[filtered_df["Vertical"]==selected_vertical]
    if selected_month:
        filtered_df = filtered_df[filtered_df["Disb Month"]==selected_month]

    campaigns_available = sorted(filtered_df["Campaign"].dropna().unique())
    selected_campaigns = st.sidebar.multiselect("Select Campaigns", campaigns_available, default=campaigns_available)
    if selected_campaigns:
        filtered_df = filtered_df[filtered_df["Campaign"].isin(selected_campaigns)]

    st.header("📊 Overview - Summary Cards")
    if filtered_df.empty:
        st.warning("No data available for selected filters")
    else:
        agg_df = filtered_df.groupby(['Vertical',"Manager"]).agg(
            Total_Disbursed=("Disbursed AMT","sum"),
            Transactions=("Manager","count"),
        ).reset_index()
        grouped_target = filtered_df.groupby(["Disb Month","Manager"])["Target"].unique()
        unique_targets = set()
        for arr in grouped_target:
            unique_targets.update(arr)
        total_target = sum(unique_targets)

        total_disbursed = agg_df["Total_Disbursed"].sum()
        total_txn = agg_df["Transactions"].sum()
        top_manager_row = agg_df.loc[agg_df["Total_Disbursed"].idxmax()]
        top_manager_name = top_manager_row["Manager"]
        top_manager_amt = top_manager_row["Total_Disbursed"]

        col1, col2, col3, col4 = st.columns(4)
        with col1: colored_metric("Total Disbursed Amount", format_inr(total_disbursed), "#636EFA")
        with col2: colored_metric("Total Transactions", total_txn, "#EF553B")
        with col3: colored_metric(f"Top Manager: {top_manager_name}", format_inr(top_manager_amt), "#00CC96")
        with col4: colored_metric_with_progress("Total Target vs Achievement", total_disbursed, total_target, "#8A2BE2")

        agg_df_display = agg_df.copy()
        agg_df_display["Total_Disbursed"] = agg_df_display["Total_Disbursed"].apply(format_inr)
        st.subheader("📄 Detailed Table")
        st.dataframe(agg_df_display, use_container_width=True, height=500)
        st.download_button("Download CSV", agg_df_display.to_csv(index=False), "all_managers.csv", "text/csv")

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
            fig_bank.update_layout(yaxis_title="Amount (L)", template="plotly_white", height=400, title="Bank-wise Disbursed Amount", xaxis_tickangle=-30)
            st.plotly_chart(fig_bank, use_container_width=True)

# -----------------------------
# Single Manager Dashboard
# -----------------------------
elif dashboard_type == "Single Manager":
    selected_manager = st.sidebar.selectbox("Select Manager", managers)
    selected_month = st.sidebar.selectbox("Select Month", months, index=latest_month_index)

    filtered_df = df[df["Manager"]==selected_manager]
    if selected_month:
        filtered_df = filtered_df[filtered_df["Disb Month"]==selected_month]

    campaigns_available = sorted(filtered_df["Campaign"].dropna().unique())
    selected_campaigns = st.sidebar.multiselect("Select Campaigns", campaigns_available, default=campaigns_available)
    if selected_campaigns:
        filtered_df = filtered_df[filtered_df["Campaign"].isin(selected_campaigns)]

    st.header(f"📈 Insights - {selected_manager}")
    f = filtered_df
    if f.empty:
        st.warning("No data available")
    else:
        total_disb, total_rev, avg_payout, txn_count, avg_disb, top_bank, top_campaign, top_caller, total_target = calc_metrics(f)

        col1,col2,col3,col4,col5 = st.columns(5)
        with col1: colored_metric("Total Disbursed (Achievement)", format_inr(total_disb), "#636EFA")
        with col2: colored_metric("Total Revenue", format_inr(total_rev), "#00CC96")
        with col3: colored_metric("Avg Payout %", f"{avg_payout:.2f}%", "#EF553B")
        with col4: colored_metric("Transactions", txn_count, "#FFA15A")
        with col5: colored_metric_with_progress("Target vs Achievement", total_disb, total_target, "#8A2BE2")

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
