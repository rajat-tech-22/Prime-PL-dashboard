import streamlit as st
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
from streamlit_autorefresh import st_autorefresh
import os
import time
from datetime import datetime, timedelta, timezone
import numpy as np

# ═══════════════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Prime PL Dashboard 🚀",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Auto refresh every minute
st_autorefresh(interval=60 * 1000, key="refresh")

# ═══════════════════════════════════════════════════════════════
# WORKING CSS - TESTED & VERIFIED
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap');

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: 'Poppins', sans-serif !important;
}

/* Animated Gradient Background */
.stApp {
    background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
    background-size: 400% 400%;
    animation: gradient 15s ease infinite;
}

@keyframes gradient {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* Glass Card Effect */
.glass-box {
    background: rgba(255, 255, 255, 0.15);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    border: 1px solid rgba(255, 255, 255, 0.3);
    padding: 30px;
    box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
    transition: all 0.3s ease;
}

.glass-box:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 40px 0 rgba(31, 38, 135, 0.5);
}

/* Metric Cards */
.metric-box {
    background: linear-gradient(135deg, rgba(255,255,255,0.2), rgba(255,255,255,0.05));
    backdrop-filter: blur(10px);
    border-radius: 20px;
    border: 2px solid rgba(255,255,255,0.4);
    padding: 25px;
    text-align: center;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

.metric-box:hover {
    transform: scale(1.05) translateY(-5px);
    box-shadow: 0 8px 30px rgba(255,255,255,0.3);
    border-color: rgba(255,255,255,0.8);
}

.metric-label {
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: rgba(255,255,255,0.9);
    margin-bottom: 10px;
}

.metric-value {
    font-size: 36px;
    font-weight: 800;
    color: white;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

.metric-icon {
    font-size: 30px;
    margin-bottom: 10px;
}

/* Title Styling */
.main-title {
    font-size: 48px;
    font-weight: 800;
    text-align: center;
    color: white;
    text-shadow: 3px 3px 6px rgba(0,0,0,0.3);
    margin: 20px 0;
    animation: fadeInDown 1s ease;
}

@keyframes fadeInDown {
    from {
        opacity: 0;
        transform: translateY(-20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Sidebar Styling */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
}

[data-testid="stSidebar"] * {
    color: white !important;
}

[data-testid="stSidebar"] .stRadio > label {
    color: white !important;
    font-weight: 600 !important;
}

[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
    background: rgba(255,255,255,0.1);
    border-radius: 10px;
    padding: 10px;
    margin: 5px 0;
    border: 1px solid rgba(255,255,255,0.2);
    transition: all 0.3s ease;
}

[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {
    background: rgba(255,255,255,0.2);
    transform: translateX(5px);
}

/* Button Styling */
.stButton > button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 12px 30px;
    font-weight: 700;
    font-size: 16px;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    transition: all 0.3s ease;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
}

/* Progress Bar */
.progress-bar-container {
    background: rgba(255,255,255,0.2);
    border-radius: 20px;
    height: 25px;
    overflow: hidden;
    margin: 15px 0;
    position: relative;
}

.progress-bar-fill {
    height: 100%;
    border-radius: 20px;
    background: linear-gradient(90deg, #667eea, #764ba2);
    transition: width 0.5s ease;
    box-shadow: 0 0 10px rgba(102, 126, 234, 0.5);
}

.progress-text {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    color: white;
    font-weight: 700;
    font-size: 12px;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
}

/* Leaderboard Card */
.leader-box {
    background: linear-gradient(135deg, rgba(255,255,255,0.2), rgba(255,255,255,0.1));
    backdrop-filter: blur(10px);
    border-radius: 15px;
    padding: 20px;
    margin: 10px 0;
    border: 1px solid rgba(255,255,255,0.3);
    display: flex;
    align-items: center;
    gap: 20px;
    transition: all 0.3s ease;
}

.leader-box:hover {
    transform: translateX(10px);
    box-shadow: 0 5px 20px rgba(255,255,255,0.2);
}

.rank-number {
    font-size: 28px;
    font-weight: 900;
    color: white;
    min-width: 50px;
    text-align: center;
}

.leader-name {
    font-size: 18px;
    font-weight: 700;
    color: white;
}

.leader-value {
    font-size: 22px;
    font-weight: 800;
    color: white;
    margin-left: auto;
}

/* Alert Cards */
.alert-box {
    border-radius: 15px;
    padding: 20px;
    margin: 15px 0;
    display: flex;
    align-items: center;
    gap: 15px;
    backdrop-filter: blur(10px);
}

.alert-critical {
    background: rgba(239, 68, 68, 0.3);
    border: 2px solid rgba(239, 68, 68, 0.6);
}

.alert-warning {
    background: rgba(245, 158, 11, 0.3);
    border: 2px solid rgba(245, 158, 11, 0.6);
}

.alert-success {
    background: rgba(16, 185, 129, 0.3);
    border: 2px solid rgba(16, 185, 129, 0.6);
}

/* Hide Streamlit Elements */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════
def format_inr(n):
    if not n or n == 0: return "₹0"
    s = str(int(n))
    last3 = s[-3:]
    rest = s[:-3]
    parts = []
    while len(rest) > 2:
        parts.append(rest[-2:])
        rest = rest[:-2]
    if rest:
        parts.append(rest)
    parts.reverse()
    return "₹" + ",".join(parts) + "," + last3 if parts else "₹" + last3

def metric_card(label, value, icon, color="#667eea"):
    return f"""
    <div class="metric-box">
        <div class="metric-icon">{icon}</div>
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
    </div>
    """

# ═══════════════════════════════════════════════════════════════
# DATA LOADING
# ═══════════════════════════════════════════════════════════════
@st.cache_data(ttl=60)
def load_data():
    url = "https://docs.google.com/spreadsheets/d/1I1ql5NwFafbWXYkVOvv0yvMM9GKnJ5954R4zif2owGI/export?format=csv"
    df = pd.read_csv(url)
    df.replace("null", None, inplace=True)
    if "DISB DATE" in df.columns:
        df["DISB DATE"] = pd.to_datetime(df["DISB DATE"], errors="coerce")
    if "Disb Month" in df.columns:
        sample_series = df["Disb Month"].dropna()
        if not sample_series.empty:
            sample_str = str(sample_series.iloc[0]).strip()
            is_date_fmt = False
            for fmt in ["%Y/%m/%d", "%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"]:
                try:
                    datetime.strptime(sample_str, fmt)
                    is_date_fmt = True
                    break
                except:
                    continue
            if is_date_fmt:
                df["Disb Month"] = pd.to_datetime(df["Disb Month"], errors="coerce").dt.strftime("%b %Y")
    return df

@st.cache_data(ttl=120)
def load_targets():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTplHDYVsgbTHNJsFFqLBzbRc4Gj8RYlrjRs4H8NxRy2V7iAFl0-teSToWaSHz5BReD5rSsgVv1sjMs/pub?output=csv"
    try:
        tdf = pd.read_csv(url)
        tdf.columns = tdf.columns.str.strip()
        return tdf, None
    except Exception as e:
        return pd.DataFrame(), str(e)

def get_target_for_manager(mgr_name, month_name, tdf):
    if tdf is None or tdf.empty:
        return 0.0
    cols_lower = {c.lower().strip(): c for c in tdf.columns}
    mgr_col = next((cols_lower[k] for k in ["manager", "name", "manager name"] if k in cols_lower), None)
    tgt_col = next((cols_lower[k] for k in ["target", "target (l)", "target_l"] if k in cols_lower), None)
    if not mgr_col or not tgt_col:
        return 0.0
    mgr_rows = tdf[tdf[mgr_col].astype(str).str.strip().str.lower() == mgr_name.strip().lower()]
    if mgr_rows.empty:
        return 0.0
    try:
        return float(str(mgr_rows.iloc[0][tgt_col]).replace(",", "").replace("₹", "").strip())
    except:
        return 0.0

# ═══════════════════════════════════════════════════════════════
# AUTH
# ═══════════════════════════════════════════════════════════════
USERNAME = os.getenv("APP_USERNAME", "Mymoneymantra")
PASSWORD = os.getenv("APP_PASSWORD", "Prime110")

if "login" not in st.session_state:
    st.session_state.login = False

# ═══════════════════════════════════════════════════════════════
# LOGIN PAGE
# ═══════════════════════════════════════════════════════════════
if not st.session_state.login:
    st.markdown('<div class="main-title">🚀 PRIME PL DASHBOARD 🚀</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div class="glass-box" style="text-align:center;">
            <h2 style="color:white;margin-bottom:20px;">🔐 LOGIN</h2>
            <p style="color:rgba(255,255,255,0.8);margin-bottom:30px;">Enter your credentials to access the dashboard</p>
        </div>
        """, unsafe_allow_html=True)
        
        username = st.text_input("👤 Username", placeholder="Enter username")
        password = st.text_input("🔒 Password", type="password", placeholder="Enter password")
        
        if st.button("🚀 LOGIN", use_container_width=True):
            if username == USERNAME and password == PASSWORD:
                st.session_state.login = True
                st.success("✅ Login Successful!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("❌ Invalid credentials")
    
    st.stop()

# ═══════════════════════════════════════════════════════════════
# LOAD DATA
# ═══════════════════════════════════════════════════════════════
df = load_data()
target_raw, target_err = load_targets()
months = sorted(df["Disb Month"].dropna().unique())
current_month_index = len(months) - 1

# ═══════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 💼 Prime PL Dashboard")
    st.markdown("---")
    
    dashboard_type = st.radio(
        "Select Dashboard",
        ["🏠 Overview", "👤 Manager View", "🏆 Leaderboard", "🎯 Target Tracker"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.login = False
        st.rerun()

# ═══════════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════════
ist_tz = timezone(timedelta(hours=5, minutes=30))
now_ist = datetime.now(ist_tz)
hour = now_ist.hour

if 5 <= hour < 12:
    greet = "Good Morning 🌅"
elif hour < 16:
    greet = "Good Afternoon ☀️"
elif hour < 20:
    greet = "Good Evening 🌇"
else:
    greet = "Good Night 🌙"

st.markdown(f"""
<div class="glass-box">
    <h1 style="color:white;font-size:32px;margin:0;">{greet}</h1>
    <p style="color:rgba(255,255,255,0.8);margin:10px 0 0 0;">{now_ist.strftime("%A, %d %B %Y • %I:%M %p IST")}</p>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# 🏠 OVERVIEW DASHBOARD
# ═══════════════════════════════════════════════════════════════
if dashboard_type == "🏠 Overview":
    st.markdown('<div class="main-title" style="font-size:36px;">📊 OVERVIEW DASHBOARD</div>', unsafe_allow_html=True)
    
    # FILTERS
    with st.sidebar:
        st.markdown("### 🔧 Filters")
        selected_month = st.selectbox("Month", months, index=current_month_index)
    
    filtered_df = df[df["Disb Month"] == selected_month]
    
    if filtered_df.empty:
        st.warning("⚠️ No data available for selected filters")
    else:
        # METRICS
        total_disb = filtered_df["Disbursed AMT"].sum()
        total_rev = filtered_df["Total_Revenue"].sum()
        total_txns = len(filtered_df)
        avg_payout = (total_rev / total_disb * 100) if total_disb else 0
        
        cols = st.columns(4)
        
        with cols[0]:
            st.markdown(metric_card("Total Disbursed", format_inr(total_disb), "💰"), unsafe_allow_html=True)
        
        with cols[1]:
            st.markdown(metric_card("Total Revenue", format_inr(total_rev), "📈"), unsafe_allow_html=True)
        
        with cols[2]:
            st.markdown(metric_card("Avg Payout", f"{avg_payout:.2f}%", "📊"), unsafe_allow_html=True)
        
        with cols[3]:
            st.markdown(metric_card("Transactions", f"{total_txns:,}", "🔁"), unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # CHARTS
        st.markdown('<div class="glass-box"><h3 style="color:white;">📊 Campaign Performance</h3></div>', unsafe_allow_html=True)
        
        campaign_data = filtered_df.groupby("Campaign")["Disbursed AMT"].sum().reset_index()
        campaign_data = campaign_data.sort_values("Disbursed AMT", ascending=False).head(10)
        
        fig = go.Figure(go.Bar(
            x=campaign_data["Campaign"],
            y=campaign_data["Disbursed AMT"] / 100000,
            text=[f"₹{v/100000:.1f}L" for v in campaign_data["Disbursed AMT"]],
            textposition="outside",
            marker=dict(
                color=campaign_data["Disbursed AMT"],
                colorscale="Viridis",
                line=dict(color='white', width=2)
            )
        ))
        
        fig.update_layout(
            template="plotly_dark",
            height=500,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white', size=14),
            yaxis_title="Amount (Lakhs)",
            xaxis_tickangle=-45,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # MANAGER TABLE
        st.markdown('<div class="glass-box"><h3 style="color:white;">👥 Manager Performance</h3></div>', unsafe_allow_html=True)
        
        mgr_data = filtered_df.groupby("Manager").agg({
            "Disbursed AMT": "sum",
            "Total_Revenue": "sum",
            "Manager": "count"
        }).reset_index()
        
        mgr_data.columns = ["Manager", "Disbursed", "Revenue", "Transactions"]
        mgr_data["Disbursed"] = mgr_data["Disbursed"].apply(format_inr)
        mgr_data["Revenue"] = mgr_data["Revenue"].apply(format_inr)
        
        st.dataframe(mgr_data, use_container_width=True, height=400)


# ═══════════════════════════════════════════════════════════════
# 👤 MANAGER VIEW
# ═══════════════════════════════════════════════════════════════
elif dashboard_type == "👤 Manager View":
    st.markdown('<div class="main-title" style="font-size:36px;">👤 MANAGER VIEW</div>', unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown("### 🔧 Filters")
        sel_month = st.selectbox("Month", months, index=current_month_index, key="mgr_month")
        mgr_list = sorted(df[df["Disb Month"] == sel_month]["Manager"].dropna().unique())
        sel_mgr = st.selectbox("Manager", mgr_list)
    
    mgr_df = df[(df["Disb Month"] == sel_month) & (df["Manager"] == sel_mgr)]
    
    if mgr_df.empty:
        st.warning("⚠️ No data available")
    else:
        total_disb = mgr_df["Disbursed AMT"].sum()
        total_rev = mgr_df["Total_Revenue"].sum()
        total_txns = len(mgr_df)
        avg_payout = (total_rev / total_disb * 100) if total_disb else 0
        
        st.markdown(f"""
        <div class="glass-box" style="text-align:center;">
            <h2 style="color:white;font-size:36px;margin-bottom:10px;">👤 {sel_mgr}</h2>
            <p style="color:rgba(255,255,255,0.8);">{sel_month}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        cols = st.columns(4)
        
        with cols[0]:
            st.markdown(metric_card("Disbursed", format_inr(total_disb), "💰"), unsafe_allow_html=True)
        
        with cols[1]:
            st.markdown(metric_card("Revenue", format_inr(total_rev), "📈"), unsafe_allow_html=True)
        
        with cols[2]:
            st.markdown(metric_card("Payout %", f"{avg_payout:.2f}%", "📊"), unsafe_allow_html=True)
        
        with cols[3]:
            st.markdown(metric_card("Deals", f"{total_txns:,}", "🔁"), unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # CHARTS
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="glass-box"><h3 style="color:white;">Campaign Breakdown</h3></div>', unsafe_allow_html=True)
            
            camp_data = mgr_df.groupby("Campaign")["Disbursed AMT"].sum().reset_index()
            
            fig_pie = go.Figure(go.Pie(
                labels=camp_data["Campaign"],
                values=camp_data["Disbursed AMT"],
                hole=0.4,
                textinfo='label+percent',
                marker=dict(line=dict(color='white', width=2))
            ))
            
            fig_pie.update_layout(
                template="plotly_dark",
                height=400,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white', size=12),
                showlegend=False
            )
            
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            st.markdown('<div class="glass-box"><h3 style="color:white;">Bank Breakdown</h3></div>', unsafe_allow_html=True)
            
            bank_data = mgr_df.groupby("Bank")["Disbursed AMT"].sum().reset_index()
            
            fig_pie2 = go.Figure(go.Pie(
                labels=bank_data["Bank"],
                values=bank_data["Disbursed AMT"],
                hole=0.4,
                textinfo='label+percent',
                marker=dict(line=dict(color='white', width=2))
            ))
            
            fig_pie2.update_layout(
                template="plotly_dark",
                height=400,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white', size=12),
                showlegend=False
            )
            
            st.plotly_chart(fig_pie2, use_container_width=True)


# ═══════════════════════════════════════════════════════════════
# 🏆 LEADERBOARD
# ═══════════════════════════════════════════════════════════════
elif dashboard_type == "🏆 Leaderboard":
    st.markdown('<div class="main-title" style="font-size:36px;">🏆 LEADERBOARD</div>', unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown("### 🔧 Filters")
        lb_month = st.selectbox("Month", months, index=current_month_index, key="lb_month")
        lb_metric = st.radio("Rank By", ["Disbursed AMT", "Total_Revenue", "Transactions"])
    
    lb_df = df[df["Disb Month"] == lb_month]
    
    if lb_metric == "Transactions":
        lb_agg = lb_df.groupby("Manager").size().reset_index(name="Value")
    else:
        lb_agg = lb_df.groupby("Manager")[lb_metric].sum().reset_index()
        lb_agg.columns = ["Manager", "Value"]
    
    lb_agg = lb_agg.sort_values("Value", ascending=False).head(10).reset_index(drop=True)
    
    # PODIUM
    if len(lb_agg) >= 3:
        st.markdown('<div class="glass-box" style="text-align:center;"><h2 style="color:white;">🎖️ TOP 3</h2></div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        podium = [
            (col2, 0, "🥇", "Gold"),
            (col1, 1, "🥈", "Silver"),
            (col3, 2, "🥉", "Bronze")
        ]
        
        for col, idx, emoji, title in podium:
            if idx < len(lb_agg):
                row = lb_agg.iloc[idx]
                val_display = f"₹{row['Value']/100000:.1f}L" if lb_metric != "Transactions" else f"{int(row['Value'])}"
                
                col.markdown(f"""
                <div class="glass-box" style="text-align:center;">
                    <div style="font-size:48px;margin-bottom:10px;">{emoji}</div>
                    <h3 style="color:white;margin-bottom:10px;">{row['Manager']}</h3>
                    <p style="font-size:24px;font-weight:800;color:white;">{val_display}</p>
                    <p style="color:rgba(255,255,255,0.7);">{title}</p>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
    
    # FULL RANKINGS
    st.markdown('<div class="glass-box"><h3 style="color:white;">📊 Full Rankings</h3></div>', unsafe_allow_html=True)
    
    for idx, row in lb_agg.iterrows():
        rank = idx + 1
        val = row["Value"]
        val_display = f"₹{val/100000:.2f}L" if lb_metric != "Transactions" else f"{int(val)}"
        
        rank_emoji = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"][idx] if idx < 10 else f"#{rank}"
        
        st.markdown(f"""
        <div class="leader-box">
            <div class="rank-number">{rank_emoji}</div>
            <div style="flex:1;">
                <div class="leader-name">{row['Manager']}</div>
            </div>
            <div class="leader-value">{val_display}</div>
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# 🎯 TARGET TRACKER
# ═══════════════════════════════════════════════════════════════
elif dashboard_type == "🎯 Target Tracker":
    st.markdown('<div class="main-title" style="font-size:36px;">🎯 TARGET TRACKER</div>', unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown("### 🔧 Filters")
        tgt_month = st.selectbox("Month", months, index=current_month_index, key="tgt_month")
    
    tgt_df = df[df["Disb Month"] == tgt_month]
    mgr_actual = tgt_df.groupby("Manager")["Disbursed AMT"].sum().reset_index()
    mgr_actual.columns = ["Manager", "Actual"]
    
    for _, row in mgr_actual.iterrows():
        manager = row["Manager"]
        actual_l = row["Actual"] / 100000
        target_l = get_target_for_manager(manager, tgt_month, target_raw)
        
        if target_l == 0:
            target_l = 50
        
        achievement = (actual_l / target_l * 100)
        
        if achievement >= 100:
            status = "✅ Target Achieved"
            color = "rgba(16, 185, 129, 0.3)"
            border = "rgba(16, 185, 129, 0.6)"
        elif achievement >= 75:
            status = "🔵 On Track"
            color = "rgba(59, 130, 246, 0.3)"
            border = "rgba(59, 130, 246, 0.6)"
        elif achievement >= 50:
            status = "🟡 Needs Push"
            color = "rgba(245, 158, 11, 0.3)"
            border = "rgba(245, 158, 11, 0.6)"
        else:
            status = "🔴 Behind Target"
            color = "rgba(239, 68, 68, 0.3)"
            border = "rgba(239, 68, 68, 0.6)"
        
        st.markdown(f"""
        <div style="background:{color};border:2px solid {border};border-radius:15px;padding:20px;margin:15px 0;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:15px;">
                <div>
                    <h3 style="color:white;margin:0;">{manager}</h3>
                    <p style="color:rgba(255,255,255,0.8);margin:5px 0 0 0;">{status}</p>
                </div>
                <div style="text-align:right;">
                    <h2 style="color:white;margin:0;">{achievement:.1f}%</h2>
                    <p style="color:rgba(255,255,255,0.8);margin:5px 0 0 0;">₹{actual_l:.1f}L / ₹{target_l:.1f}L</p>
                </div>
            </div>
            <div class="progress-bar-container">
                <div class="progress-bar-fill" style="width:{min(achievement, 100):.1f}%;"></div>
                <div class="progress-text">{achievement:.1f}% Complete</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════════
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center;padding:20px;">
    <p style="color:white;font-size:14px;margin:0;">
        <strong>Prime PL Dashboard</strong> • MyMoneyMantra © 2025
    </p>
</div>
""", unsafe_allow_html=True)
