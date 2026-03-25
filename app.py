import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Manager Dashboard", layout="wide")
st_autorefresh(interval=60*1000, key="refresh")

# -----------------------------
# LOGIN
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
            st.error("Invalid Credentials")
    st.stop()

# -----------------------------
# UI CSS
# -----------------------------
st.markdown("""
<style>
div[data-testid="column"] > div:hover {
    transform: scale(1.03);
    transition: 0.2s;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# PREMIUM CARD
# -----------------------------
def colored_metric(label, value, gradient):
    st.markdown(f"""
    <div style="
        background: {gradient};
        padding:18px;
        border-radius:12px;
        color:white;
        box-shadow:0 4px 12px rgba(0,0,0,0.15);
        margin-bottom:10px;">
        <div style="font-size:14px;">{label}</div>
        <div style="font-size:26px;font-weight:bold;">{value}</div>
    </div>
    """, unsafe_allow_html=True)

# -----------------------------
# DATA
# -----------------------------
@st.cache_data(ttl=60)
def load_data():
    url = "https://docs.google.com/spreadsheets/d/1I1ql5NwFafbWXYkVOvv0yvMM9GKnJ5954R4zif2owGI/export?format=csv"
    return pd.read_csv(url)

df = load_data()

# -----------------------------
# HELPERS
# -----------------------------
def format_inr(x):
    return f"₹{int(x):,}" if x else "₹0"

def calc_metrics(f):
    total = f["Disbursed AMT"].sum()
    rev = f["Total_Revenue"].sum()
    payout = (rev/total*100) if total else 0
    return total, rev, payout, len(f)

# -----------------------------
# SIDEBAR
# -----------------------------
dashboard_type = st.sidebar.radio("Dashboard", ["All Managers","Single Manager","Comparison","Campaign Performance"])

# -----------------------------
# ALL MANAGERS
# -----------------------------
if dashboard_type=="All Managers":

    total = df["Disbursed AMT"].sum()
    txn = len(df)
    top_mgr = df.groupby("Manager")["Disbursed AMT"].sum().idxmax()

    col1,col2,col3 = st.columns(3)

    colored_metric("Total Disbursed", format_inr(total),"linear-gradient(135deg,#667eea,#764ba2)")
    colored_metric("Transactions", txn,"linear-gradient(135deg,#fc4a1a,#f7b733)")
    colored_metric("Top Manager", top_mgr,"linear-gradient(135deg,#11998e,#38ef7d)")

    # AI Insight
    st.info(f"📊 Total ₹{int(total):,} disbursed. 🏆 {top_mgr} is leading overall.")

# -----------------------------
# SINGLE MANAGER
# -----------------------------
elif dashboard_type=="Single Manager":

    mgr = st.selectbox("Manager", df["Manager"].unique())
    f = df[df["Manager"]==mgr]

    total, rev, payout, txn = calc_metrics(f)

    col1,col2,col3,col4 = st.columns(4)
    colored_metric("Disbursed",format_inr(total),"linear-gradient(135deg,#667eea,#764ba2)")
    colored_metric("Revenue",format_inr(rev),"linear-gradient(135deg,#11998e,#38ef7d)")
    colored_metric("Payout %",f"{payout:.2f}%","linear-gradient(135deg,#fc4a1a,#f7b733)")
    colored_metric("Txn",txn,"linear-gradient(135deg,#f953c6,#b91d73)")

    top_camp = f.groupby("Campaign")["Disbursed AMT"].sum().idxmax()

    st.info(f"🤖 {mgr} performs best in {top_camp} campaign.")

# -----------------------------
# COMPARISON
# -----------------------------
elif dashboard_type=="Comparison":

    m1 = st.selectbox("Manager 1", df["Manager"].unique())
    m2 = st.selectbox("Manager 2", df["Manager"].unique())

    f1 = df[df["Manager"]==m1]
    f2 = df[df["Manager"]==m2]

    d1,r1,p1,t1 = calc_metrics(f1)
    d2,r2,p2,t2 = calc_metrics(f2)

    col1,col2 = st.columns(2)

    with col1:
        colored_metric(m1,format_inr(d1),"linear-gradient(135deg,#667eea,#764ba2)")
    with col2:
        colored_metric(m2,format_inr(d2),"linear-gradient(135deg,#11998e,#38ef7d)")

    st.info(f"⚖️ {m1} vs {m2}: Higher performer = {m1 if d1>d2 else m2}")

# -----------------------------
# CAMPAIGN
# -----------------------------
elif dashboard_type=="Campaign Performance":

    total = df["Disbursed AMT"].sum()
    rev = df["Total_Revenue"].sum()

    col1,col2,col3 = st.columns(3)
    colored_metric("Total Disbursed",format_inr(total),"linear-gradient(135deg,#667eea,#764ba2)")
    colored_metric("Revenue",format_inr(rev),"linear-gradient(135deg,#11998e,#38ef7d)")
    colored_metric("Campaigns",df["Campaign"].nunique(),"linear-gradient(135deg,#fc4a1a,#f7b733)")

    top_campaign = df.groupby("Campaign")["Disbursed AMT"].sum().idxmax()

    st.info(f"🚀 Top campaign driving growth: {top_campaign}")

# -----------------------------
# LOGOUT
# -----------------------------
if st.sidebar.button("Logout"):
    st.session_state.login=False
    st.rerun()
