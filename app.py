import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from streamlit_autorefresh import st_autorefresh

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(page_title="Manager Dashboard", layout="wide")
st_autorefresh(interval=60*1000, key="refresh")  # refresh every 1 min

# -----------------------------
# 🔐 LOGIN
# -----------------------------
USERNAME = "PrimePL"
PASSWORD = "@1234"

if "login" not in st.session_state:
    st.session_state.login = False

if not st.session_state.login:
    st.title("🔐 Login")
    u = st.text_input("Username", value="")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        if u == USERNAME and p == PASSWORD:
            st.session_state.login = True
            st.rerun()
        else:
            st.error("Invalid Credentials")
    st.stop()

# -----------------------------
# 📥 DATA LOADING
# -----------------------------
@st.cache_data(ttl=300)
def load_data():
    main_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRfDuP8FJ8yxoZxPPiKYrxWyP1Brlq7hmyxrkp81_oURiPrCJHqup7Ru8wFoE-pWMEZjZIuH_VBM5_i/pub?output=csv"
    target_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTplHDYVsgbTHNJsFFqLBzbRc4Gj8RYlrjRs4H8NxRy2V7iAFl0-teSToWaSHz5BReD5rSsgVv1sjMs/pub?gid=0&single=true&output=csv"

    df_main = pd.read_csv(main_url)
    df_target = pd.read_csv(target_url)

    df_target.columns = df_target.columns.str.strip()
    df_target["Target"] = pd.to_numeric(df_target["Target"], errors="coerce").fillna(0)

    # merge target into main data
    df_main = df_main.merge(df_target, on="Manager", how="left")
    df_main["Target"] = df_main["Target"].fillna(0)

    # convert numeric
    df_main["Disbursed AMT"] = pd.to_numeric(df_main["Disbursed AMT"], errors="coerce").fillna(0)
    df_main["Total_Revenue"] = pd.to_numeric(df_main["Total_Revenue"], errors="coerce").fillna(0)

    return df_main

df = load_data()

# -----------------------------
# HELPERS
# -----------------------------
def format_inr(x):
    if pd.isna(x): return "₹0"
    return "₹" + "{:,}".format(int(x))

def calc_metrics(f):
    total_disb = f["Disbursed AMT"].sum()
    total_rev = f["Total_Revenue"].sum()
    txn = len(f)
    target = f["Target"].sum()
    achievement = (total_disb / target * 100) if target else 0
    gap = target - total_disb
    return total_disb, total_rev, txn, target, achievement, gap

def colored_metric(label, value, color="#2596be"):
    st.markdown(f"""
        <div style="
            background-color: #EDC7E7;
            padding: 15px;
            border-radius: 10px;
            border-left: 6px solid {color};
            margin-bottom:10px;
        ">
            <p style="font-size:12px; margin:0;"><strong>{label}</strong></p>
            <h3 style="margin:0;">{value}</h3>
        </div>""", unsafe_allow_html=True)

# -----------------------------
# SIDEBAR FILTERS
# -----------------------------
st.sidebar.title("📊 Filters")
dash_type = st.sidebar.radio("Dashboard Type", ["All Managers", "Single Manager", "Comparison"])

managers = sorted(df["Manager"].dropna().unique())
months = sorted(df["Disb Month"].dropna().unique())

# -----------------------------
# ALL MANAGERS DASHBOARD
# -----------------------------
if dash_type == "All Managers":
    st.header("📊 All Managers Summary")
    selected_month = st.sidebar.selectbox("Select Month", months)
    df_f = df[df["Disb Month"]==selected_month]

    if df_f.empty:
        st.warning("No data for this month")
    else:
        agg = df_f.groupby("Manager").agg({
            "Disbursed AMT":"sum",
            "Target":"sum",
            "Total_Revenue":"sum"
        }).reset_index()
        agg["Achievement %"] = (agg["Disbursed AMT"] / agg["Target"] * 100).round(2)
        agg["Disbursed AMT"] = agg["Disbursed AMT"].apply(format_inr)
        agg["Target"] = agg["Target"].apply(format_inr)
        agg["Total_Revenue"] = agg["Total_Revenue"].apply(format_inr)
        st.dataframe(agg)

# -----------------------------
# SINGLE MANAGER DASHBOARD
# -----------------------------
elif dash_type == "Single Manager":
    st.header("📈 Single Manager Dashboard")
    selected_manager = st.sidebar.selectbox("Select Manager", managers)
    selected_month = st.sidebar.selectbox("Select Month", months)
    df_f = df[(df["Manager"]==selected_manager) & (df["Disb Month"]==selected_month)]

    if df_f.empty:
        st.warning("No data")
    else:
        total_disb, total_rev, txn, target, ach, gap = calc_metrics(df_f)
        col1,col2,col3,col4,col5,col6 = st.columns(6)
        with col1: colored_metric("Disbursed AMT", format_inr(total_disb), "#636EFA")
        with col2: colored_metric("Target", format_inr(target), "#AB63FA")
        with col3: colored_metric("Achievement %", f"{ach:.2f}%", "#00CC96")
        with col4: colored_metric("Revenue", format_inr(total_rev), "#19D3F3")
        with col5: colored_metric("Transactions", txn, "#FFA15A")
        with col6: st.write("")

        if gap > 0:
            st.error(f"⚠️ Shortfall: {format_inr(gap)}")
        else:
            st.success(f"🎉 Surplus: {format_inr(abs(gap))}")

        fig = go.Figure()
        fig.add_trace(go.Bar(name="Actual", x=["Performance"], y=[total_disb]))
        fig.add_trace(go.Bar(name="Target", x=["Performance"], y=[target]))
        fig.update_layout(barmode="group", template="plotly_white", title="Target vs Actual")
        st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# COMPARISON DASHBOARD
# -----------------------------
elif dash_type == "Comparison":
    st.header("⚖️ Comparison Dashboard")
    m1 = st.sidebar.selectbox("Manager 1", managers, index=0)
    mo1 = st.sidebar.selectbox("Month 1", months, index=0)
    m2 = st.sidebar.selectbox("Manager 2", managers, index=0)
    mo2 = st.sidebar.selectbox("Month 2", months, index=0)

    df1 = df[(df["Manager"]==m1) & (df["Disb Month"]==mo1)]
    df2 = df[(df["Manager"]==m2) & (df["Disb Month"]==mo2)]

    if df1.empty or df2.empty:
        st.warning("No data")
    else:
        d1,r1,t1,target1,a1,g1 = calc_metrics(df1)
        d2,r2,t2,target2,a2,g2 = calc_metrics(df2)

        label1 = f"{m1} ({mo1})"
        label2 = f"{m2} ({mo2})"

        col1,col2 = st.columns(2)
        with col1:
            colored_metric(label1 + " Disb", format_inr(d1))
            colored_metric("Target", format_inr(target1))
            colored_metric("Ach %", f"{a1:.2f}%")
        with col2:
            colored_metric(label2 + " Disb", format_inr(d2))
            colored_metric("Target", format_inr(target2))
            colored_metric("Ach %", f"{a2:.2f}%")

        fig = go.Figure()
        fig.add_trace(go.Bar(name=label1, x=["Disbursed","Target"], y=[d1,target1]))
        fig.add_trace(go.Bar(name=label2, x=["Disbursed","Target"], y=[d2,target2]))
        fig.update_layout(barmode="group", template="plotly_white", title="Comparison Chart")
        st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# LOGOUT
# -----------------------------
if st.sidebar.button("Logout"):
    st.session_state.login = False
    st.rerun()
