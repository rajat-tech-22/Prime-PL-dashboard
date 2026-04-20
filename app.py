import streamlit as st
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
from streamlit_autorefresh import st_autorefresh
import os
import time
from datetime import datetime, timedelta, timezone
from io import BytesIO

# ─────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────
st.set_page_config(
    page_title="Prime PL Dashboard",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)
st_autorefresh(interval=60 * 1000, key="refresh")

# ─────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%) !important;
}
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }

[data-testid="stSidebar"] .stRadio > label,
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stMultiSelect label,
[data-testid="stSidebar"] .stNumberInput label {
    color: #cbd5e1 !important;
    font-size: 12px !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-weight: 600 !important;
}

[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] *,
[data-testid="stSidebar"] .stSelectbox input,
[data-testid="stSidebar"] .stMultiSelect div[data-baseweb="select"] *,
[data-testid="stSidebar"] .stMultiSelect input,
[data-testid="stSidebar"] [data-baseweb="select"] [data-testid="stMarkdownContainer"] p,
[data-testid="stSidebar"] div[data-baseweb="select"] span,
[data-testid="stSidebar"] div[data-baseweb="select"] div {
    color: #000000 !important;
    font-weight: 500 !important;
}

[data-testid="stSidebar"] div[data-baseweb="select"] > div {
    background-color: #ffffff !important;
    border-radius: 8px !important;
    border: 1px solid #334155 !important;
}

[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label p,
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label span {
    color: #e2e8f0 !important;
    font-size: 14px !important;
}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover p {
    color: #ffffff !important;
}

[data-testid="stSidebar"] span[data-baseweb="tag"] {
    background-color: #e0e7ff !important;
}
[data-testid="stSidebar"] span[data-baseweb="tag"] span {
    color: #1e1b4b !important;
    font-weight: 600 !important;
}

[data-testid="stSidebar"] .streamlit-expanderHeader p {
    color: #f1f5f9 !important;
    font-weight: 600 !important;
}
[data-testid="stSidebar"] details {
    background: rgba(255,255,255,0.05) !important;
    border-radius: 10px !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    margin-bottom: 8px !important;
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #f8fafc !important; }

[data-testid="stSidebar"] .stButton > button {
    background: #ef4444 !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    width: 100%;
}
[data-testid="stSidebar"] .stButton > button:hover { background: #dc2626 !important; }

.stApp { background-color: #f8fafc; }

/* ── LOGIN PAGE ── */
[data-testid="stAppViewContainer"] > .main > .block-container {
    padding: 0 !important;
    max-width: 100% !important;
}
.login-bg {
    min-height: 100vh;
    background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 40%, #312e81 70%, #4c1d95 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 2rem 1rem;
    position: relative;
    overflow: hidden;
}
.login-card {
    background: white;
    border-radius: 24px;
    width: 100%;
    max-width: 440px;
    overflow: hidden;
    box-shadow: 0 24px 80px rgba(0,0,0,0.35);
    position: relative;
    z-index: 2;
}
.login-card-banner {
    background: linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #4c1d95 100%);
    padding: 2rem 2rem 1.5rem;
    position: relative;
    overflow: hidden;
}
.login-banner-brand {
    display: flex; align-items: center; gap: 10px;
    margin-bottom: 1.4rem;
}
.login-banner-logo {
    width: 38px; height: 38px;
    background: rgba(255,255,255,0.15);
    border: 1px solid rgba(255,255,255,0.2);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px;
}
.login-banner-name { font-size: 14px; font-weight: 600; color: #e0e7ff; }
.login-banner-title { font-size: 22px; font-weight: 700; color: #fff; line-height:1.3; margin-bottom: 6px; }
.login-banner-sub { font-size: 12px; color: #a5b4fc; margin-bottom: 1.2rem; }
.login-banner-stats {
    display: flex; gap: 10px;
}
.login-banner-stat {
    flex: 1;
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 10px;
    padding: 10px 12px;
}
.login-banner-stat-val { font-size: 17px; font-weight: 700; color: #fff; margin-bottom: 1px; }
.login-banner-stat-lbl { font-size: 10px; color: #a5b4fc; }
.login-form-area {
    padding: 1.8rem 2rem 1.5rem;
    background: white;
}
.login-form-heading { font-size: 18px; font-weight: 700; color: #0f172a; margin-bottom: 4px; }
.login-form-sub { font-size: 13px; color: #64748b; margin-bottom: 1.5rem; }
.login-info-row {
    display: flex; gap: 8px; flex-wrap: wrap;
    margin-top: 1rem; margin-bottom: 0.5rem;
}
.login-info-chip {
    display: flex; align-items: center; gap: 5px;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 20px;
    padding: 4px 10px;
    font-size: 11px; color: #64748b;
}
.login-info-dot { width: 6px; height: 6px; border-radius: 50%; }
.login-footer-txt {
    text-align: center;
    font-size: 11px; color: #94a3b8;
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid #f1f5f9;
}

/* ── DASHBOARD STYLES ── */
.metric-card {
    background: white;
    border-radius: 16px;
    padding: 20px 24px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    text-align: center;
    transition: transform 0.2s, box-shadow 0.2s;
    min-height: 110px;
    display: flex; flex-direction: column;
    justify-content: center; align-items: center;
}
.metric-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.10);
}
.metric-label {
    font-size: 11px; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.08em;
    color: #94a3b8; margin-bottom: 8px;
}
.metric-value { font-size: 26px; font-weight: 700; color: #0f172a; line-height: 1.1; }
.metric-icon { font-size: 20px; margin-bottom: 6px; }

.section-header {
    font-size: 18px; font-weight: 700; color: #0f172a;
    margin: 28px 0 16px 0;
    padding-left: 12px;
    border-left: 4px solid #6366f1;
}

.insight-strip {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
    border-radius: 12px; padding: 14px 20px;
    display: flex; justify-content: space-around;
    flex-wrap: wrap; gap: 10px;
    margin: 16px 0; color: white;
}
.insight-item { text-align: center; font-size: 13px; }
.insight-item b {
    display: block; font-size: 11px; opacity: 0.8;
    text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 2px;
}

.target-card {
    background: white; border-radius: 16px;
    padding: 20px; border: 1px solid #e2e8f0;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    margin-bottom: 16px;
}
.progress-bar-bg {
    background: #f1f5f9; border-radius: 999px;
    height: 12px; overflow: hidden; margin: 10px 0 6px 0;
}
.progress-bar-fill { height: 12px; border-radius: 999px; transition: width 0.5s ease; }

.stDataFrame { border-radius: 12px !important; overflow: hidden; }
thead tr th { background: #f8fafc !important; font-weight: 600 !important; }

.streamlit-expanderHeader {
    background: #f1f5f9 !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
}

h1 { color: #0f172a !important; font-weight: 700 !important; }
h2 { color: #1e293b !important; font-weight: 600 !important; }
h3 { color: #334155 !important; font-weight: 600 !important; }

.stDownloadButton > button {
    background: #6366f1 !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}
.stDownloadButton > button:hover { background: #4f46e5 !important; }

/* Primary button override for login */
[data-testid="stMain"] .stButton > button[kind="primary"] {
    background: #6366f1 !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 15px !important;
    padding: 0.6rem 1rem !important;
}
[data-testid="stMain"] .stButton > button[kind="primary"]:hover {
    background: #4f46e5 !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────
USERNAME = os.getenv("APP_USERNAME", "Mymoneymantra")
PASSWORD = os.getenv("APP_PASSWORD", "Prime110")
MAX_ATTEMPTS = 4
LOCK_TIME = 43200

for key, val in [("login", False), ("attempts", 0), ("lock_time", None)]:
    if key not in st.session_state:
        st.session_state[key] = val

# ─────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────
def format_inr(n):
    if not n or n == 0:
        return "₹0"
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

COLORS = ["#6366f1","#f59e0b","#10b981","#ef4444","#3b82f6","#8b5cf6","#ec4899","#14b8a6"]
GOLD = "#f59e0b"

def get_colors(index_list, top_val):
    return [GOLD if v == top_val else COLORS[i % len(COLORS)] for i, v in enumerate(index_list)]

def calc_metrics(f):
    td = f["Disbursed AMT"].sum()
    tr = f["Total_Revenue"].sum()
    ap = (tr / td * 100) if td else 0
    tc = len(f)
    ad = td / tc if tc else 0
    tb = f.groupby("Bank")["Disbursed AMT"].sum().idxmax() if not f.empty else "N/A"
    tcamp = f.groupby("Campaign")["Disbursed AMT"].sum().idxmax() if not f.empty else "N/A"
    tcall = f.groupby("Caller")["Disbursed AMT"].sum().idxmax() if not f.empty else "N/A"
    return td, tr, ap, tc, ad, tb, tcamp, tcall

def metric_card(label, value, icon="", color="#6366f1"):
    return f"""
    <div class="metric-card">
        <div class="metric-icon">{icon}</div>
        <div class="metric-label">{label}</div>
        <div class="metric-value" style="color:{color}">{value}</div>
    </div>"""

def section_header(title):
    st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)

def insight_strip(items: dict):
    inner = "".join([
        f'<div class="insight-item"><b>{k}</b>{v}</div>'
        for k, v in items.items()
    ])
    st.markdown(f'<div class="insight-strip">{inner}</div>', unsafe_allow_html=True)

def styled_bar(df_group, col, x_col, y_col, title, top_val=None, height=400):
    colors = get_colors(df_group[x_col], top_val or df_group.loc[df_group[y_col].idxmax(), x_col])
    fig = go.Figure(go.Bar(
        x=df_group[x_col],
        y=df_group[y_col] / 100000,
        text=[f"<b>{v/100000:.2f}L</b>" for v in df_group[y_col]],
        textposition="outside",
        marker_color=colors,
        marker_line_width=0,
    ))
    fig.update_layout(
        title=dict(text=title, font=dict(size=15, color="#0f172a")),
        yaxis_title="Amount (Lakhs)",
        template="plotly_white",
        height=height,
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="Inter, sans-serif", size=12),
        margin=dict(t=50, b=60, l=40, r=20),
        xaxis=dict(tickangle=-30),
    )
    fig.update_traces(cliponaxis=False)
    return fig

def generate_pdf_bytes(df_display: pd.DataFrame, title: str) -> bytes:
    try:
        from fpdf import FPDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 12, title, ln=True, align="C")
        pdf.set_font("Helvetica", "", 8)
        pdf.ln(4)
        cols = list(df_display.columns)
        col_w = min(190 // len(cols), 40)
        pdf.set_fill_color(99, 102, 241)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 8)
        for c in cols:
            pdf.cell(col_w, 8, str(c)[:18], border=1, fill=True)
        pdf.ln()
        pdf.set_text_color(15, 23, 42)
        pdf.set_font("Helvetica", "", 7)
        for _, row in df_display.iterrows():
            for c in cols:
                pdf.cell(col_w, 7, str(row[c])[:18], border=1)
            pdf.ln()
        return pdf.output()
    except Exception:
        return b""

# ─────────────────────────────────────────
# ✅ UPGRADED: CURRENT MONTH HELPER
# Handles all possible month formats robustly
# ─────────────────────────────────────────
def get_current_month_index(months_list):
    if not months_list:
        return 0
    ist = timezone(timedelta(hours=5, minutes=30))
    now = datetime.now(ist)

    # Generate all possible format candidates for current month
    candidates = set([
        now.strftime("%B %Y"),    # "April 2025"
        now.strftime("%b %Y"),    # "Apr 2025"
        now.strftime("%b-%y"),    # "Apr-25"
        now.strftime("%B-%Y"),    # "April-2025"
        now.strftime("%m-%Y"),    # "04-2025"
        now.strftime("%Y-%m"),    # "2025-04"
        now.strftime("%b-%Y"),    # "Apr-2025"
        now.strftime("%B %y"),    # "April 25"
        now.strftime("%m/%Y"),    # "04/2025"
        now.strftime("%b/%Y"),    # "Apr/2025"
        now.strftime("%B/%Y"),    # "April/2025"
        now.strftime("%Y/%m"),    # "2025/04"
        now.strftime("%d-%b-%Y"), # "01-Apr-2025" edge case
        now.strftime("%b %Y").upper(),   # "APR 2025"
        now.strftime("%B %Y").upper(),   # "APRIL 2025"
        now.strftime("%b %Y").lower(),   # "apr 2025"
    ])

    # Try exact match first (case-insensitive strip)
    for i, m in enumerate(months_list):
        m_str = str(m).strip()
        if m_str in candidates or m_str.lower() in {c.lower() for c in candidates}:
            return i

    # Fallback: try partial match on month number + year
    month_num = now.strftime("%m")
    year_4    = now.strftime("%Y")
    year_2    = now.strftime("%y")

    for i, m in enumerate(months_list):
        m_str = str(m).strip()
        # Check if both month number/abbr AND year appear in string
        has_year  = year_4 in m_str or year_2 in m_str
        has_month = (
            month_num in m_str
            or now.strftime("%b").lower() in m_str.lower()
            or now.strftime("%B").lower() in m_str.lower()
        )
        if has_year and has_month:
            return i

    # Last resort: return last month in list
    return len(months_list) - 1


# ─────────────────────────────────────────
# IST TIME
# ─────────────────────────────────────────
ist = timezone(timedelta(hours=5, minutes=30))
now_ist = datetime.now(ist)

# ─────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────
@st.cache_data(ttl=60)
def load_data():
    url = "https://docs.google.com/spreadsheets/d/1I1ql5NwFafbWXYkVOvv0yvMM9GKnJ5954R4zif2owGI/export?format=csv"
    df = pd.read_csv(url)
    df.replace("null", None, inplace=True)
    if "DISB DATE" in df.columns:
        df["DISB DATE"] = pd.to_datetime(df["DISB DATE"], errors="coerce")
    return df

@st.cache_data(ttl=60)
def load_campaign_data():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vROJC-HN52HXZboNKd2rNzYbTHzXtAsewd_hbht7MnQMvpNmVfE9H4fjQA0S06sFZGwPDCErXIPEhsy/pub?output=csv"
    df2 = pd.read_csv(url)
    df2.columns = df2.columns.str.strip()
    return df2

@st.cache_data(ttl=120)
def load_targets():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTplHDYVsgbTHNJsFFqLBzbRc4Gj8RYlrjRs4H8NxRy2V7iAFl0-teSToWaSHz5BReD5rSsgVv1sjMs/pub?output=csv"
    try:
        tdf = pd.read_csv(url)
        tdf.columns = tdf.columns.str.strip()
        return tdf, None
    except Exception as e:
        return pd.DataFrame(), str(e)

# ─────────────────────────────────────────
# TARGET FETCH FUNCTION
# ─────────────────────────────────────────
def get_target_for_manager(mgr_name, month_name, tdf):
    if tdf is None or tdf.empty:
        return 0.0
    cols_lower = {c.lower().strip(): c for c in tdf.columns}
    mgr_col = next((cols_lower[k] for k in ["manager","name","manager name"] if k in cols_lower), None)
    mon_col = next((cols_lower[k] for k in ["month","disb month","month name"] if k in cols_lower), None)
    tgt_col = next((cols_lower[k] for k in [
        "target","target (l)","target_l","target (lakhs)","amount","target(l)"
    ] if k in cols_lower), None)
    if not mgr_col or not tgt_col:
        return 0.0
    mgr_rows = tdf[tdf[mgr_col].astype(str).str.strip().str.lower() == mgr_name.strip().lower()]
    if mgr_rows.empty:
        return 0.0
    if mon_col:
        mon_rows = mgr_rows[
            mgr_rows[mon_col].astype(str).str.strip().str.lower() == month_name.strip().lower()
        ]
        if not mon_rows.empty:
            try:
                return float(str(mon_rows.iloc[0][tgt_col]).replace(",","").replace("₹","").strip())
            except:
                pass
    try:
        return float(str(mgr_rows.iloc[0][tgt_col]).replace(",","").replace("₹","").strip())
    except:
        return 0.0


# ─────────────────────────────────────────
# LOGIN PAGE
# ─────────────────────────────────────────
if not st.session_state.login:

    # Lock check
    if st.session_state.lock_time:
        elapsed = time.time() - st.session_state.lock_time
        remaining = LOCK_TIME - elapsed
        if remaining > 0:
            h_r = int(remaining // 3600)
            m_r = int((remaining % 3600) // 60)
            st.error(f"🔒 Account locked. Try again in {h_r}h {m_r}m.")
            st.stop()
        else:
            st.session_state.attempts = 0
            st.session_state.lock_time = None

    # Hide sidebar and header
    st.markdown(
        "<style>"
        "[data-testid='stSidebar']{display:none!important;}"
        "[data-testid='stHeader']{display:none!important;}"
        "[data-testid='stToolbar']{display:none!important;}"
        "footer{display:none!important;}"
        ".stApp{background:linear-gradient(135deg,#0f172a 0%,#1e1b4b 50%,#312e81 100%)!important;}"
        "[data-testid='stAppViewContainer']>.main>.block-container{"
        "padding:4rem 1rem 2rem!important;max-width:420px!important;margin:0 auto!important;}"
        ".stTextInput label{color:#a5b4fc!important;font-size:12px!important;"
        "font-weight:600!important;text-transform:uppercase!important;letter-spacing:0.06em!important;}"
        ".stTextInput input{background:rgba(255,255,255,0.07)!important;"
        "border:1.5px solid rgba(255,255,255,0.15)!important;border-radius:10px!important;"
        "color:#f1f5f9!important;font-size:14px!important;padding:12px 14px!important;}"
        ".stTextInput input:focus{border-color:#6366f1!important;"
        "box-shadow:0 0 0 3px rgba(99,102,241,0.2)!important;}"
        ".stTextInput input::placeholder{color:rgba(255,255,255,0.25)!important;}"
        ".stButton>button{background:linear-gradient(135deg,#6366f1,#8b5cf6)!important;"
        "color:white!important;border:none!important;border-radius:12px!important;"
        "font-weight:700!important;font-size:15px!important;"
        "box-shadow:0 4px 20px rgba(99,102,241,0.4)!important;}"
        "</style>",
        unsafe_allow_html=True
    )

    # Logo + title
    st.markdown(
        "<div style='text-align:center;margin-bottom:2rem;'>"
        "<div style='width:56px;height:56px;background:linear-gradient(135deg,#6366f1,#8b5cf6);"
        "border-radius:16px;display:flex;align-items:center;justify-content:center;"
        "margin:0 auto 14px;font-size:26px;box-shadow:0 8px 24px rgba(99,102,241,0.4);'>&#x1F4BC;</div>"
        "<div style='font-size:22px;font-weight:700;color:#fff;margin-bottom:4px;'>Prime PL Dashboard</div>"
        "<div style='font-size:13px;color:#7c8cba;'>MyMoneyMantra &nbsp;&middot;&nbsp; Real-time Analytics</div>"
        "</div>",
        unsafe_allow_html=True
    )

    # Login card
    st.markdown(
        "<div style='background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);"
        "border-radius:20px;padding:28px 28px 20px;'>"
        "<div style='font-size:18px;font-weight:700;color:#fff;margin-bottom:4px;'>Welcome back &#x1F44B;</div>"
        "<div style='font-size:13px;color:#64748b;margin-bottom:20px;'>Sign in to continue</div>"
        "</div>",
        unsafe_allow_html=True
    )

    u = st.text_input("Username", placeholder="Enter your username", key="login_user")
    p = st.text_input("Password", type="password", placeholder="Enter your password", key="login_pass")

    if st.button("Sign in  →", use_container_width=True, key="login_btn"):
        if u == USERNAME and p == PASSWORD:
            st.session_state.login = True
            st.session_state.attempts = 0
            st.rerun()
        else:
            st.session_state.attempts += 1
            left_att = MAX_ATTEMPTS - st.session_state.attempts
            if left_att <= 0:
                st.session_state.lock_time = time.time()
                st.error("🔒 Too many attempts. Account locked for 12 hours.")
            else:
                st.warning(f"❌ Invalid credentials — {left_att} attempt(s) remaining.")

    attempts_left = MAX_ATTEMPTS - st.session_state.attempts
    dot_color = "#10b981" if attempts_left >= 3 else "#f59e0b" if attempts_left == 2 else "#ef4444"

    st.markdown(
        "<div style='text-align:center;margin-top:16px;'>"
        "<div style='display:flex;justify-content:center;gap:8px;flex-wrap:wrap;margin-bottom:12px;'>"
        "<span style='background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.1);"
        "border-radius:20px;padding:3px 10px;font-size:11px;color:#94a3b8;display:inline-flex;align-items:center;gap:5px;'>"
        "<span style='width:6px;height:6px;border-radius:50%;background:" + dot_color + ";display:inline-block;'></span>"
        + str(attempts_left) + "/" + str(MAX_ATTEMPTS) + " attempts left</span>"
        "<span style='background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.1);"
        "border-radius:20px;padding:3px 10px;font-size:11px;color:#94a3b8;'>&#x1F512; 12h lockout</span>"
        "</div>"
        "<div style='font-size:11px;color:#334155;'>"
        "Prime PL &nbsp;&middot;&nbsp; " + now_ist.strftime("%d %b %Y  %I:%M %p") + " IST"
        "</div></div>",
        unsafe_allow_html=True
    )

    st.stop()


# ─────────────────────────────────────────
# LOAD DATA (after login)


# ─────────────────────────────────────────
df = load_data()
campaign_df = load_campaign_data()
target_raw, target_err = load_targets()

# ✅ months + current_month_index calculated ONCE here, used everywhere
months = sorted(df["Disb Month"].dropna().unique())
verticals = ["All"] + sorted(df["Vertical"].dropna().unique())
managers = sorted(df["Manager"].dropna().unique())
current_month_index = get_current_month_index(months)

# ─────────────────────────────────────────
# SIDEBAR NAVIGATION
# ─────────────────────────────────────────
with st.sidebar:
    st.markdown("## 💼 Prime PL")
    st.markdown("---")
    dashboard_type = st.radio(
        "Navigation",
        ["🏠 Overview", "👤 Single Manager", "⚖️ Comparison",
         "📊 Campaign Performance", "🎯 Target Tracker", "📅 Team vs Month"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    if st.button("🚪 Logout"):
        st.session_state.login = False
        st.rerun()

# ─────────────────────────────────────────
# GREETING
# ─────────────────────────────────────────
ist_tz = timezone(timedelta(hours=5, minutes=30))
now_ist2 = datetime.now(ist_tz)
hour = now_ist2.hour
greet = ("Good Morning 🌅" if 5 <= hour < 12
         else "Good Afternoon ☀️" if hour < 16
         else "Good Evening 🌇" if hour < 20
         else "Good Night 🌙")

st.markdown(f"""
<div style="background: linear-gradient(135deg, #6366f1, #8b5cf6, #ec4899);
            border-radius: 16px; padding: 20px 28px; margin-bottom: 24px; color: white;">
    <div style="font-size: 22px; font-weight: 700;">{greet}, Welcome to Prime PL!</div>
    <div style="font-size: 13px; opacity: 0.85; margin-top: 4px;">
        {now_ist2.strftime("%A, %d %B %Y  •  %I:%M %p")} IST
    </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════
# 🏠 OVERVIEW
# ══════════════════════════════════════════
if dashboard_type == "🏠 Overview":
    st.title("Overview — All Managers")

    with st.sidebar.expander("🔧 Filters", expanded=True):
        # ✅ index=current_month_index — current month auto-selected
        selected_month = st.selectbox("Month", months, index=current_month_index)
        selected_vertical = st.selectbox("Vertical", verticals)

    filtered_df = df.copy()
    if selected_vertical != "All":
        filtered_df = filtered_df[filtered_df["Vertical"] == selected_vertical]
    filtered_df = filtered_df[filtered_df["Disb Month"] == selected_month]

    camps = sorted(filtered_df["Campaign"].dropna().unique())
    with st.sidebar.expander("📌 Campaigns", expanded=False):
        sel_camps = st.multiselect("Campaigns", camps, default=camps)
    if sel_camps:
        filtered_df = filtered_df[filtered_df["Campaign"].isin(sel_camps)]

    if filtered_df.empty:
        st.warning("No data for selected filters.")
    else:
        agg = filtered_df.groupby(["Vertical", "Manager"]).agg(
            Total_Disbursed=("Disbursed AMT", "sum"),
            Total_Revenue=("Total_Revenue", "sum"),
            Transactions=("Manager", "count"),
        ).reset_index()

        td = agg["Total_Disbursed"].sum()
        tr = agg["Total_Revenue"].sum()
        tt = int(agg["Transactions"].sum())
        ap = (tr / td * 100) if td else 0

        cards = [
            ("Total Disbursed", format_inr(td), "💰", "#6366f1"),
            ("Total Revenue", format_inr(tr), "📈", "#10b981"),
            ("Avg Payout %", f"{ap:.2f}%", "📊", "#f59e0b"),
            ("Transactions", f"{tt:,}", "🔁", "#ef4444"),
        ]
        cols = st.columns(4)
        for col, (lbl, val, icon, clr) in zip(cols, cards):
            col.markdown(metric_card(lbl, val, icon, clr), unsafe_allow_html=True)

        top_bank = filtered_df.groupby("Bank")["Disbursed AMT"].sum().idxmax()
        top_campaign = filtered_df.groupby("Campaign")["Disbursed AMT"].sum().idxmax()
        top_caller = filtered_df.groupby("Caller")["Disbursed AMT"].sum().idxmax()

        insight_strip({
            "🏦 Top Bank": top_bank,
            "🚀 Top Campaign": top_campaign,
            "🏆 Top Caller": top_caller,
            "📅 Month": selected_month,
        })

        section_header("Manager Summary Table")
        disp = agg.copy()
        disp["Total_Disbursed"] = disp["Total_Disbursed"].apply(format_inr)
        disp["Total_Revenue"] = disp["Total_Revenue"].apply(format_inr)
        st.dataframe(disp, use_container_width=True, height=300)

        pdf_bytes = generate_pdf_bytes(disp, f"Overview - {selected_month}")
        c1, c2 = st.columns(2)
        with c1:
            st.download_button("⬇️ Download CSV", disp.to_csv(index=False), "overview.csv", "text/csv")
        with c2:
            if pdf_bytes:
                st.download_button("📄 Export PDF", pdf_bytes, "overview.pdf", "application/pdf")

        section_header("Campaign-wise Disbursed")
        cs = filtered_df.groupby("Campaign")["Disbursed AMT"].sum().reset_index()
        cs.columns = ["Campaign", "Disbursed AMT"]
        st.plotly_chart(styled_bar(cs, "Campaign", "Campaign", "Disbursed AMT",
                                   "Campaign-wise Disbursed Amount"), use_container_width=True)

        section_header("Bank-wise Disbursed")
        bs = filtered_df.groupby("Bank")["Disbursed AMT"].sum().reset_index()
        bs.columns = ["Bank", "Disbursed AMT"]
        st.plotly_chart(styled_bar(bs, "Bank", "Bank", "Disbursed AMT",
                                   "Bank-wise Disbursed Amount"), use_container_width=True)


# ══════════════════════════════════════════
# 👤 SINGLE MANAGER
# ══════════════════════════════════════════
elif dashboard_type == "👤 Single Manager":
    with st.sidebar.expander("🔧 Filters", expanded=True):
        # ✅ index=current_month_index
        sel_month_sm = st.selectbox("Month", months, index=current_month_index, key="sm_month")
        mgr_list = sorted(df[df["Disb Month"] == sel_month_sm]["Manager"].dropna().unique())
        sel_mgr = st.selectbox("Manager", mgr_list, key="sm_mgr")
        sel_vert_sm = st.selectbox("Vertical", verticals, key="sm_vert")

    f_sm = df[(df["Disb Month"] == sel_month_sm) & (df["Manager"] == sel_mgr)]
    if sel_vert_sm != "All":
        f_sm = f_sm[f_sm["Vertical"] == sel_vert_sm]

    camps_sm = sorted(f_sm["Campaign"].dropna().unique())
    with st.sidebar.expander("📌 Campaigns", expanded=False):
        sel_camps_sm = st.multiselect("Campaigns", camps_sm, default=camps_sm, key="sm_camps")
    if sel_camps_sm:
        f_sm = f_sm[f_sm["Campaign"].isin(sel_camps_sm)]

    st.title(f"👤 {sel_mgr} — {sel_month_sm}")

    if f_sm.empty:
        st.warning("No data for selected filters.")
    else:
        td, tr, ap, tc, ad, tb, tcamp, tcall = calc_metrics(f_sm)

        cards = [
            ("Total Disbursed", format_inr(td), "💰", "#6366f1"),
            ("Total Revenue", format_inr(tr), "📈", "#10b981"),
            ("Avg Payout %", f"{ap:.2f}%", "📊", "#f59e0b"),
            ("Transactions", f"{tc:,}", "🔁", "#ef4444"),
        ]
        cols = st.columns(4)
        for col, (lbl, val, icon, clr) in zip(cols, cards):
            col.markdown(metric_card(lbl, val, icon, clr), unsafe_allow_html=True)

        insight_strip({
            "🏦 Top Bank": tb,
            "🚀 Top Campaign": tcamp,
            "🏆 Top Caller": tcall,
            "💵 Avg Ticket": f"₹{ad/100000:.2f}L",
        })

        section_header("Campaign-wise Disbursed")
        cs = f_sm.groupby("Campaign")["Disbursed AMT"].sum().reset_index()
        cs.columns = ["Campaign", "Disbursed AMT"]
        st.plotly_chart(styled_bar(cs, "Campaign", "Campaign", "Disbursed AMT",
                                   "Campaign-wise"), use_container_width=True)

        section_header("Bank-wise Disbursed")
        bs = f_sm.groupby("Bank")["Disbursed AMT"].sum().reset_index()
        bs.columns = ["Bank", "Disbursed AMT"]
        st.plotly_chart(styled_bar(bs, "Bank", "Bank", "Disbursed AMT",
                                   "Bank-wise"), use_container_width=True)

        section_header("Caller-wise Disbursed")
        cls = f_sm.groupby("Caller")["Disbursed AMT"].sum().reset_index()
        cls.columns = ["Caller", "Disbursed AMT"]
        st.plotly_chart(styled_bar(cls, "Caller", "Caller", "Disbursed AMT",
                                   "Caller-wise"), use_container_width=True)

        section_header("Monthly Trend")
        trend = df[df["Manager"] == sel_mgr].groupby("Disb Month")["Disbursed AMT"].sum().reset_index()
        fig_t = go.Figure(go.Scatter(
            x=trend["Disb Month"], y=trend["Disbursed AMT"]/100000,
            mode="lines+markers", line=dict(width=2.5, color="#6366f1"),
            marker=dict(size=8)
        ))
        fig_t.update_layout(template="plotly_white", height=380, yaxis_title="Disbursed (L)",
                             font=dict(family="Inter"), plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig_t, use_container_width=True)

        section_header("Raw Data")
        dd = f_sm.dropna(how="all").copy()
        st.dataframe(dd, use_container_width=True, height=300)
        st.download_button("⬇️ Download CSV", dd.to_csv(index=False),
                           f"{sel_mgr}_{sel_month_sm}.csv", "text/csv")


# ══════════════════════════════════════════
# ⚖️ COMPARISON
# ══════════════════════════════════════════
elif dashboard_type == "⚖️ Comparison":
    with st.sidebar.expander("🔧 First Selection", expanded=True):
        # ✅ index=current_month_index for both
        m1 = st.selectbox("Month", months, index=current_month_index, key="m1")
        mgr1 = st.selectbox("Manager",
                             sorted(df[df["Disb Month"] == m1]["Manager"].dropna().unique()), key="mgr1")
    f1 = df[(df["Disb Month"] == m1) & (df["Manager"] == mgr1)]

    with st.sidebar.expander("🔧 Second Selection", expanded=True):
        m2 = st.selectbox("Month", months, index=current_month_index, key="m2")
        mgr2 = st.selectbox("Manager",
                             sorted(df[df["Disb Month"] == m2]["Manager"].dropna().unique()), key="mgr2")
    f2 = df[(df["Disb Month"] == m2) & (df["Manager"] == mgr2)]

    with st.sidebar.expander("📌 Campaigns — 1", expanded=False):
        c1_list = sorted(f1["Campaign"].dropna().unique())
        sc1 = st.multiselect("Campaigns", c1_list, default=c1_list, key="c1")
    with st.sidebar.expander("📌 Campaigns — 2", expanded=False):
        c2_list = sorted(f2["Campaign"].dropna().unique())
        sc2 = st.multiselect("Campaigns", c2_list, default=c2_list, key="c2")

    if sc1: f1 = f1[f1["Campaign"].isin(sc1)]
    if sc2: f2 = f2[f2["Campaign"].isin(sc2)]

    lbl1 = f"{mgr1} ({m1})"
    lbl2 = f"{mgr2} ({m2})"
    st.title("⚖️ Comparison")

    if f1.empty or f2.empty:
        st.warning("No data for one or both selections.")
        st.stop()

    d1, r1, p1, t1, a1, tb1, tc1, tcall1 = calc_metrics(f1)
    d2, r2, p2, t2, a2, tb2, tc2, tcall2 = calc_metrics(f2)
    winner = lbl1 if d1 > d2 else lbl2

    st.success(f"🏆 Winner: **{winner}** with {format_inr(max(d1, d2))}")

    col1, col2 = st.columns(2)
    cards_meta = [
        ("Total Disbursed","#6366f1"),("Total Revenue","#10b981"),
        ("Avg Payout %","#f59e0b"),("Transactions","#ef4444")
    ]
    vals1 = [format_inr(d1), format_inr(r1), f"{p1:.2f}%", f"{t1:,}"]
    vals2 = [format_inr(d2), format_inr(r2), f"{p2:.2f}%", f"{t2:,}"]
    icons = ["💰","📈","📊","🔁"]

    with col1:
        st.subheader(lbl1)
        for (lbl, clr), val, ico in zip(cards_meta, vals1, icons):
            st.markdown(metric_card(lbl, val, ico, clr), unsafe_allow_html=True)
    with col2:
        st.subheader(lbl2)
        for (lbl, clr), val, ico in zip(cards_meta, vals2, icons):
            st.markdown(metric_card(lbl, val, ico, clr), unsafe_allow_html=True)

    insight_strip({
        f"{lbl1} Bank": tb1, f"{lbl1} Campaign": tc1,
        f"{lbl2} Bank": tb2, f"{lbl2} Campaign": tc2
    })

    section_header("Head-to-Head Comparison")
    comp = pd.DataFrame({
        "Metric": ["Disbursed (L)", "Revenue (L)", "Transactions"],
        lbl1: [d1/100000, r1/100000, t1],
        lbl2: [d2/100000, r2/100000, t2],
    })
    fig_c = go.Figure()
    for lbl, vals, clr in [(lbl1, comp[lbl1], "#6366f1"), (lbl2, comp[lbl2], "#ef4444")]:
        fig_c.add_trace(go.Bar(name=lbl, x=comp["Metric"], y=vals,
                               text=[f"<b>{v:.2f}</b>" for v in vals],
                               textposition="outside", marker_color=clr))
    fig_c.update_layout(barmode="group", template="plotly_white", height=420,
                        font=dict(family="Inter"), plot_bgcolor="white")
    st.plotly_chart(fig_c, use_container_width=True)

    growth = ((d1 - d2) / d2 * 100) if d2 else 0
    st.info(f"📈 {lbl1} is **{abs(growth):.2f}%** {'higher' if growth >= 0 else 'lower'} than {lbl2}")

    for title, col_name in [("Bank","Bank"),("Caller","Caller"),("Campaign","Campaign")]:
        section_header(f"{title}-wise Comparison")
        fig = go.Figure()
        for f_x, lbl, clr in [(f1, lbl1, "#6366f1"), (f2, lbl2, "#ef4444")]:
            s = f_x.groupby(col_name)["Disbursed AMT"].sum()
            fig.add_trace(go.Bar(x=s.index, y=s.values/100000,
                                 text=[f"<b>{v/100000:.2f}L</b>" for v in s.values],
                                 textposition="auto", name=lbl, marker_color=clr))
        fig.update_layout(barmode="group", template="plotly_white", xaxis_tickangle=-30,
                          height=400, font=dict(family="Inter"), plot_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)

    section_header("Trend Line Comparison")
    fig_tl = go.Figure()
    for mgr, lbl, clr in [(mgr1, lbl1, "#6366f1"), (mgr2, lbl2, "#ef4444")]:
        t_data = df[df["Manager"] == mgr].groupby("Disb Month")["Disbursed AMT"].sum().reset_index()
        fig_tl.add_trace(go.Scatter(x=t_data["Disb Month"], y=t_data["Disbursed AMT"]/100000,
                                    mode="lines+markers", name=lbl,
                                    line=dict(width=2.5, color=clr), marker=dict(size=7)))
    fig_tl.update_layout(template="plotly_white", height=400, yaxis_title="Disbursed (L)",
                          hovermode="x unified", font=dict(family="Inter"),
                          plot_bgcolor="white", paper_bgcolor="white")
    st.plotly_chart(fig_tl, use_container_width=True)

    for label_x, f_x, fname in [
        (f"Data — {lbl1}", f1, "mgr1.csv"),
        (f"Data — {lbl2}", f2, "mgr2.csv")
    ]:
        section_header(label_x)
        dd = f_x.dropna(how="all").copy()
        for c in ["Disbursed AMT","Total_Revenue","AVG_Payout"]:
            if c in dd.columns:
                dd[c] = dd[c].round(2)
        st.dataframe(dd.style.set_properties(**{"text-align": "center"}),
                     use_container_width=True, height=280)
        st.download_button(f"⬇️ {fname}", dd.to_csv(index=False), fname, "text/csv")


# ══════════════════════════════════════════
# 📊 CAMPAIGN PERFORMANCE
# ══════════════════════════════════════════
elif dashboard_type == "📊 Campaign Performance":
    with st.sidebar.expander("🔧 Filters", expanded=True):
        # ✅ index=current_month_index — uses global months list
        sel_month = st.selectbox("Month", months, index=current_month_index)
        temp_df = df[df["Disb Month"] == sel_month]
        camp_list = sorted(temp_df["Campaign"].dropna().unique())
        c1, c2 = st.columns(2)
        if c1.button("All"):  st.session_state.camp_sel = camp_list
        if c2.button("Clear"): st.session_state.camp_sel = []
        if "camp_sel" not in st.session_state: st.session_state.camp_sel = camp_list
        sel_camps = st.multiselect("Campaigns", camp_list,
                                   default=st.session_state.camp_sel)

    camp_f = df[df["Disb Month"] == sel_month]
    if sel_camps: camp_f = camp_f[camp_f["Campaign"].isin(sel_camps)]

    st.title("Campaign Performance")

    if camp_f.empty:
        st.warning("No data.")
        st.stop()

    cp = camp_f.groupby("Campaign")["Disbursed AMT"].sum()
    top_c = cp.idxmax()
    st.success(f"🏆 Top Campaign: **{top_c}** — {format_inr(cp.max())}")

    td = camp_f["Disbursed AMT"].sum()
    tr = camp_f["Total_Revenue"].sum()
    ap = (tr / td * 100) if td else 0
    top_mgr = camp_f.groupby("Manager")["Disbursed AMT"].sum().idxmax()

    cards_row = [
        ("Total Disbursed", format_inr(td), "💰", "#6366f1"),
        ("Total Revenue", format_inr(tr), "📈", "#10b981"),
        ("Avg Payout %", f"{ap:.2f}%", "📊", "#f59e0b"),
        ("Best Manager", top_mgr, "🏆", "#8b5cf6"),
    ]
    cols = st.columns(4)
    for col, (lbl, val, ico, clr) in zip(cols, cards_row):
        col.markdown(metric_card(lbl, val, ico, clr), unsafe_allow_html=True)

    section_header("Campaign-wise Disbursed")
    cp_df = cp.reset_index()
    cp_df.columns = ["Campaign", "Disbursed AMT"]
    st.plotly_chart(styled_bar(cp_df, "Campaign", "Campaign", "Disbursed AMT",
                               "Campaign Performance"), use_container_width=True)

    section_header("Manager Performance Table")
    mgr_agg = camp_f.groupby("Manager").agg(
        Total_Disbursed=("Disbursed AMT","sum"),
        Total_Revenue=("Total_Revenue","sum"),
        Transactions=("Manager","count"),
    ).reset_index()
    mgr_agg["Avg_Payout%"] = (mgr_agg["Total_Revenue"] / mgr_agg["Total_Disbursed"] * 100).round(2)
    mgr_disp = mgr_agg.copy()
    mgr_disp["Total_Disbursed"] = mgr_disp["Total_Disbursed"].apply(format_inr)
    mgr_disp["Total_Revenue"]   = mgr_disp["Total_Revenue"].apply(format_inr)
    st.dataframe(mgr_disp, use_container_width=True, height=320)

    pdf_bytes = generate_pdf_bytes(mgr_disp, f"Campaign Performance — {sel_month}")
    c1, c2 = st.columns(2)
    with c1:
        st.download_button("⬇️ Download CSV", mgr_disp.to_csv(index=False),
                           "campaign_perf.csv", "text/csv")
    with c2:
        if pdf_bytes:
            st.download_button("📄 Export PDF", pdf_bytes, "campaign_perf.pdf", "application/pdf")

    section_header("Best Manager per Campaign")
    bm = camp_f.groupby(["Campaign","Manager"])["Disbursed AMT"].sum().reset_index()
    bm = bm.loc[bm.groupby("Campaign")["Disbursed AMT"].idxmax()]
    bm["Disbursed AMT"] = bm["Disbursed AMT"].apply(format_inr)
    st.dataframe(bm, use_container_width=True, height=280)

    section_header("Underperforming Campaigns")
    avg_p = cp.mean()
    under = cp[cp < avg_p].reset_index()
    under.columns = ["Campaign","Disbursed AMT"]
    if under.empty:
        st.success("✅ All campaigns above average!")
    else:
        under["Disbursed AMT"] = under["Disbursed AMT"].apply(format_inr)
        st.warning(f"{len(under)} campaign(s) below average ({format_inr(avg_p)})")
        st.dataframe(under, use_container_width=True)

    section_header("Bank-wise Disbursed")
    bk = camp_f.groupby("Bank")["Disbursed AMT"].sum().reset_index()
    bk.columns = ["Bank","Disbursed AMT"]
    st.plotly_chart(styled_bar(bk,"Bank","Bank","Disbursed AMT",
                               "Bank-wise Performance"), use_container_width=True)

    if months.index(sel_month) > 0:
        prev = months[months.index(sel_month) - 1]
        prev_t = df[df["Disb Month"] == prev]["Disbursed AMT"].sum()
        growth = ((td - prev_t) / prev_t * 100) if prev_t else 0
        section_header("MoM Growth")
        g_col = "#10b981" if growth >= 0 else "#ef4444"
        st.markdown(f"""
        <div style="background:white;border-radius:12px;padding:16px 20px;
                    border:1px solid #e2e8f0;text-align:center;">
            <span style="font-size:32px;font-weight:700;color:{g_col}">
                {'▲' if growth >= 0 else '▼'} {abs(growth):.2f}%
            </span>
            <div style="color:#64748b;font-size:13px;margin-top:4px">
                {sel_month} vs {prev}
            </div>
        </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════
# 🎯 TARGET TRACKER
# ══════════════════════════════════════════
elif dashboard_type == "🎯 Target Tracker":
    st.title("🎯 Target Tracker")

    with st.sidebar.expander("🔧 Filter", expanded=True):
        # ✅ index=current_month_index
        sel_month = st.selectbox("Month", months, index=current_month_index)
        period = st.radio("Period", ["Monthly", "Weekly"])

    col_ref, col_info = st.columns([1, 5])
    with col_ref:
        if st.button("🔄 Reload Targets"):
            st.cache_data.clear()
            st.rerun()
    with col_info:
        if target_err:
            st.error(f"Target sheet load failed: {target_err}")
        elif target_raw.empty:
            st.warning("Target sheet is empty.")
        else:
            st.success(f"✅ Targets loaded — {len(target_raw)} rows")

    if not target_raw.empty:
        with st.expander("📋 View Raw Target Sheet", expanded=False):
            st.dataframe(target_raw, use_container_width=True, height=250)

    filtered_mgr_df = df[df["Disb Month"] == sel_month]
    mgr_actual = filtered_mgr_df.groupby("Manager")["Disbursed AMT"].sum().reset_index()
    mgr_actual.columns = ["Manager", "Actual"]

    targets_dict = {}
    for _, row in mgr_actual.iterrows():
        mgr = row["Manager"]
        t_val = get_target_for_manager(mgr, sel_month, target_raw)
        targets_dict[mgr] = t_val if t_val > 0 else 50

    section_header("Targets from Sheet")
    preview_data = []
    for _, row in mgr_actual.iterrows():
        mgr = row["Manager"]
        t = get_target_for_manager(mgr, sel_month, target_raw)
        source = "📊 Sheet" if t > 0 else "⚙️ Default (50L)"
        preview_data.append({"Manager": mgr, "Target (L)": targets_dict[mgr], "Source": source})
    st.dataframe(pd.DataFrame(preview_data), use_container_width=True, height=250)

    section_header("Progress Dashboard")
    now_tracker = datetime.now(timezone(timedelta(hours=5, minutes=30)))

    for _, row in mgr_actual.iterrows():
        mgr = row["Manager"]
        actual_l = row["Actual"] / 100000
        target_l = targets_dict.get(mgr, 50)

        if period == "Weekly":
            day_of_month = now_tracker.day
            week_num = (day_of_month - 1) // 7 + 1
            weeks_passed = min(week_num, 4)
            effective_target = (target_l / 4) * weeks_passed
            period_label = f"Week {week_num} pro-rated target"
        else:
            effective_target = target_l
            period_label = "Monthly target"

        pct = min((actual_l / effective_target * 100) if effective_target else 0, 100)
        remaining = max(effective_target - actual_l, 0)

        if pct >= 100:
            bar_color = "#10b981"; status = "✅ Target Achieved!"
        elif pct >= 75:
            bar_color = "#6366f1"; status = f"🔵 {pct:.1f}% — On track"
        elif pct >= 50:
            bar_color = "#f59e0b"; status = f"🟡 {pct:.1f}% — Needs push"
        else:
            bar_color = "#ef4444"; status = f"🔴 {pct:.1f}% — Behind target"

        st.markdown(f"""
        <div class="target-card">
            <div style="display:flex;justify-content:space-between;
                        align-items:center;margin-bottom:4px;">
                <span style="font-weight:700;font-size:15px;color:#0f172a">{mgr}</span>
                <span style="font-size:12px;color:#64748b;font-weight:500">
                    {period_label}: <b>{effective_target:.1f}L</b>
                </span>
            </div>
            <div style="display:flex;justify-content:space-between;
                        align-items:center;font-size:13px;color:#475569;margin-bottom:4px;">
                <span>✅ Achieved: <b style="color:#0f172a">{actual_l:.2f}L</b></span>
                <span>⏳ Remaining: <b style="color:#ef4444">{remaining:.2f}L</b></span>
                <span>🎯 Full Target: <b style="color:#6366f1">{target_l:.1f}L</b></span>
            </div>
            <div class="progress-bar-bg">
                <div class="progress-bar-fill"
                     style="width:{pct:.1f}%;background:{bar_color}"></div>
            </div>
            <div style="display:flex;justify-content:space-between;
                        align-items:center;margin-top:4px;">
                <div style="font-size:12px;font-weight:700;color:{bar_color}">{status}</div>
                <div style="font-size:12px;font-weight:600;color:#94a3b8">{pct:.1f}% complete</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    section_header("Team Progress Overview")
    total_actual = mgr_actual["Actual"].sum() / 100000
    total_target = sum(targets_dict.get(m, 50) for m in mgr_actual["Manager"])
    team_pct = (total_actual / total_target * 100) if total_target else 0

    col_a, col_b, col_c = st.columns(3)
    col_a.markdown(metric_card("Team Disbursed", f"{total_actual:.1f}L", "💼", "#6366f1"),
                   unsafe_allow_html=True)
    col_b.markdown(metric_card("Team Target", f"{total_target:.1f}L", "🎯", "#f59e0b"),
                   unsafe_allow_html=True)
    col_c.markdown(metric_card("Achievement %", f"{team_pct:.1f}%", "📊",
                               "#10b981" if team_pct >= 75 else "#ef4444"),
                   unsafe_allow_html=True)

    section_header("Manager Target vs Actual (Bar)")
    target_df_plot = mgr_actual.copy()
    target_df_plot["Target"]   = target_df_plot["Manager"].map(lambda m: targets_dict.get(m, 50))
    target_df_plot["Actual_L"] = target_df_plot["Actual"] / 100000

    fig_tgt = go.Figure()
    fig_tgt.add_trace(go.Bar(
        name="Target", x=target_df_plot["Manager"], y=target_df_plot["Target"],
        marker_color="#e2e8f0",
        text=[f"{v:.1f}L" for v in target_df_plot["Target"]],
        textposition="outside"
    ))
    fig_tgt.add_trace(go.Bar(
        name="Actual", x=target_df_plot["Manager"], y=target_df_plot["Actual_L"],
        marker_color="#6366f1",
        text=[f"{v:.1f}L" for v in target_df_plot["Actual_L"]],
        textposition="outside"
    ))
    fig_tgt.update_layout(
        barmode="overlay", template="plotly_white", height=420,
        font=dict(family="Inter", size=12), plot_bgcolor="white",
        yaxis_title="Disbursed (Lakhs)",
        legend=dict(orientation="h", y=-0.2),
    )
    st.plotly_chart(fig_tgt, use_container_width=True)


# ══════════════════════════════════════════
# 📅 TEAM vs MONTH
# ══════════════════════════════════════════
elif dashboard_type == "📅 Team vs Month":
    st.title("📅 Team vs Month Comparison")

    ist_tz2 = timezone(timedelta(hours=5, minutes=30))
    now_ist_tvm = datetime.now(ist_tz2)

    with st.sidebar.expander("🔧 Filters", expanded=True):
        # ✅ Month 1 = previous month, Month 2 = current month (auto)
        month1 = st.selectbox("Month 1", months,
                              index=max(0, current_month_index - 1), key="tvm_m1")
        month2 = st.selectbox("Month 2", months,
                              index=current_month_index, key="tvm_m2")
        sel_vertical_tvm = st.selectbox("Vertical", verticals, key="tvm_vert")

        st.markdown("---")
        st.markdown("**📅 Till Date Filter**")

        disb_col = "DISB DATE"
        has_date_col = disb_col in df.columns

        if has_date_col:
            month2_dates = df[df["Disb Month"] == month2][disb_col].dropna()
            if not month2_dates.empty:
                min_date_m2 = month2_dates.min().date()
                max_date_m2 = month2_dates.max().date()
            else:
                min_date_m2 = now_ist_tvm.date().replace(day=1)
                max_date_m2 = now_ist_tvm.date()
        else:
            min_date_m2 = now_ist_tvm.date().replace(day=1)
            max_date_m2 = now_ist_tvm.date()

        enable_till_date = st.checkbox("Enable Till Date Filter", value=False,
                                       key="tvm_till_enable")

        if enable_till_date:
            till_date = st.date_input(
                "Show data till date",
                value=max_date_m2,
                min_value=min_date_m2,
                max_value=max_date_m2,
                key="tvm_till_date",
                help="Filter Month 2 data up to this date."
            )
            st.caption(f"📊 Showing Month 2 data till: **{till_date.strftime('%d %b %Y')}**")
        else:
            till_date = None

    col_ref2, col_info2 = st.columns([1, 5])
    with col_ref2:
        if st.button("🔄 Reload Data"):
            st.cache_data.clear()
            st.rerun()
    with col_info2:
        if target_err:
            st.error(f"Target sheet error: {target_err}")
        elif target_raw.empty:
            st.warning("Target sheet empty.")
        else:
            st.success(f"✅ Target sheet loaded — {len(target_raw)} rows")

    if not target_raw.empty:
        with st.expander("📋 View Raw Target Sheet", expanded=False):
            st.dataframe(target_raw, use_container_width=True, height=220)

    disb_df = df.copy()
    if sel_vertical_tvm != "All":
        disb_df = disb_df[disb_df["Vertical"] == sel_vertical_tvm]

    df_m1 = disb_df[disb_df["Disb Month"] == month1]
    df_m2 = disb_df[disb_df["Disb Month"] == month2]

    if enable_till_date and till_date is not None and has_date_col:
        df_m2 = df_m2[df_m2[disb_col].notna()]
        df_m2 = df_m2[df_m2[disb_col].dt.date <= till_date]
        same_day = till_date.day
        df_m1 = df_m1[df_m1[disb_col].notna()]
        df_m1 = df_m1[df_m1[disb_col].dt.day <= same_day]
        st.info(
            f"📅 **Till Date active:** "
            f"Month 1 ({month1}) filtered till day **{same_day}**, "
            f"Month 2 ({month2}) filtered till **{till_date.strftime('%d %b %Y')}**"
        )
    elif enable_till_date and not has_date_col:
        st.warning("⚠️ 'DISB DATE' column not found. Till Date filter could not be applied.")

    agg_m1 = df_m1.groupby(["Vertical","Manager"])["Disbursed AMT"].sum().reset_index()
    agg_m1.rename(columns={"Disbursed AMT": "M1_Disb"}, inplace=True)

    agg_m2 = df_m2.groupby(["Vertical","Manager"])["Disbursed AMT"].sum().reset_index()
    agg_m2.rename(columns={"Disbursed AMT": "M2_Disb"}, inplace=True)

    comp = pd.merge(agg_m1, agg_m2, on=["Vertical","Manager"], how="outer").fillna(0)

    if comp.empty:
        st.warning("No data found for the selected months/vertical.")
        st.stop()

    comp["M1_Target_L"] = comp["Manager"].apply(
        lambda m: get_target_for_manager(m, month1, target_raw))
    comp["M2_Target_L"] = comp["Manager"].apply(
        lambda m: get_target_for_manager(m, month2, target_raw))

    comp["M1_Disb_L"] = (comp["M1_Disb"] / 100000).round(2)
    comp["M2_Disb_L"] = (comp["M2_Disb"] / 100000).round(2)

    comp["M1_Ach%"] = comp.apply(
        lambda r: round(r["M1_Disb_L"] / r["M1_Target_L"] * 100, 1)
        if r["M1_Target_L"] > 0 else 0.0, axis=1)
    comp["M2_Ach%"] = comp.apply(
        lambda r: round(r["M2_Disb_L"] / r["M2_Target_L"] * 100, 1)
        if r["M2_Target_L"] > 0 else 0.0, axis=1)

    comp["MoM%"] = comp.apply(
        lambda r: round((r["M2_Disb_L"] - r["M1_Disb_L"]) / r["M1_Disb_L"] * 100, 1)
        if r["M1_Disb_L"] > 0 else 0.0, axis=1)

    comp = comp.sort_values(["Vertical","M2_Disb_L"],
                            ascending=[True, False]).reset_index(drop=True)

    section_header("Team Summary")
    total_m1d = comp["M1_Disb_L"].sum()
    total_m2d = comp["M2_Disb_L"].sum()
    total_m1t = comp["M1_Target_L"].sum()
    total_m2t = comp["M2_Target_L"].sum()
    team_m1_ach = round(total_m1d / total_m1t * 100, 1) if total_m1t > 0 else 0.0
    team_m2_ach = round(total_m2d / total_m2t * 100, 1) if total_m2t > 0 else 0.0
    team_mom    = round((total_m2d - total_m1d) / total_m1d * 100, 1) if total_m1d > 0 else 0.0

    m2_label = f"{month2}" + (f" (till {till_date.strftime('%d %b')})"
                              if (enable_till_date and till_date) else "")
    m1_label = f"{month1}" + (f" (till day {till_date.day})"
                              if (enable_till_date and till_date and has_date_col) else "")

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(metric_card(f"{m1_label} Disb", f"{total_m1d:.1f}L", "💰", "#6366f1"),
                unsafe_allow_html=True)
    c2.markdown(metric_card(f"{m2_label} Disb", f"{total_m2d:.1f}L", "💼", "#8b5cf6"),
                unsafe_allow_html=True)
    c3.markdown(metric_card(f"{month1} Ach%", f"{team_m1_ach:.1f}%", "📊",
                            "#10b981" if team_m1_ach >= 75 else "#ef4444"),
                unsafe_allow_html=True)
    c4.markdown(metric_card(f"{month2} Ach%", f"{team_m2_ach:.1f}%", "📈",
                            "#10b981" if team_m2_ach >= 75 else "#ef4444"),
                unsafe_allow_html=True)

    mom_color_strip = "#10b981" if team_mom >= 0 else "#ef4444"
    mom_arrow = "▲" if team_mom >= 0 else "▼"
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#0f172a,#1e293b);border-radius:12px;
                padding:16px 24px;margin:12px 0;display:flex;
                justify-content:space-between;align-items:center;">
        <div style="color:#94a3b8;font-size:13px;font-weight:600">
            MoM Team Change:
            <span style="color:{mom_color_strip};font-size:20px;font-weight:700">
                {mom_arrow} {abs(team_mom):.1f}%
            </span>
        </div>
        <div style="color:#64748b;font-size:12px">{month1} → {month2}</div>
    </div>
    """, unsafe_allow_html=True)

    section_header(f"Manager-wise: {month1} vs {month2}")

    def mom_badge(val):
        if val > 0:
            return (f'<span style="background:#d1fae5;color:#065f46;font-weight:700;'
                    f'font-size:12px;padding:3px 9px;border-radius:5px;white-space:nowrap">'
                    f'▲ {val:.1f}%</span>')
        elif val < 0:
            return (f'<span style="background:#fee2e2;color:#991b1b;font-weight:700;'
                    f'font-size:12px;padding:3px 9px;border-radius:5px;white-space:nowrap">'
                    f'▼ {abs(val):.1f}%</span>')
        else:
            return f'<span style="color:#94a3b8;font-size:12px">0.0%</span>'

    def ach_color(val):
        if val >= 90: return "#065f46"
        elif val >= 70: return "#b45309"
        else: return "#991b1b"

    def ach_bg(val):
        if val >= 90: return "#d1fae5"
        elif val >= 70: return "#fef3c7"
        else: return "#fee2e2"

    rows_html = ""
    for i, row in comp.iterrows():
        bg = "#f8fafc" if i % 2 == 0 else "#ffffff"
        m1t_display = f"{row['M1_Target_L']:.1f}L" if row['M1_Target_L'] > 0 else "—"
        m2t_display = f"{row['M2_Target_L']:.1f}L" if row['M2_Target_L'] > 0 else "—"
        rows_html += f"""
        <tr style="background:{bg};border-bottom:1px solid #f1f5f9">
            <td style="padding:11px 14px;font-size:13px;color:#64748b;font-weight:500">
                {row['Vertical']}</td>
            <td style="padding:11px 14px;font-size:13px;font-weight:700;color:#0f172a">
                {row['Manager']}</td>
            <td style="padding:11px 14px;font-size:13px;text-align:right;
                       color:#6366f1;font-weight:500">{m1t_display}</td>
            <td style="padding:11px 14px;font-size:13px;text-align:right;
                       font-weight:600;color:#0f172a">{row['M1_Disb_L']:.2f}L</td>
            <td style="padding:11px 14px;text-align:right">
                <span style="background:{ach_bg(row['M1_Ach%'])};
                             color:{ach_color(row['M1_Ach%'])};
                             font-weight:700;font-size:12px;
                             padding:3px 8px;border-radius:5px">
                    {row['M1_Ach%']:.1f}%
                </span>
            </td>
            <td style="padding:11px 14px;font-size:13px;text-align:right;
                       color:#8b5cf6;font-weight:500">{m2t_display}</td>
            <td style="padding:11px 14px;font-size:13px;text-align:right;
                       font-weight:600;color:#0f172a">{row['M2_Disb_L']:.2f}L</td>
            <td style="padding:11px 14px;text-align:right">
                <span style="background:{ach_bg(row['M2_Ach%'])};
                             color:{ach_color(row['M2_Ach%'])};
                             font-weight:700;font-size:12px;
                             padding:3px 8px;border-radius:5px">
                    {row['M2_Ach%']:.1f}%
                </span>
            </td>
            <td style="padding:11px 14px;text-align:right">{mom_badge(row['MoM%'])}</td>
        </tr>"""

    rows_html += f"""
    <tr style="background:#1e293b;border-top:2px solid #334155">
        <td colspan="2" style="padding:13px 14px;font-size:13px;font-weight:700;color:#f8fafc">
            🏢 TOTAL</td>
        <td style="padding:13px 14px;font-size:13px;text-align:right;
                   color:#818cf8;font-weight:600">{total_m1t:.1f}L</td>
        <td style="padding:13px 14px;font-size:13px;text-align:right;
                   font-weight:700;color:#f8fafc">{total_m1d:.2f}L</td>
        <td style="padding:13px 14px;text-align:right">
            <span style="background:{ach_bg(team_m1_ach)};color:{ach_color(team_m1_ach)};
                         font-weight:700;font-size:13px;padding:4px 10px;border-radius:5px">
                {team_m1_ach:.1f}%
            </span>
        </td>
        <td style="padding:13px 14px;font-size:13px;text-align:right;
                   color:#a78bfa;font-weight:600">{total_m2t:.1f}L</td>
        <td style="padding:13px 14px;font-size:13px;text-align:right;
                   font-weight:700;color:#f8fafc">{total_m2d:.2f}L</td>
        <td style="padding:13px 14px;text-align:right">
            <span style="background:{ach_bg(team_m2_ach)};color:{ach_color(team_m2_ach)};
                         font-weight:700;font-size:13px;padding:4px 10px;border-radius:5px">
                {team_m2_ach:.1f}%
            </span>
        </td>
        <td style="padding:13px 14px;text-align:right">{mom_badge(team_mom)}</td>
    </tr>"""

    table_html = f"""
    <div style="border-radius:16px;overflow:hidden;border:1px solid #e2e8f0;
                box-shadow:0 2px 8px rgba(0,0,0,0.06);margin-bottom:20px">
        <table style="width:100%;border-collapse:collapse;font-family:'Inter',sans-serif">
            <thead>
                <tr style="background:#0f172a">
                    <th style="padding:13px 14px;text-align:left;font-size:11px;font-weight:600;
                               color:#94a3b8;text-transform:uppercase;letter-spacing:0.07em">Vertical</th>
                    <th style="padding:13px 14px;text-align:left;font-size:11px;font-weight:600;
                               color:#94a3b8;text-transform:uppercase;letter-spacing:0.07em">Manager</th>
                    <th style="padding:13px 14px;text-align:right;font-size:11px;font-weight:600;
                               color:#818cf8;text-transform:uppercase;letter-spacing:0.07em;white-space:nowrap">
                        {month1} Target</th>
                    <th style="padding:13px 14px;text-align:right;font-size:11px;font-weight:600;
                               color:#818cf8;text-transform:uppercase;letter-spacing:0.07em;white-space:nowrap">
                        {month1} Disb</th>
                    <th style="padding:13px 14px;text-align:right;font-size:11px;font-weight:600;
                               color:#818cf8;text-transform:uppercase;letter-spacing:0.07em;white-space:nowrap">
                        {month1} Ach%</th>
                    <th style="padding:13px 14px;text-align:right;font-size:11px;font-weight:600;
                               color:#a78bfa;text-transform:uppercase;letter-spacing:0.07em;white-space:nowrap">
                        {month2} Target</th>
                    <th style="padding:13px 14px;text-align:right;font-size:11px;font-weight:600;
                               color:#a78bfa;text-transform:uppercase;letter-spacing:0.07em;white-space:nowrap">
                        {month2} Disb</th>
                    <th style="padding:13px 14px;text-align:right;font-size:11px;font-weight:600;
                               color:#a78bfa;text-transform:uppercase;letter-spacing:0.07em;white-space:nowrap">
                        {month2} Ach%</th>
                    <th style="padding:13px 14px;text-align:right;font-size:11px;font-weight:600;
                               color:#94a3b8;text-transform:uppercase;letter-spacing:0.07em;white-space:nowrap">
                        MoM %</th>
                </tr>
            </thead>
            <tbody>{rows_html}</tbody>
        </table>
    </div>"""
    st.markdown(table_html, unsafe_allow_html=True)

    section_header(f"Target vs Actual — {month1} & {month2}")
    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        name=f"{month1} Target", x=comp["Manager"], y=comp["M1_Target_L"],
        marker_color="rgba(99,102,241,0.25)",
        text=[f"{v:.1f}L" for v in comp["M1_Target_L"]], textposition="outside"
    ))
    fig_bar.add_trace(go.Bar(
        name=f"{month1} Actual", x=comp["Manager"], y=comp["M1_Disb_L"],
        marker_color="#6366f1",
        text=[f"{v:.1f}L" for v in comp["M1_Disb_L"]], textposition="outside"
    ))
    fig_bar.add_trace(go.Bar(
        name=f"{month2} Target", x=comp["Manager"], y=comp["M2_Target_L"],
        marker_color="rgba(139,92,246,0.25)",
        text=[f"{v:.1f}L" for v in comp["M2_Target_L"]], textposition="outside"
    ))
    fig_bar.add_trace(go.Bar(
        name=f"{month2} Actual", x=comp["Manager"], y=comp["M2_Disb_L"],
        marker_color="#8b5cf6",
        text=[f"{v:.1f}L" for v in comp["M2_Disb_L"]], textposition="outside"
    ))
    fig_bar.update_layout(
        barmode="group", template="plotly_white", height=440,
        font=dict(family="Inter", size=12), plot_bgcolor="white", paper_bgcolor="white",
        yaxis_title="Disbursed (Lakhs)", xaxis_tickangle=-30,
        legend=dict(orientation="h", y=-0.25),
        margin=dict(t=40, b=80)
    )
    fig_bar.update_traces(cliponaxis=False)
    st.plotly_chart(fig_bar, use_container_width=True)

    section_header("MoM Change % per Manager")
    mom_colors = ["#10b981" if v >= 0 else "#ef4444" for v in comp["MoM%"]]
    fig_mom = go.Figure(go.Bar(
        x=comp["Manager"], y=comp["MoM%"],
        marker_color=mom_colors,
        text=[f"{'▲' if v >= 0 else '▼'} {abs(v):.1f}%" for v in comp["MoM%"]],
        textposition="outside", marker_line_width=0,
    ))
    fig_mom.add_hline(y=0, line_dash="dash", line_color="#94a3b8", line_width=1.5)
    fig_mom.update_layout(
        template="plotly_white", height=380,
        font=dict(family="Inter", size=12), plot_bgcolor="white", paper_bgcolor="white",
        yaxis_title="MoM Change (%)", xaxis_tickangle=-30,
        margin=dict(t=40, b=60)
    )
    fig_mom.update_traces(cliponaxis=False)
    st.plotly_chart(fig_mom, use_container_width=True)

    section_header("Achievement % Comparison")
    fig_ach = go.Figure()
    fig_ach.add_trace(go.Bar(
        name=f"{month1} Ach%", x=comp["Manager"], y=comp["M1_Ach%"],
        marker_color="#6366f1",
        text=[f"{v:.1f}%" for v in comp["M1_Ach%"]], textposition="outside"
    ))
    fig_ach.add_trace(go.Bar(
        name=f"{month2} Ach%", x=comp["Manager"], y=comp["M2_Ach%"],
        marker_color="#8b5cf6",
        text=[f"{v:.1f}%" for v in comp["M2_Ach%"]], textposition="outside"
    ))
    fig_ach.add_hline(y=100, line_dash="dot", line_color="#10b981", line_width=1.5,
                      annotation_text="100% Target", annotation_position="top right")
    fig_ach.update_layout(
        barmode="group", template="plotly_white", height=400,
        font=dict(family="Inter", size=12), plot_bgcolor="white", paper_bgcolor="white",
        yaxis_title="Achievement %", xaxis_tickangle=-30,
        legend=dict(orientation="h", y=-0.22),
        margin=dict(t=40, b=70)
    )
    fig_ach.update_traces(cliponaxis=False)
    st.plotly_chart(fig_ach, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    export_df = comp[[
        "Vertical","Manager",
        "M1_Target_L","M1_Disb_L","M1_Ach%",
        "M2_Target_L","M2_Disb_L","M2_Ach%","MoM%"
    ]].copy()
    export_df.columns = [
        "Vertical","Manager",
        f"{month1} Target(L)", f"{month1} Disb(L)", f"{month1} Ach%",
        f"{month2} Target(L)", f"{month2} Disb(L)", f"{month2} Ach%", "MoM%"
    ]
    col_dl1, col_dl2 = st.columns([1, 5])
    with col_dl1:
        st.download_button("⬇️ Download CSV", export_df.to_csv(index=False),
                           "team_vs_month.csv", "text/csv")
    with col_dl2:
        pdf_bytes_tvm = generate_pdf_bytes(export_df,
                                           f"Team vs Month — {month1} vs {month2}")
        if pdf_bytes_tvm:
            st.download_button("📄 Export PDF", pdf_bytes_tvm,
                               "team_vs_month.pdf", "application/pdf")
