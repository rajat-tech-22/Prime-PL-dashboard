import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from streamlit_autorefresh import st_autorefresh

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(page_title="Executive Manager Dashboard", layout="wide")
st_autorefresh(interval=60*1000, key="refresh")

# -----------------------------
# 🔐 LOGIN SYSTEM
# -----------------------------
USERNAME, PASSWORD = "PrimePL", "@1234"
if "login" not in st.session_state: st.session_state.login = False

if not st.session_state.login:
    st.title("🔐 Portfolio Login")
    u = st.text_input("Username", value="PrimePL")
    p = st.text_input("Password", type="password")
    if st.button("Login"):
        if u == USERNAME and p == PASSWORD:
            st.session_state.login = True
            st.rerun()
        else: st.error("Invalid Credentials")
    st.stop()

# -----------------------------
# Global Styling (CSS)
# -----------------------------
st.markdown("""
    <style>
    .main { background-color: #f4f7f9; }
    [data-testid="stSidebar"] { background-color: #2596be; }
    .stMetric { background-color: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)

# -----------------------------
# Data Loading
# -----------------------------
@st.cache_data(ttl=60)
def load_data():
    url = "https://docs.google.com/spreadsheets/d/1I1ql5NwFafbWXYkVOvv0yvMM9GKnJ5954R4zif2owGI/export?format=csv"
    df = pd.read_csv(url)
    df.replace("null", None, inplace=True)
    return df

df = load_data()

# -----------------------------
# Pro-Helper Functions
# -----------------------------
def format_inr(number):
    if not number or number == 0: return "₹0"
    s = str(int(number))
    last3, rest = s[-3:], s[:-3]
    parts = []
    while len(rest) > 2:
        parts.append(rest[-2:]); rest = rest[:-2]
    if rest: parts.append(rest)
    parts.reverse()
    return "₹" + ",".join(parts) + "," + last3 if parts else "₹" + last3

def get_delta(current, previous):
    if previous and previous > 0:
        return ((current - previous) / previous) * 100
    return None

def colored_metric_pro(label, value, delta=None, color="#2596be"):
    delta_html = ""
    if delta is not None:
        color_d = "#28a745" if delta >= 0 else "#dc3545"
        arrow = "▲" if delta >= 0 else "▼"
        delta_html = f'<span style="color:{color_d}; font-size:14px; font-weight:bold; margin-left:10px;">{arrow} {abs(delta):.1f}%</span>'
    
    st.markdown(f"""
        <div style="background: white; padding: 20px; border-radius: 12px; border-top: 5px solid {color}; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 15px;">
            <p style="color: #6c757d; font-size: 12px; font-weight: 700; text-transform: uppercase; margin:0;">{label}</p>
            <div style="display: flex; align-items: baseline;">
                <h2 style="margin: 5px 0 0 0; font-size: 24px; font-weight: 800; color: #1a1a1a;">{value}</h2>
                {delta_html}
            </div>
        </div>
    """, unsafe_allow_html=True)

# -----------------------------
# Sidebar Filters
# -----------------------------
st.sidebar.title("📊 Control Panel")
dashboard_type = st.sidebar.radio("Navigation", ["All Managers", "Single Manager", "Comparison", "Campaign Analysis"])

months = sorted(df["Disb Month"].dropna().unique())
managers = sorted(df["Manager"].dropna().unique())
curr_month = months[-1]
prev_month = months[-2] if len(months) > 1 else None

# -----------------------------
# 1. All Managers Dashboard
# -----------------------------
if dashboard_type == "All Managers":
    st.header(f"🏢 Portfolio Overview - {curr_month}")
    
    # Filtering for Delta calculation
    f_curr = df[df["Disb Month"] == curr_month]
    f_prev = df[df["Disb Month"] == prev_month] if prev_month else pd.DataFrame()

    c_disb = f_curr["Disbursed AMT"].sum()
    p_disb = f_prev["Disbursed AMT"].sum()
    d_disb = get_delta(c_disb, p_disb)

    c_txn = len(f_curr)
    p_txn = len(f_prev)
    d_txn = get_delta(c_txn, p_txn)

    col1, col2, col3 = st.columns(3)
    with col1: colored_metric_pro("Total Disbursed", format_inr(c_disb), d_disb, "#636EFA")
    with col2: colored_metric_pro("Total Transactions", f"{c_txn:,}", d_txn, "#EF553B")
    with col3:
        top_mgr = f_curr.groupby("Manager")["Disbursed AMT"].sum().idxmax()
        colored_metric_pro("Top Performer", top_mgr, None, "#00CC96")

    st.subheader("📄 Manager Performance Breakdown")
    agg = f_curr.groupby("Manager").agg({"Disbursed AMT": "sum", "Total_Revenue": "sum", "Vertical": "count"}).reset_index()
    agg.columns = ["Manager", "Disbursed", "Revenue", "Count"]
    agg["Disbursed"] = agg["Disbursed"].apply(format_inr)
    st.dataframe(agg, use_container_width=True)

# -----------------------------
# 2. Single Manager Dashboard
# -----------------------------
elif dashboard_type == "Single Manager":
    sel_mgr = st.sidebar.selectbox("Select Manager", managers)
    st.header(f"📈 Performance Insights: {sel_mgr}")

    m_curr = df[(df["Manager"] == sel_mgr) & (df["Disb Month"] == curr_month)]
    m_prev = df[(df["Manager"] == sel_mgr) & (df["Disb Month"] == prev_month)]

    if m_curr.empty:
        st.warning("No data found for this manager in current month.")
    else:
        disb = m_curr["Disbursed AMT"].sum()
        rev = m_curr["Total_Revenue"].sum()
        d_disb = get_delta(disb, m_prev["Disbursed AMT"].sum())
        
        c1, c2, c3, c4 = st.columns(4)
        with c1: colored_metric_pro("Disbursed", format_inr(disb), d_disb, "#636EFA")
        with c2: colored_metric_pro("Revenue", format_inr(rev), None, "#00CC96")
        with c3: colored_metric_pro("Avg Payout", f"{(rev/disb*100):.2f}%", None, "#EF553B")
        with c4: colored_metric_pro("Leads", len(m_curr), None, "#FFA15A")

        # Charts
        col_left, col_right = st.columns(2)
        with col_left:
            bank_sum = m_curr.groupby("Bank")["Disbursed AMT"].sum().sort_values()
            fig = go.Figure(go.Bar(y=bank_sum.index, x=bank_sum.values/100000, orientation='h', marker_color='#636EFA'))
            fig.update_layout(title="Bank Wise (Lakhs)", height=300)
            st.plotly_chart(fig, use_container_width=True)
        with col_right:
            camp_sum = m_curr.groupby("Campaign")["Disbursed AMT"].sum()
            fig = go.Figure(go.Pie(labels=camp_sum.index, values=camp_sum.values, hole=.5))
            fig.update_layout(title="Campaign Mix", height=300)
            st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# 3. Comparison & 4. Campaign Analysis
# -----------------------------
# (Note: Use similar logic for Comparison and Campaign Analysis)
else:
    st.info("Select Comparison or Campaign Analysis from sidebar to view detailed benchmarks.")

# -----------------------------
# Footer
# -----------------------------
if st.sidebar.button("Logout"):
    st.session_state.login = False
    st.rerun()
