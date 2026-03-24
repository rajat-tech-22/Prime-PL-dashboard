import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from io import BytesIO

st.set_page_config(page_title="Manager Dashboard", layout="wide")

# -----------------------------
# 🔐 SIMPLE LOGIN SYSTEM
# -----------------------------
users = {
    "admin": "admin123",
    "manager1": "1234",
    "manager2": "1234"
}

if "login" not in st.session_state:
    st.session_state.login = False

if not st.session_state.login:
    st.title("🔐 Login")

    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        if u in users and users[u] == p:
            st.session_state.login = True
            st.success("Login Successful")
            st.rerun()
        else:
            st.error("Invalid Credentials")
    st.stop()

# -----------------------------
# Sidebar Theme
# -----------------------------
st.markdown("""
<style>
[data-testid="stSidebar"] {
    background-color: #0E1117;
    color: white;
}
[data-testid="stSidebar"] label {
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Load Data
# -----------------------------
@st.cache_data
def load_data():
    url = "https://docs.google.com/spreadsheets/d/1I1ql5NwFafbWXYkVOvv0yvMM9GKnJ5954R4zif2owGI/export?format=csv"
    df = pd.read_csv(url)

    df["Disbursed AMT"] = pd.to_numeric(df["Disbursed AMT"], errors='coerce')
    df["Total_Revenue"] = pd.to_numeric(df["Total_Revenue"], errors='coerce')

    return df

df = load_data()

# -----------------------------
# Helper
# -----------------------------
def format_inr(x):
    return f"₹{int(x):,}" if pd.notna(x) else "₹0"

def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.title("📊 Filters")
dashboard = st.sidebar.radio(
    "Dashboard",
    ["All Managers","Single Manager","Target vs Achievement","Monthly Trend"]
)

months = sorted(df["Disb Month"].dropna().unique())
managers = sorted(df["Manager"].dropna().unique())

# -----------------------------
# 🏢 ALL MANAGERS
# -----------------------------
if dashboard == "All Managers":

    month = st.sidebar.selectbox("Month", months)

    f = df[df["Disb Month"]==month]

    st.title("📊 All Managers")

    agg = f.groupby("Manager").agg(
        Disbursed=("Disbursed AMT","sum"),
        Revenue=("Total_Revenue","sum"),
        Count=("Manager","count")
    ).reset_index()

    # KPI
    c1,c2,c3 = st.columns(3)
    c1.metric("Total Disbursed", format_inr(agg["Disbursed"].sum()))
    c2.metric("Total Revenue", format_inr(agg["Revenue"].sum()))
    c3.metric("Total Txn", agg["Count"].sum())

    # Top performer
    top = agg.sort_values("Disbursed", ascending=False).iloc[0]
    st.success(f"🏆 Top Performer: {top['Manager']}")

    st.dataframe(agg, use_container_width=True)

    st.download_button("Download Excel", to_excel(agg), "all.xlsx")

# -----------------------------
# 👤 SINGLE MANAGER
# -----------------------------
elif dashboard == "Single Manager":

    m = st.sidebar.selectbox("Manager", managers)
    month = st.sidebar.selectbox("Month", months)

    f = df[(df["Manager"]==m)&(df["Disb Month"]==month)]

    st.title(f"📈 {m}")

    d = f["Disbursed AMT"].sum()
    r = f["Total_Revenue"].sum()

    st.metric("Disbursed", format_inr(d))
    st.metric("Revenue", format_inr(r))

# -----------------------------
# 🎯 TARGET VS ACHIEVEMENT
# -----------------------------
elif dashboard == "Target vs Achievement":

    st.title("🎯 Target vs Achievement")

    # manual targets
    targets = {
        "manager1": 5000000,
        "manager2": 4000000,
    }

    agg = df.groupby("Manager")["Disbursed AMT"].sum().reset_index()

    agg["Target"] = agg["Manager"].map(targets)
    agg["Achievement %"] = (agg["Disbursed AMT"]/agg["Target"]*100).round(2)

    st.dataframe(agg, use_container_width=True)

    fig = go.Figure()
    fig.add_bar(x=agg["Manager"], y=agg["Disbursed AMT"], name="Achieved")
    fig.add_bar(x=agg["Manager"], y=agg["Target"], name="Target")

    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# 📊 MONTHLY TREND
# -----------------------------
elif dashboard == "Monthly Trend":

    st.title("📊 Monthly Trend")

    trend = df.groupby("Disb Month")["Disbursed AMT"].sum().reset_index()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=trend["Disb Month"],
        y=trend["Disbursed AMT"],
        mode='lines+markers'
    ))

    st.plotly_chart(fig, use_container_width=True)
