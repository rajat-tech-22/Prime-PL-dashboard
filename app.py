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
# LOAD DATA
# -----------------------------
@st.cache_data(ttl=300)
def load_data():
    url = "YOUR MAIN GOOGLE SHEET CSV LINK HERE"
    df = pd.read_csv(url)
    df.replace("null", None, inplace=True)
    return df

@st.cache_data(ttl=300)
def load_target_data():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTplHDYVsgbTHNJsFFqLBzbRc4Gj8RYlrjRs4H8NxRy2V7iAFl0-teSToWaSHz5BReD5rSsgVv1sjMs/pub?gid=0&single=true&output=csv"
    df_target = pd.read_csv(url)
    df_target.columns = df_target.columns.str.strip()
    df_target["Target"] = pd.to_numeric(df_target["Target"], errors="coerce").fillna(0)
    return df_target

df = load_data()
target_df = load_target_data()

df = df.merge(target_df, on="Manager", how="left")
df["Target"] = df["Target"].fillna(0)

df["Disbursed AMT"] = pd.to_numeric(df["Disbursed AMT"], errors="coerce")
df["Total_Revenue"] = pd.to_numeric(df["Total_Revenue"], errors="coerce")

# -----------------------------
# FUNCTIONS
# -----------------------------
def format_inr(x):
    return f"₹{int(x):,}"

def calc_metrics(f):
    total_disb = f["Disbursed AMT"].sum()
    total_rev = f["Total_Revenue"].sum()
    txn = len(f)

    target = f["Target"].sum()
    achievement = (total_disb/target*100) if target else 0
    gap = target - total_disb

    return total_disb, total_rev, txn, target, achievement, gap

def metric(label, value):
    st.markdown(f"**{label}**  \n{value}")

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.title("Filters")

dashboard_type = st.sidebar.radio("Dashboard", [
    "All Managers",
    "Single Manager",
    "Comparison"
])

managers = sorted(df["Manager"].dropna().unique())
months = sorted(df["Disb Month"].dropna().unique())

# -----------------------------
# ALL MANAGERS
# -----------------------------
if dashboard_type == "All Managers":

    month = st.sidebar.selectbox("Month", months)

    f = df[df["Disb Month"] == month]

    agg = f.groupby("Manager").agg({
        "Disbursed AMT":"sum",
        "Target":"sum"
    }).reset_index()

    agg["Achievement %"] = (agg["Disbursed AMT"]/agg["Target"]*100)

    st.dataframe(agg)

# -----------------------------
# SINGLE MANAGER
# -----------------------------
elif dashboard_type == "Single Manager":

    manager = st.sidebar.selectbox("Manager", managers)
    month = st.sidebar.selectbox("Month", months)

    f = df[(df["Manager"]==manager)&(df["Disb Month"]==month)]

    if f.empty:
        st.warning("No Data")
        st.stop()

    total_disb,total_rev,txn,target,ach,gap = calc_metrics(f)

    col1,col2,col3,col4,col5 = st.columns(5)

    with col1: metric("Disbursed", format_inr(total_disb))
    with col2: metric("Target", format_inr(target))
    with col3: metric("Ach %", f"{ach:.2f}%")
    with col4: metric("Revenue", format_inr(total_rev))
    with col5: metric("Txn", txn)

    if gap > 0:
        st.error(f"Shortfall: {format_inr(gap)}")
    else:
        st.success(f"Surplus: {format_inr(abs(gap))}")

    fig = go.Figure()
    fig.add_bar(name="Actual", x=["Performance"], y=[total_disb])
    fig.add_bar(name="Target", x=["Performance"], y=[target])
    st.plotly_chart(fig)

# -----------------------------
# COMPARISON
# -----------------------------
elif dashboard_type == "Comparison":

    m1 = st.sidebar.selectbox("Manager 1", managers)
    mo1 = st.sidebar.selectbox("Month 1", months)

    m2 = st.sidebar.selectbox("Manager 2", managers)
    mo2 = st.sidebar.selectbox("Month 2", months)

    f1 = df[(df["Manager"]==m1)&(df["Disb Month"]==mo1)]
    f2 = df[(df["Manager"]==m2)&(df["Disb Month"]==mo2)]

    if f1.empty or f2.empty:
        st.warning("No Data")
        st.stop()

    d1,r1,t1,target1,a1,g1 = calc_metrics(f1)
    d2,r2,t2,target2,a2,g2 = calc_metrics(f2)

    label1 = f"{m1} ({mo1})"
    label2 = f"{m2} ({mo2})"

    col1,col2 = st.columns(2)

    with col1:
        st.subheader(label1)
        metric("Disbursed", format_inr(d1))
        metric("Target", format_inr(target1))
        metric("Ach %", f"{a1:.2f}%")

    with col2:
        st.subheader(label2)
        metric("Disbursed", format_inr(d2))
        metric("Target", format_inr(target2))
        metric("Ach %", f"{a2:.2f}%")

    fig = go.Figure()
    fig.add_bar(name=label1, x=["Disbursed","Target"], y=[d1,target1])
    fig.add_bar(name=label2, x=["Disbursed","Target"], y=[d2,target2])
    st.plotly_chart(fig)

# -----------------------------
# LOGOUT
# -----------------------------
if st.sidebar.button("Logout"):
    st.session_state.login = False
    st.rerun()
