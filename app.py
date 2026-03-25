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
# Sidebar CSS & Global Styles
# -----------------------------
st.markdown("""
    <style>
    [data-testid="stSidebar"] {
        background-color: #2596be;
    }
    [data-testid="stSidebar"] .st-expander {
        background-color: #ffffff;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    /* Main Background Color */
    .main {
        background-color: #f8f9fa;
    }
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

# --- UPDATED MODERN CARD UI FUNCTION ---
def colored_metric(label, value, color="#2596be"):
    st.markdown(f"""
        <div style="
            background: white;
            padding: 20px;
            border-radius: 12px;
            border-left: 6px solid {color};
            box-shadow: 2px 4px 8px rgba(0,0,0,0.05);
            text-align: left;
            margin-bottom: 15px;
        ">
            <p style="color: #6c757d; font-size: 13px; margin: 0; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">{label}</p>
            <h2 style="color: #212529; margin: 5px 0 0 0; font-size: 26px; font-weight: 800;">{value}</h2>
        </div>
        """, unsafe_allow_html=True)

# -----------------------------
# Sidebar Filters
# -----------------------------
st.sidebar.title("📊 Filters")
with st.sidebar.expander("Select Dashboard Type", expanded=True):
    dashboard_type = st.radio("Dashboard", ["All Managers", "Single Manager", "Comparison", "Campaign Performance"])

verticals = ["All"] + sorted(df["Vertical"].dropna().unique())
months = sorted(df["Disb Month"].dropna().unique())
managers = sorted(df["Manager"].dropna().unique())
latest_month_index = len(months)-1

# -----------------------------
# All Managers Dashboard
# -----------------------------
if dashboard_type == "All Managers":
    with st.sidebar.expander("Month & Vertical Filters", expanded=True):
        selected_month = st.selectbox("Select Month", months, index=latest_month_index)
        selected_vertical = st.selectbox("Business Vertical", verticals)

    filtered_df = df.copy()
    if selected_vertical != "All":
        filtered_df = filtered_df[filtered_df["Vertical"]==selected_vertical]
    if selected_month:
        filtered_df = filtered_df[filtered_df["Disb Month"]==selected_month]

    campaigns_available = sorted(filtered_df["Campaign"].dropna().unique())
    with st.sidebar.expander("Campaign Filter", expanded=True):
        selected_campaigns = st.multiselect("Select Campaigns", campaigns_available, default=campaigns_available)
    if selected_campaigns:
        filtered_df = filtered_df[filtered_df["Campaign"].isin(selected_campaigns)]

    st.header("🏢 Portfolio Summary")
    if filtered_df.empty:
        st.warning("No data available for selected filters")
    else:
        agg_df = filtered_df.groupby(['Vertical',"Manager"]).agg(
            Total_Disbursed=("Disbursed AMT","sum"),
            Transactions=("Manager","count"),
        ).reset_index()
        
        total_disbursed = agg_df["Total_Disbursed"].sum()
        total_txn = agg_df["Transactions"].sum()
        top_manager_row = agg_df.loc[agg_df["Total_Disbursed"].idxmax()]

        # New Card UI Row
        col1, col2, col3 = st.columns(3)
        with col1:
            colored_metric("Total Disbursed", format_inr(total_disbursed), "#636EFA")
        with col2:
            colored_metric("Total Transactions", f"{total_txn:,}", "#EF553B")
        with col3:
            colored_metric(f"Top Manager: {top_manager_row['Manager']}", format_inr(top_manager_row['Total_Disbursed']), "#00CC96")
     
        st.subheader("📄 Detailed Table")
        st.dataframe(agg_df, use_container_width=True, height=400)

        bank_summary = filtered_df.groupby("Bank")["Disbursed AMT"].sum()
        if not bank_summary.empty:
            fig_bank = plot_bar(filtered_df, "Bank", bank_summary.idxmax(), "Overall", "bank_all")
            st.plotly_chart(fig_bank, use_container_width=True)

# -----------------------------
# Single Manager Dashboard
# -----------------------------
elif dashboard_type == "Single Manager":
    with st.sidebar.expander("Manager & Month Filters", expanded=True):
        selected_manager = st.selectbox("Select Manager", managers)
        selected_month = st.selectbox("Select Month", months, index=latest_month_index)

    filtered_df = df[df["Manager"]==selected_manager]
    if selected_month:
        filtered_df = filtered_df[filtered_df["Disb Month"]==selected_month]

    st.header(f"📈 Insights - {selected_manager}")
    if filtered_df.empty:
        st.warning("No data available")
    else:
        total_disb,total_rev,avg_payout,txn_count,avg_disb,top_bank,top_camp,top_caller = calc_metrics(filtered_df)
        
        # New Card UI Grid
        c1, c2, c3, c4 = st.columns(4)
        with c1: colored_metric("Total Disbursed", format_inr(total_disb), "#636EFA")
        with c2: colored_metric("Total Revenue", format_inr(total_rev), "#00CC96")
        with c3: colored_metric("Avg Payout %", f"{avg_payout:.2f}%", "#EF553B")
        with c4: colored_metric("Transactions", txn_count, "#FFA15A")

        st.plotly_chart(plot_bar(filtered_df,"Bank",top_bank,selected_manager,"b1"), use_container_width=True)
        st.plotly_chart(plot_bar(filtered_df,"Caller",top_caller,selected_manager,"c1"), use_container_width=True)

# -----------------------------
# Comparison Dashboard
# -----------------------------
elif dashboard_type == "Comparison":
    with st.sidebar.expander("Manager Selection", expanded=True):
        m1 = st.selectbox("First Manager", managers, index=0)
        m2 = st.selectbox("Second Manager", managers, index=1 if len(managers)>1 else 0)
        sel_month = st.selectbox("Select Month", months, index=latest_month_index)

    f1 = df[(df["Manager"]==m1) & (df["Disb Month"]==sel_month)]
    f2 = df[(df["Manager"]==m2) & (df["Disb Month"]==sel_month)]

    st.header("⚖️ Benchmark Comparison")
    if f1.empty or f2.empty:
        st.warning("Data missing for comparison")
    else:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader(m1)
            d1, r1, p1, t1, _, _, _, _ = calc_metrics(f1)
            colored_metric("Disbursed", format_inr(d1), "#636EFA")
            colored_metric("Revenue", format_inr(r1), "#00CC96")
        with col2:
            st.subheader(m2)
            d2, r2, p2, t2, _, _, _, _ = calc_metrics(f2)
            colored_metric("Disbursed", format_inr(d2), "#636EFA")
            colored_metric("Revenue", format_inr(r2), "#00CC96")

# -----------------------------
# Campaign Performance Dashboard
# -----------------------------
elif dashboard_type == "Campaign Performance":
    sel_camp_month = st.sidebar.selectbox("Select Month", months, index=latest_month_index)
    camp_df = df[df["Disb Month"] == sel_camp_month]

    st.header(f"🚀 Campaign Analysis - {sel_camp_month}")
    if not camp_df.empty:
        total_d = camp_df["Disbursed AMT"].sum()
        total_r = camp_df["Total_Revenue"].sum()
        
        col1, col2, col3 = st.columns(3)
        with col1: colored_metric("Total Disbursed", format_inr(total_d), "#636EFA")
        with col2: colored_metric("Total Revenue", format_inr(total_r), "#00CC96")
        with col3:
            top_c = camp_df.groupby("Campaign")["Disbursed AMT"].sum().idxmax()
            colored_metric("Top Campaign", top_c, "#FFA15A")

        camp_perf = camp_df.groupby("Campaign")["Disbursed AMT"].sum().sort_values(ascending=False)
        fig = go.Figure(go.Bar(x=camp_perf.index, y=camp_perf.values/100000, marker_color="#636EFA"))
        fig.update_layout(title="Campaign-wise Performance (Lakhs)", template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Sidebar Footer
# -----------------------------
st.sidebar.markdown("---")
if st.sidebar.button("🚪 Logout"):
    st.session_state.login = False
    st.rerun()
