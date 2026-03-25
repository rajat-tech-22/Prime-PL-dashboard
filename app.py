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
# 🔐 LOGIN
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
            st.rerun()
        else:
            st.error("Invalid Credentials ❌")

    st.stop()

# -----------------------------
# CSS
# -----------------------------
st.markdown("""
<style>
[data-testid="stSidebar"] {
    background-color: #2596be;
}
.main {
    background-color: #f8f9fa;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data(ttl=60)
def load_data():
    url = "https://docs.google.com/spreadsheets/d/1I1ql5NwFafbWXYkVOvv0yvMM9GKnJ5954R4zif2owGI/export?format=csv"
    df = pd.read_csv(url)
    df.replace("null", None, inplace=True)
    return df

df = load_data()

# -----------------------------
# HELPERS
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

# -----------------------------
# 🤖 AI INSIGHTS FUNCTION
# -----------------------------
def generate_ai_insights(df):
    if df.empty:
        return "No insights available"

    total_disb = df["Disbursed AMT"].sum()
    total_rev = df["Total_Revenue"].sum()
    avg_payout = (total_rev / total_disb * 100) if total_disb else 0

    top_manager = df.groupby("Manager")["Disbursed AMT"].sum().idxmax()
    low_manager = df.groupby("Manager")["Disbursed AMT"].sum().idxmin()

    top_bank = df.groupby("Bank")["Disbursed AMT"].sum().idxmax()
    top_campaign = df.groupby("Campaign")["Disbursed AMT"].sum().idxmax()
    low_campaign = df.groupby("Campaign")["Disbursed AMT"].sum().idxmin()

    return f"""
📊 Total Disbursed: {format_inr(total_disb)}  
💰 Total Revenue: {format_inr(total_rev)}  
📈 Avg Payout: {avg_payout:.2f}%  

🏆 Best Manager: {top_manager}  
⚠️ Low Performer: {low_manager}  

🏦 Top Bank: {top_bank}  
🚀 Top Campaign: {top_campaign}  
📉 Weak Campaign: {low_campaign}  

📌 Recommendation: Focus on {top_campaign} and improve {low_campaign}
"""

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.title("📊 Filters")
dashboard_type = st.sidebar.radio(
    "Dashboard",
    ["All Managers", "Single Manager", "Comparison", "Campaign Performance"]
)

months = sorted(df["Disb Month"].dropna().unique())
managers = sorted(df["Manager"].dropna().unique())

# -----------------------------
# 1️⃣ ALL MANAGERS
# -----------------------------
if dashboard_type == "All Managers":

    selected_month = st.sidebar.selectbox("Month", months, index=len(months)-1)
    filtered_df = df[df["Disb Month"] == selected_month]

    st.header("📊 All Managers Overview")

    total = filtered_df["Disbursed AMT"].sum()
    st.metric("Total Disbursed", format_inr(total))

    st.dataframe(filtered_df)

    # ✅ AI Insights
    st.markdown("### 🤖 AI Insights")
    st.info(generate_ai_insights(filtered_df))

# -----------------------------
# 2️⃣ SINGLE MANAGER
# -----------------------------
elif dashboard_type == "Single Manager":

    m = st.sidebar.selectbox("Manager", managers)
    month = st.sidebar.selectbox("Month", months, index=len(months)-1)

    f = df[(df["Manager"]==m) & (df["Disb Month"]==month)]

    st.header(f"📈 {m}")

    if not f.empty:
        d,r,p,txn,avg,_,_,_ = calc_metrics(f)

        st.metric("Disbursed", format_inr(d))
        st.metric("Revenue", format_inr(r))

        st.dataframe(f)

        # ✅ AI Insights
        st.markdown("### 🤖 AI Insights")
        st.info(generate_ai_insights(f))

# -----------------------------
# 3️⃣ COMPARISON
# -----------------------------
elif dashboard_type == "Comparison":

    m1 = st.sidebar.selectbox("Manager 1", managers)
    m2 = st.sidebar.selectbox("Manager 2", managers)

    f1 = df[df["Manager"]==m1]
    f2 = df[df["Manager"]==m2]

    st.header("⚖️ Comparison")

    col1,col2 = st.columns(2)

    with col1:
        st.subheader(m1)
        st.info(generate_ai_insights(f1))

    with col2:
        st.subheader(m2)
        st.info(generate_ai_insights(f2))

# -----------------------------
# 4️⃣ CAMPAIGN
# -----------------------------
elif dashboard_type == "Campaign Performance":

    month = st.sidebar.selectbox("Month", months, index=len(months)-1)
    camp_df = df[df["Disb Month"]==month]

    st.header("📊 Campaign Performance")

    st.dataframe(camp_df)

    # ✅ AI Insights (already but improved)
    st.markdown("### 🤖 AI Insights")
    st.info(generate_ai_insights(camp_df))

# -----------------------------
# LOGOUT
# -----------------------------
if st.sidebar.button("🚪 Logout"):
    st.session_state.login = False
    st.rerun()
