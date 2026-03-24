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
# Tabs
# -----------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 All Managers",
    "📈 Single Manager",
    "⚖️ Comparison",
    "📅 Day to Day"
])

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
# Sidebar Filters
# -----------------------------
st.sidebar.title("Filters")

dashboard_type = st.sidebar.radio("Select Dashboard", ["All Managers", "Single Manager", "Comparison"])

months = sorted(df["Disb Month"].dropna().unique())
latest_month_index = len(months)-1 if months else 0

# -----------------------------
# TAB 1: All Managers
# -----------------------------
with tab1:
    if dashboard_type == "All Managers":
        st.header("📊 Enterprise Overview")

        selected_month = st.sidebar.selectbox("Select Month", months, index=latest_month_index)

        filtered_df = df[df["Disb Month"] == selected_month]

        agg_df = filtered_df.groupby(["Manager"]).agg(
            Total_Disbursed=("Disbursed AMT","sum"),
            Total_Revenue=("Total_Revenue","sum"),
            Transactions=("Manager","count")
        ).reset_index()

        agg_df["Avg_Payout"] = (agg_df["Total_Revenue"]/agg_df["Total_Disbursed"]*100).round(2)

        st.dataframe(agg_df, use_container_width=True)

# -----------------------------
# TAB 2: Single Manager
# -----------------------------
with tab2:
    if dashboard_type == "Single Manager":
        managers = sorted(df["Manager"].dropna().unique())
        selected_manager = st.sidebar.selectbox("Manager", managers)
        selected_month = st.sidebar.selectbox("Month", months, index=latest_month_index)

        f = df[(df["Manager"]==selected_manager)&(df["Disb Month"]==selected_month)]

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
# TAB 3: Comparison
# -----------------------------
with tab3:
    if dashboard_type == "Comparison":
        managers = sorted(df["Manager"].dropna().unique())

        m1 = st.sidebar.selectbox("Manager 1", managers)
        m2 = st.sidebar.selectbox("Manager 2", managers)

        f1 = df[df["Manager"]==m1]
        f2 = df[df["Manager"]==m2]

        d1 = f1["Disbursed AMT"].sum()
        d2 = f2["Disbursed AMT"].sum()

        c1,c2 = st.columns(2)
        with c1: colored_metric(m1, format_inr(d1), "#636EFA")
        with c2: colored_metric(m2, format_inr(d2), "#00CC96")

# -----------------------------
# TAB 4: Day to Day (NEW)
# -----------------------------
with tab4:
    st.header("📅 Day to Day Performance")

    df_day = df.copy()

    if "Disb Date" not in df_day.columns:
        st.warning("⚠️ 'Disb Date' column missing in sheet")
    else:
        df_day["Disb Date"] = pd.to_datetime(df_day["Disb Date"], errors="coerce")

        managers = ["All"] + sorted(df_day["Manager"].dropna().unique())
        selected_manager = st.selectbox("Manager", managers)

        if selected_manager != "All":
            df_day = df_day[df_day["Manager"] == selected_manager]

        daily = df_day.groupby("Disb Date").agg(
            Disbursed=("Disbursed AMT","sum"),
            Revenue=("Total_Revenue","sum"),
            Txn=("Manager","count")
        ).reset_index().sort_values("Disb Date")

        if not daily.empty:
            daily["Disbursed_L"] = daily["Disbursed"]/100000

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=daily["Disb Date"],
                y=daily["Disbursed_L"],
                mode='lines+markers',
                name="Disb"
            ))

            fig.update_layout(title="Daily Disbursal Trend", template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)

            st.dataframe(daily, use_container_width=True)
