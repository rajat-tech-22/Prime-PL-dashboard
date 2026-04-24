import streamlit as st
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
from streamlit_autorefresh import st_autorefresh
import os
import time
import requests
from datetime import datetime, timedelta, timezone
from io import BytesIO
import json
import numpy as np

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
# DARK MODE STATE
# ─────────────────────────────────────────
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

DM = st.session_state.dark_mode

if DM:
    BG        = "#0f172a"
    CARD_BG   = "#1e293b"
    CARD_BOR  = "#334155"
    TEXT_PRI  = "#f1f5f9"
    TEXT_SEC  = "#94a3b8"
    TEXT_MUT  = "#64748b"
    PLOT_BG   = "#1e293b"
    PAPER_BG  = "#1e293b"
    TABLE_HDR = "#0f172a"
    EVEN_ROW  = "#1e293b"
    ODD_ROW   = "#263148"
else:
    BG        = "#f8fafc"
    CARD_BG   = "#ffffff"
    CARD_BOR  = "#e2e8f0"
    TEXT_PRI  = "#0f172a"
    TEXT_SEC  = "#64748b"
    TEXT_MUT  = "#94a3b8"
    PLOT_BG   = "white"
    PAPER_BG  = "white"
    TABLE_HDR = "#0f172a"
    EVEN_ROW  = "#f8fafc"
    ODD_ROW   = "#ffffff"

# ─────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"] {{ font-family: 'Inter', sans-serif !important; }}

.stApp {{ background-color: {BG} !important; }}

[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%) !important;
}}
[data-testid="stSidebar"] * {{ color: #e2e8f0 !important; }}
[data-testid="stSidebar"] .stRadio > label,
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stMultiSelect label,
[data-testid="stSidebar"] .stNumberInput label {{
    color: #cbd5e1 !important; font-size: 12px !important;
    text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600 !important;
}}
[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] *,
[data-testid="stSidebar"] .stMultiSelect div[data-baseweb="select"] *,
[data-testid="stSidebar"] div[data-baseweb="select"] span,
[data-testid="stSidebar"] div[data-baseweb="select"] div {{ color: #000000 !important; font-weight: 500 !important; }}
[data-testid="stSidebar"] div[data-baseweb="select"] > div {{
    background-color: #ffffff !important; border-radius: 8px !important; border: 1px solid #334155 !important;
}}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label p,
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label span {{ color: #e2e8f0 !important; font-size: 14px !important; }}
[data-testid="stSidebar"] span[data-baseweb="tag"] {{ background-color: #e0e7ff !important; }}
[data-testid="stSidebar"] span[data-baseweb="tag"] span {{ color: #1e1b4b !important; font-weight: 600 !important; }}
[data-testid="stSidebar"] details {{
    background: rgba(255,255,255,0.05) !important; border-radius: 10px !important;
    border: 1px solid rgba(255,255,255,0.08) !important; margin-bottom: 8px !important;
}}
[data-testid="stSidebar"] .stButton > button {{
    background: #ef4444 !important; color: white !important;
    border: none !important; border-radius: 8px !important; width: 100%;
}}

.metric-card {{
    background: {CARD_BG}; border-radius: 16px; padding: 20px 24px;
    border: 1px solid {CARD_BOR}; box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    text-align: center; transition: transform 0.2s, box-shadow 0.2s;
    min-height: 110px; display: flex; flex-direction: column;
    justify-content: center; align-items: center;
}}
.metric-card:hover {{ transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.12); }}
.metric-label {{
    font-size: 11px; font-weight: 600; text-transform: uppercase;
    letter-spacing: 0.08em; color: {TEXT_MUT}; margin-bottom: 8px;
}}
.metric-value {{ font-size: 26px; font-weight: 700; color: {TEXT_PRI}; line-height: 1.1; }}
.metric-icon {{ font-size: 20px; margin-bottom: 6px; }}

.section-header {{
    font-size: 18px; font-weight: 700; color: {TEXT_PRI};
    margin: 28px 0 16px 0; padding-left: 12px; border-left: 4px solid #6366f1;
}}

.insight-strip {{
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
    border-radius: 12px; padding: 14px 20px;
    display: flex; justify-content: space-around; flex-wrap: wrap;
    gap: 10px; margin: 16px 0; color: white;
}}
.insight-item {{ text-align: center; font-size: 13px; }}
.insight-item b {{
    display: block; font-size: 11px; opacity: 0.8;
    text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 2px;
}}

.target-card {{
    background: {CARD_BG}; border-radius: 16px; padding: 20px;
    border: 1px solid {CARD_BOR}; box-shadow: 0 1px 3px rgba(0,0,0,0.06); margin-bottom: 16px;
}}
.progress-bar-bg {{
    background: {"#1e293b" if DM else "#f1f5f9"}; border-radius: 999px;
    height: 12px; overflow: hidden; margin: 10px 0 6px 0;
}}
.progress-bar-fill {{ height: 12px; border-radius: 999px; transition: width 0.5s ease; }}

.leader-card {{
    background: {CARD_BG}; border-radius: 16px; padding: 16px 20px;
    border: 1px solid {CARD_BOR}; margin-bottom: 10px;
    display: flex; align-items: center; gap: 16px;
    transition: transform 0.15s;
}}
.leader-card:hover {{ transform: translateX(4px); }}
.leader-rank {{
    font-size: 22px; font-weight: 800; min-width: 40px; text-align: center;
}}
.leader-info {{ flex: 1; }}
.leader-name {{ font-size: 15px; font-weight: 700; color: {TEXT_PRI}; }}
.leader-sub {{ font-size: 12px; color: {TEXT_SEC}; margin-top: 2px; }}
.leader-amt {{ font-size: 18px; font-weight: 800; color: #6366f1; }}
.leader-bar-bg {{
    background: {"#1e293b" if DM else "#f1f5f9"}; border-radius: 999px; height: 6px;
    margin-top: 8px; overflow: hidden;
}}
.leader-bar-fill {{ height: 6px; border-radius: 999px; }}

.alert-card {{
    border-radius: 12px; padding: 14px 18px; margin-bottom: 10px;
    display: flex; align-items: flex-start; gap: 12px;
}}
.alert-danger {{ background: {"#2d1515" if DM else "#fef2f2"}; border: 1px solid #fca5a5; }}
.alert-warning {{ background: {"#2d2415" if DM else "#fffbeb"}; border: 1px solid #fcd34d; }}
.alert-success {{ background: {"#152d1e" if DM else "#f0fdf4"}; border: 1px solid #86efac; }}

.stDownloadButton > button {{
    background: #6366f1 !important; color: white !important;
    border: none !important; border-radius: 8px !important; font-weight: 600 !important;
}}

h1 {{ color: {TEXT_PRI} !important; font-weight: 700 !important; }}
h2 {{ color: {TEXT_PRI} !important; font-weight: 600 !important; }}
h3 {{ color: {TEXT_PRI} !important; font-weight: 600 !important; }}
p, span, div {{ color: {TEXT_PRI}; }}
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
    if not n or n == 0: return "₹0"
    s = str(int(n)); last3 = s[-3:]; rest = s[:-3]; parts = []
    while len(rest) > 2: parts.append(rest[-2:]); rest = rest[:-2]
    if rest: parts.append(rest)
    parts.reverse()
    return "₹" + ",".join(parts) + "," + last3 if parts else "₹" + last3

COLORS = ["#6366f1","#f59e0b","#10b981","#ef4444","#3b82f6","#8b5cf6","#ec4899","#14b8a6"]
GOLD = "#f59e0b"
RANK_COLORS = ["#f59e0b","#94a3b8","#cd7f32","#6366f1","#10b981"]
RANK_EMOJIS = ["🥇","🥈","🥉","4️⃣","5️⃣"]

def get_colors(index_list, top_val):
    return [GOLD if v == top_val else COLORS[i % len(COLORS)] for i, v in enumerate(index_list)]

def calc_metrics(f):
    td = f["Disbursed AMT"].sum(); tr = f["Total_Revenue"].sum()
    ap = (tr / td * 100) if td else 0; tc = len(f); ad = td / tc if tc else 0
    tb    = f.groupby("Bank")["Disbursed AMT"].sum().idxmax() if not f.empty else "N/A"
    tcamp = f.groupby("Campaign")["Disbursed AMT"].sum().idxmax() if not f.empty else "N/A"
    tcall = f.groupby("Caller")["Disbursed AMT"].sum().idxmax() if not f.empty else "N/A"
    return td, tr, ap, tc, ad, tb, tcamp, tcall

def metric_card(label, value, icon="", color="#6366f1"):
    return f"""<div class="metric-card">
        <div class="metric-icon">{icon}</div>
        <div class="metric-label">{label}</div>
        <div class="metric-value" style="color:{color}">{value}</div>
    </div>"""

def section_header(title):
    st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)

def insight_strip(items: dict):
    inner = "".join([f'<div class="insight-item"><b>{k}</b>{v}</div>' for k, v in items.items()])
    st.markdown(f'<div class="insight-strip">{inner}</div>', unsafe_allow_html=True)

def styled_bar(df_group, col, x_col, y_col, title, top_val=None, height=400):
    colors = get_colors(df_group[x_col], top_val or df_group.loc[df_group[y_col].idxmax(), x_col])
    fig = go.Figure(go.Bar(
        x=df_group[x_col], y=df_group[y_col] / 100000,
        text=[f"<b>{v/100000:.2f}L</b>" for v in df_group[y_col]],
        textposition="outside", marker_color=colors, marker_line_width=0,
    ))
    fig.update_layout(
        title=dict(text=title, font=dict(size=15, color=TEXT_PRI)),
        yaxis_title="Amount (Lakhs)", template="plotly_white", height=height,
        plot_bgcolor=PLOT_BG, paper_bgcolor=PAPER_BG,
        font=dict(family="Inter, sans-serif", size=12, color=TEXT_PRI),
        margin=dict(t=50, b=60, l=40, r=20), xaxis=dict(tickangle=-30),
    )
    if DM:
        fig.update_layout(
            xaxis=dict(tickangle=-30, color=TEXT_SEC, gridcolor="#334155"),
            yaxis=dict(color=TEXT_SEC, gridcolor="#334155"),
        )
    fig.update_traces(cliponaxis=False)
    return fig

def generate_pdf_bytes(df_display: pd.DataFrame, title: str) -> bytes:
    try:
        from fpdf import FPDF
        pdf = FPDF(); pdf.add_page()
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 12, title, ln=True, align="C")
        pdf.set_font("Helvetica", "", 8); pdf.ln(4)
        cols = list(df_display.columns)
        col_w = min(190 // len(cols), 40)
        pdf.set_fill_color(99, 102, 241); pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 8)
        for c in cols: pdf.cell(col_w, 8, str(c)[:18], border=1, fill=True)
        pdf.ln(); pdf.set_text_color(15, 23, 42); pdf.set_font("Helvetica", "", 7)
        for _, row in df_display.iterrows():
            for c in cols: pdf.cell(col_w, 7, str(row[c])[:18], border=1)
            pdf.ln()
        return pdf.output()
    except Exception: return b""

def get_current_month_index(months_list):
    if not months_list: return 0
    ist = timezone(timedelta(hours=5, minutes=30))
    now = datetime.now(ist)
    all_formats = [
        "%Y/%m/%d", "%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y",
        "%B %Y", "%b %Y", "%b-%y", "%b-%Y", "%m-%Y",
        "%Y-%m", "%B-%Y", "%m/%Y", "%b/%Y", "%B/%Y",
        "%Y/%m", "%B %y", "%b %y", "%d-%b-%Y",
    ]
    for i, m in enumerate(months_list):
        m_str = str(m).strip()
        for fmt in all_formats:
            try:
                parsed = datetime.strptime(m_str, fmt)
                if parsed.month == now.month and parsed.year == now.year: return i
            except: continue
    cur_year_4 = str(now.year); cur_year_2 = str(now.year)[-2:]
    cur_month_abbr = now.strftime("%b").lower(); cur_month_full = now.strftime("%B").lower()
    cur_mm = now.strftime("%m")
    for i, m in enumerate(months_list):
        m_str = str(m).strip().lower()
        has_year  = cur_year_4 in m_str or cur_year_2 in m_str
        has_month = cur_month_abbr in m_str or cur_month_full in m_str or cur_mm in m_str
        if has_year and has_month: return i
    return len(months_list) - 1

def send_whatsapp_alert(phone, message, wa_token, wa_phone_id):
    try:
        url = f"https://graph.facebook.com/v18.0/{wa_phone_id}/messages"
        headers = {"Authorization": f"Bearer {wa_token}", "Content-Type": "application/json"}
        payload = {"messaging_product": "whatsapp", "to": phone, "type": "text", "text": {"body": message}}
        r = requests.post(url, headers=headers, json=payload, timeout=10)
        return r.status_code == 200
    except: return False

def send_email_alert(to_email, subject, body, smtp_user, smtp_pass):
    try:
        import smtplib
        from email.mime.text import MIMEText
        msg = MIMEText(body, "html")
        msg["Subject"] = subject; msg["From"] = smtp_user; msg["To"] = to_email
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
            s.login(smtp_user, smtp_pass); s.send_message(msg)
        return True
    except: return False

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
    if "Disb Month" in df.columns:
        sample_series = df["Disb Month"].dropna()
        if not sample_series.empty:
            sample_str = str(sample_series.iloc[0]).strip()
            is_date_fmt = False
            for fmt in ["%Y/%m/%d", "%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"]:
                try: datetime.strptime(sample_str, fmt); is_date_fmt = True; break
                except: continue
            if is_date_fmt:
                df["Disb Month"] = pd.to_datetime(df["Disb Month"], errors="coerce").dt.strftime("%b %Y")
    return df

@st.cache_data(ttl=60)
def load_campaign_data():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vROJC-HN52HXZboNKd2rNzYbTHzXtAsewd_hbht7MnQMvpNmVfE9H4fjQA0S06sFZGwPDCErXIPEhsy/pub?output=csv"
    df2 = pd.read_csv(url); df2.columns = df2.columns.str.strip(); return df2

@st.cache_data(ttl=120)
def load_targets():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTplHDYVsgbTHNJsFFqLBzbRc4Gj8RYlrjRs4H8NxRy2V7iAFl0-teSToWaSHz5BReD5rSsgVv1sjMs/pub?output=csv"
    try:
        tdf = pd.read_csv(url); tdf.columns = tdf.columns.str.strip(); return tdf, None
    except Exception as e: return pd.DataFrame(), str(e)

def get_target_for_manager(mgr_name, month_name, tdf):
    if tdf is None or tdf.empty: return 0.0
    cols_lower = {c.lower().strip(): c for c in tdf.columns}
    mgr_col = next((cols_lower[k] for k in ["manager","name","manager name"] if k in cols_lower), None)
    mon_col = next((cols_lower[k] for k in ["month","disb month","month name"] if k in cols_lower), None)
    tgt_col = next((cols_lower[k] for k in ["target","target (l)","target_l","target (lakhs)","amount","target(l)"] if k in cols_lower), None)
    if not mgr_col or not tgt_col: return 0.0
    mgr_rows = tdf[tdf[mgr_col].astype(str).str.strip().str.lower() == mgr_name.strip().lower()]
    if mgr_rows.empty: return 0.0
    if mon_col:
        mon_rows = mgr_rows[mgr_rows[mon_col].astype(str).str.strip().str.lower() == month_name.strip().lower()]
        if not mon_rows.empty:
            try: return float(str(mon_rows.iloc[0][tgt_col]).replace(",","").replace("₹","").strip())
            except: pass
    try: return float(str(mgr_rows.iloc[0][tgt_col]).replace(",","").replace("₹","").strip())
    except: return 0.0

# ─────────────────────────────────────────
# LOGIN PAGE
# ─────────────────────────────────────────
if not st.session_state.login:
    if st.session_state.lock_time:
        elapsed = time.time() - st.session_state.lock_time
        remaining = LOCK_TIME - elapsed
        if remaining > 0:
            h_r = int(remaining // 3600); m_r = int((remaining % 3600) // 60)
            st.error(f"🔒 Account locked. Try again in {h_r}h {m_r}m.")
            st.stop()
        else:
            st.session_state.attempts = 0; st.session_state.lock_time = None

    try:
        _df_login = load_data()
        _months_login = sorted(_df_login["Disb Month"].dropna().unique())
        _latest = _months_login[-1] if _months_login else ""
        _disb_total = _df_login[_df_login["Disb Month"] == _latest]["Disbursed AMT"].sum()
        _rev_total  = _df_login[_df_login["Disb Month"] == _latest]["Total_Revenue"].sum()
        stat1_val = "Rs." + str(round(_disb_total / 10000000, 1)) + "Cr"
        stat1_lbl = str(_latest) + " Disbursed"
        stat2_val = str(round((_rev_total / _disb_total * 100) if _disb_total else 0, 1)) + "%"
        stat2_lbl = "Avg Payout"
    except Exception:
        stat1_val = "Prime PL"; stat1_lbl = "Dashboard"; stat2_val = "Live"; stat2_lbl = "Analytics"

    today_str = now_ist.strftime("%d %b")
    time_str  = now_ist.strftime("%d %b %Y  %I:%M %p")
    attempts_left = MAX_ATTEMPTS - st.session_state.attempts
    dot_color = "#10b981" if attempts_left >= 3 else "#f59e0b" if attempts_left == 2 else "#ef4444"

    st.markdown("""
    <style>
    [data-testid='stSidebar']{display:none!important;}
    [data-testid='stHeader']{display:none!important;}
    [data-testid='stToolbar']{display:none!important;}
    footer{display:none!important;}
    .stApp { background: linear-gradient(135deg,#0f172a 0%,#1e1b4b 40%,#312e81 70%,#4c1d95 100%) !important; min-height: 100vh; }
    [data-testid='stAppViewContainer'] > .main > .block-container {
        max-width: 320px !important; margin: 0 auto !important; padding: 1.5rem 0.5rem !important;
    }
    [data-testid='stAppViewContainer'] .stTextInput > div > div > input {
        border-radius: 8px !important; border: 1.5px solid rgba(255,255,255,0.15) !important;
        padding: 8px 12px !important; font-size: 13px !important;
        background: rgba(255,255,255,0.92) !important; color: #000000 !important; height: 38px !important;
    }
    [data-testid='stAppViewContainer'] .stTextInput > div > div > input:focus {
        border-color: #6366f1 !important; box-shadow: 0 0 0 3px rgba(99,102,241,0.2) !important;
        background: #ffffff !important;
    }
    [data-testid='stAppViewContainer'] .stTextInput label {
        font-size: 11px !important; font-weight: 600 !important;
        color: rgba(255,255,255,0.5) !important; text-transform: uppercase !important;
        letter-spacing: 0.06em !important;
    }
    [data-testid='stAppViewContainer'] .stTextInput > div > div > input::placeholder { color: rgba(0,0,0,0.4) !important; }
    [data-testid='stAppViewContainer'] .stButton > button {
        background: linear-gradient(135deg,#6366f1,#8b5cf6) !important; color: white !important;
        border: none !important; border-radius: 10px !important; font-weight: 700 !important;
        font-size: 14px !important; padding: 0.55rem 1rem !important;
        box-shadow: 0 4px 16px rgba(99,102,241,0.4) !important; margin-top: 4px !important; width: 100% !important;
    }
    </style>""", unsafe_allow_html=True)

    st.markdown("""<div style="text-align:center;margin-bottom:12px;">
        <span style="display:inline-flex;align-items:center;gap:8px;background:rgba(255,255,255,0.08);
            border:1px solid rgba(255,255,255,0.14);border-radius:40px;padding:6px 14px;">
            <span style="font-size:15px;">💼</span>
            <span style="font-size:12px;font-weight:600;color:#e0e7ff;">Prime PL Dashboard</span>
        </span></div>""", unsafe_allow_html=True)

    st.markdown(f"""<div style="text-align:center;margin-bottom:14px;">
        <div style="font-size:19px;font-weight:700;color:#fff;line-height:1.3;margin-bottom:4px;">
            Track. Analyze.<br><span style="color:#a5b4fc;">Grow your portfolio.</span></div>
        <div style="font-size:11px;color:#7c8cba;">Real-time disbursement &nbsp;·&nbsp; Campaign insights &nbsp;·&nbsp; Team targets</div>
    </div>""", unsafe_allow_html=True)

    chart_svg = (
        "<svg viewBox='0 0 300 95' width='50%' style='display:block;margin:0 auto 6px;' xmlns='http://www.w3.org/2000/svg'>"
        "<rect x='5' y='62' width='32' height='32' rx='4' fill='#3730a3' opacity='0.85'/>"
        "<rect x='50' y='50' width='32' height='44' rx='4' fill='#4338ca' opacity='0.9'/>"
        "<rect x='95' y='36' width='32' height='58' rx='4' fill='#4f46e5' opacity='0.9'/>"
        "<rect x='140' y='22' width='32' height='72' rx='4' fill='#6366f1' opacity='0.9'/>"
        "<rect x='185' y='10' width='32' height='84' rx='4' fill='#818cf8' opacity='0.9'/>"
        "<rect x='230' y='2' width='32' height='92' rx='4' fill='#a5b4fc' opacity='0.9'/>"
        "<polyline points='21,62 66,50 111,36 156,22 201,10 246,2' fill='none' stroke='#fbbf24' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round'/>"
        "<circle cx='21' cy='62' r='4' fill='#fbbf24'/><circle cx='66' cy='50' r='4' fill='#fbbf24'/>"
        "<circle cx='111' cy='36' r='4' fill='#fbbf24'/><circle cx='156' cy='22' r='4' fill='#fbbf24'/>"
        "<circle cx='201' cy='10' r='4' fill='#fbbf24'/><circle cx='246' cy='2' r='4' fill='#fbbf24'/>"
        "<text x='21' y='90' fill='#818cf8' font-size='8' text-anchor='middle' font-family='Inter,sans-serif'>Nov</text>"
        "<text x='66' y='90' fill='#818cf8' font-size='8' text-anchor='middle' font-family='Inter,sans-serif'>Dec</text>"
        "<text x='111' y='90' fill='#818cf8' font-size='8' text-anchor='middle' font-family='Inter,sans-serif'>Jan</text>"
        "<text x='156' y='90' fill='#818cf8' font-size='8' text-anchor='middle' font-family='Inter,sans-serif'>Feb</text>"
        "<text x='201' y='90' fill='#818cf8' font-size='8' text-anchor='middle' font-family='Inter,sans-serif'>Mar</text>"
        "<text x='246' y='90' fill='#818cf8' font-size='8' text-anchor='middle' font-family='Inter,sans-serif'>Apr</text>"
        "</svg>"
    )
    pill_style = "background:rgba(99,102,241,0.18);border:1px solid rgba(99,102,241,0.3);border-radius:8px;padding:5px 10px;text-align:center;min-width:70px;"
    stats_row = (
        "<div style='display:flex;gap:6px;justify-content:center;margin-top:6px;flex-wrap:wrap;'>"
        f"<div style='{pill_style}'><div style='font-size:12px;font-weight:700;color:#fff;'>{stat1_val}</div><div style='font-size:10px;color:#a5b4fc;'>{stat1_lbl}</div></div>"
        f"<div style='{pill_style}'><div style='font-size:12px;font-weight:700;color:#fff;'>{stat2_val}</div><div style='font-size:10px;color:#a5b4fc;'>{stat2_lbl}</div></div>"
        f"<div style='{pill_style}'><div style='font-size:12px;font-weight:700;color:#fff;'>{today_str}</div><div style='font-size:10px;color:#a5b4fc;'>Today IST</div></div>"
        "</div>"
    )
    st.markdown(f"<div style='background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);border-radius:14px;padding:12px 14px 10px;margin:0 auto 12px;'>{chart_svg}{stats_row}</div>", unsafe_allow_html=True)
    st.markdown("""<div style="background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);border-radius:14px;padding:14px 16px 4px;">
        <div style="font-size:14px;font-weight:700;color:#fff;margin-bottom:2px;">Welcome back 👋</div>
        <div style="font-size:11px;color:#7c8cba;margin-bottom:4px;">Sign in to your account</div>
    </div>""", unsafe_allow_html=True)

    u = st.text_input("Username", placeholder="Enter username", key="login_user")
    p = st.text_input("Password", type="password", placeholder="Enter password", key="login_pass")
    st.markdown("<div style='margin-top:-6px;margin-bottom:6px;'><button onclick=\"(function(){var i=window.parent.document.querySelector('input[type=password]');if(i)i.type=i.type==='password'?'text':'password';})()\" style='background:none;border:none;cursor:pointer;color:rgba(165,180,252,0.8);font-size:11px;font-weight:600;padding:0;font-family:Inter,sans-serif;'>👁 Show / Hide password</button></div>", unsafe_allow_html=True)

    if st.button("Sign in  →", use_container_width=True, key="login_btn"):
        if u == USERNAME and p == PASSWORD:
            st.session_state.login = True; st.session_state.attempts = 0; st.rerun()
        else:
            st.session_state.attempts += 1
            left_att = MAX_ATTEMPTS - st.session_state.attempts
            if left_att <= 0:
                st.session_state.lock_time = time.time()
                st.error("🔒 Too many attempts. Account locked for 12 hours.")
            else:
                st.warning(f"❌ Invalid credentials — {left_att} attempt(s) remaining.")

    chips_html = (
        "<div style='text-align:center;margin-top:10px;'>"
        "<div style='display:flex;gap:6px;justify-content:center;flex-wrap:wrap;margin-bottom:8px;'>"
        f"<span style='display:inline-flex;align-items:center;gap:4px;background:rgba(255,255,255,0.07);border:1px solid rgba(255,255,255,0.1);border-radius:20px;padding:3px 9px;font-size:10px;color:#94a3b8;'><span style='width:5px;height:5px;border-radius:50%;background:{dot_color};display:inline-block;'></span>{attempts_left}/{MAX_ATTEMPTS} attempts left</span>"
        "<span style='display:inline-flex;align-items:center;gap:4px;background:rgba(255,255,255,0.07);border:1px solid rgba(255,255,255,0.1);border-radius:20px;padding:3px 9px;font-size:10px;color:#94a3b8;'><span style='width:5px;height:5px;border-radius:50%;background:#f59e0b;display:inline-block;'></span>12h lockout</span>"
        "<span style='display:inline-flex;align-items:center;gap:4px;background:rgba(255,255,255,0.07);border:1px solid rgba(255,255,255,0.1);border-radius:20px;padding:3px 9px;font-size:10px;color:#94a3b8;'><span style='width:5px;height:5px;border-radius:50%;background:#6366f1;display:inline-block;'></span>Auto-refresh on</span>"
        f"</div><div style='font-size:10px;color:#475569;padding-top:8px;border-top:1px solid rgba(255,255,255,0.06);'>Prime PL &nbsp;·&nbsp; MyMoneyMantra &nbsp;·&nbsp; {time_str} IST</div></div>"
    )
    st.markdown(chips_html, unsafe_allow_html=True)
    st.stop()

# ─────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────
df = load_data()
campaign_df = load_campaign_data()
target_raw, target_err = load_targets()
months = sorted(df["Disb Month"].dropna().unique())
verticals = ["All"] + sorted(df["Vertical"].dropna().unique())
managers = sorted(df["Manager"].dropna().unique())
current_month_index = get_current_month_index(months)

# ─────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────
with st.sidebar:
    st.markdown("## 💼 Prime PL")
    dm_label = "☀️ Light Mode" if DM else "🌙 Dark Mode"
    if st.button(dm_label, key="dm_toggle"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()
    st.markdown("---")
    dashboard_type = st.radio(
        "Navigation",
        ["🏠 Overview", "👤 Single Manager", "⚖️ Comparison",
         "📊 Campaign Performance", "🎯 Target Tracker",
         "📅 Team vs Month", "🏆 Leaderboard",
         "📈 Advanced Analytics", "🔬 Deep Analysis",   # ← NEW
         "🔔 Alerts & Notifications"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    if st.button("🚪 Logout"):
        st.session_state.login = False; st.rerun()

# ─────────────────────────────────────────
# GREETING
# ─────────────────────────────────────────
ist_tz = timezone(timedelta(hours=5, minutes=30))
now_ist2 = datetime.now(ist_tz)
hour = now_ist2.hour
greet = ("Good Morning 🌅" if 5 <= hour < 12 else "Good Afternoon ☀️" if hour < 16
         else "Good Evening 🌇" if hour < 20 else "Good Night 🌙")

st.markdown(f"""
<div style="background:linear-gradient(135deg,#6366f1,#8b5cf6,#ec4899);
    border-radius:16px;padding:20px 28px;margin-bottom:24px;color:white;">
    <div style="font-size:22px;font-weight:700;">{greet}, Welcome to Prime PL!</div>
    <div style="font-size:13px;opacity:0.85;margin-top:4px;">
        {now_ist2.strftime("%A, %d %B %Y  •  %I:%M %p")} IST
    </div>
</div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════
# 🏠 OVERVIEW
# ══════════════════════════════════════════
if dashboard_type == "🏠 Overview":
    st.title("Overview — All Managers")
    with st.sidebar.expander("🔧 Filters", expanded=True):
        selected_month   = st.selectbox("Month", months, index=current_month_index)
        selected_vertical = st.selectbox("Vertical", verticals)
    filtered_df = df.copy()
    if selected_vertical != "All": filtered_df = filtered_df[filtered_df["Vertical"] == selected_vertical]
    filtered_df = filtered_df[filtered_df["Disb Month"] == selected_month]
    camps = sorted(filtered_df["Campaign"].dropna().unique())
    with st.sidebar.expander("📌 Campaigns", expanded=False):
        sel_camps = st.multiselect("Campaigns", camps, default=camps)
    if sel_camps: filtered_df = filtered_df[filtered_df["Campaign"].isin(sel_camps)]

    if filtered_df.empty:
        st.warning("No data for selected filters.")
    else:
        agg = filtered_df.groupby(["Vertical","Manager"]).agg(
            Total_Disbursed=("Disbursed AMT","sum"), Total_Revenue=("Total_Revenue","sum"),
            Transactions=("Manager","count")).reset_index()
        td = agg["Total_Disbursed"].sum(); tr = agg["Total_Revenue"].sum()
        tt = int(agg["Transactions"].sum()); ap = (tr/td*100) if td else 0
        cols = st.columns(4)
        for col, (lbl,val,icon,clr) in zip(cols,[
            ("Total Disbursed",format_inr(td),"💰","#6366f1"),("Total Revenue",format_inr(tr),"📈","#10b981"),
            ("Avg Payout %",f"{ap:.2f}%","📊","#f59e0b"),("Transactions",f"{tt:,}","🔁","#ef4444")]):
            col.markdown(metric_card(lbl,val,icon,clr),unsafe_allow_html=True)
        top_bank = filtered_df.groupby("Bank")["Disbursed AMT"].sum().idxmax()
        top_campaign = filtered_df.groupby("Campaign")["Disbursed AMT"].sum().idxmax()
        top_caller = filtered_df.groupby("Caller")["Disbursed AMT"].sum().idxmax()
        insight_strip({"🏦 Top Bank":top_bank,"🚀 Top Campaign":top_campaign,"🏆 Top Caller":top_caller,"📅 Month":selected_month})
        section_header("Manager Summary Table")
        disp = agg.copy()
        disp["Total_Disbursed"] = disp["Total_Disbursed"].apply(format_inr)
        disp["Total_Revenue"]   = disp["Total_Revenue"].apply(format_inr)
        st.dataframe(disp, use_container_width=True, height=300)
        c1,c2 = st.columns(2)
        with c1: st.download_button("⬇️ Download CSV", disp.to_csv(index=False), "overview.csv","text/csv")
        section_header("Campaign-wise Disbursed")
        cs = filtered_df.groupby("Campaign")["Disbursed AMT"].sum().reset_index()
        cs.columns = ["Campaign","Disbursed AMT"]
        st.plotly_chart(styled_bar(cs,"Campaign","Campaign","Disbursed AMT","Campaign-wise Disbursed Amount"), use_container_width=True)
        section_header("Bank-wise Disbursed")
        bs = filtered_df.groupby("Bank")["Disbursed AMT"].sum().reset_index()
        bs.columns = ["Bank","Disbursed AMT"]
        st.plotly_chart(styled_bar(bs,"Bank","Bank","Disbursed AMT","Bank-wise Disbursed Amount"), use_container_width=True)


# ══════════════════════════════════════════
# 👤 SINGLE MANAGER
# ══════════════════════════════════════════
elif dashboard_type == "👤 Single Manager":
    with st.sidebar.expander("🔧 Filters", expanded=True):
        sel_month_sm = st.selectbox("Month", months, index=current_month_index, key="sm_month")
        mgr_list = sorted(df[df["Disb Month"]==sel_month_sm]["Manager"].dropna().unique())
        sel_mgr  = st.selectbox("Manager", mgr_list, key="sm_mgr")
        sel_vert_sm = st.selectbox("Vertical", verticals, key="sm_vert")
    f_sm = df[(df["Disb Month"]==sel_month_sm)&(df["Manager"]==sel_mgr)]
    if sel_vert_sm != "All": f_sm = f_sm[f_sm["Vertical"]==sel_vert_sm]
    camps_sm = sorted(f_sm["Campaign"].dropna().unique())
    with st.sidebar.expander("📌 Campaigns", expanded=False):
        sel_camps_sm = st.multiselect("Campaigns", camps_sm, default=camps_sm, key="sm_camps")
    if sel_camps_sm: f_sm = f_sm[f_sm["Campaign"].isin(sel_camps_sm)]
    st.title(f"👤 {sel_mgr} — {sel_month_sm}")
    if f_sm.empty:
        st.warning("No data for selected filters.")
    else:
        td,tr,ap,tc,ad,tb,tcamp,tcall = calc_metrics(f_sm)
        cols = st.columns(4)
        for col,(lbl,val,icon,clr) in zip(cols,[
            ("Total Disbursed",format_inr(td),"💰","#6366f1"),("Total Revenue",format_inr(tr),"📈","#10b981"),
            ("Avg Payout %",f"{ap:.2f}%","📊","#f59e0b"),("Transactions",f"{tc:,}","🔁","#ef4444")]):
            col.markdown(metric_card(lbl,val,icon,clr),unsafe_allow_html=True)
        insight_strip({"🏦 Top Bank":tb,"🚀 Top Campaign":tcamp,"🏆 Top Caller":tcall,"💵 Avg Ticket":f"₹{ad/100000:.2f}L"})
        for title_x, grp_col in [("Campaign-wise Disbursed","Campaign"),("Bank-wise Disbursed","Bank"),("Caller-wise Disbursed","Caller")]:
            section_header(title_x)
            s = f_sm.groupby(grp_col)["Disbursed AMT"].sum().reset_index()
            s.columns = [grp_col,"Disbursed AMT"]
            st.plotly_chart(styled_bar(s,grp_col,grp_col,"Disbursed AMT",title_x), use_container_width=True)
        section_header("Monthly Trend")
        trend = df[df["Manager"]==sel_mgr].groupby("Disb Month")["Disbursed AMT"].sum().reset_index()
        fig_t = go.Figure(go.Scatter(x=trend["Disb Month"],y=trend["Disbursed AMT"]/100000,
            mode="lines+markers",line=dict(width=2.5,color="#6366f1"),marker=dict(size=8)))
        fig_t.update_layout(template="plotly_white",height=380,yaxis_title="Disbursed (L)",
            font=dict(family="Inter"),plot_bgcolor=PLOT_BG,paper_bgcolor=PAPER_BG)
        st.plotly_chart(fig_t,use_container_width=True)
        section_header("Raw Data")
        dd = f_sm.dropna(how="all").copy()
        st.dataframe(dd,use_container_width=True,height=300)
        st.download_button("⬇️ Download CSV",dd.to_csv(index=False),f"{sel_mgr}_{sel_month_sm}.csv","text/csv")


# ══════════════════════════════════════════
# ⚖️ COMPARISON
# ══════════════════════════════════════════
elif dashboard_type == "⚖️ Comparison":
    with st.sidebar.expander("🔧 First Selection", expanded=True):
        m1   = st.selectbox("Month", months, index=current_month_index, key="m1")
        mgr1 = st.selectbox("Manager", sorted(df[df["Disb Month"]==m1]["Manager"].dropna().unique()), key="mgr1")
    f1 = df[(df["Disb Month"]==m1)&(df["Manager"]==mgr1)]
    with st.sidebar.expander("🔧 Second Selection", expanded=True):
        m2   = st.selectbox("Month", months, index=current_month_index, key="m2")
        mgr2 = st.selectbox("Manager", sorted(df[df["Disb Month"]==m2]["Manager"].dropna().unique()), key="mgr2")
    f2 = df[(df["Disb Month"]==m2)&(df["Manager"]==mgr2)]
    with st.sidebar.expander("📌 Campaigns — 1", expanded=False):
        sc1 = st.multiselect("Campaigns", sorted(f1["Campaign"].dropna().unique()), default=sorted(f1["Campaign"].dropna().unique()), key="c1")
    with st.sidebar.expander("📌 Campaigns — 2", expanded=False):
        sc2 = st.multiselect("Campaigns", sorted(f2["Campaign"].dropna().unique()), default=sorted(f2["Campaign"].dropna().unique()), key="c2")
    if sc1: f1 = f1[f1["Campaign"].isin(sc1)]
    if sc2: f2 = f2[f2["Campaign"].isin(sc2)]
    lbl1=f"{mgr1} ({m1})"; lbl2=f"{mgr2} ({m2})"
    st.title("⚖️ Comparison")
    if f1.empty or f2.empty: st.warning("No data for one or both selections."); st.stop()
    d1,r1,p1,t1,a1,tb1,tc1,tcall1 = calc_metrics(f1)
    d2,r2,p2,t2,a2,tb2,tc2,tcall2 = calc_metrics(f2)
    winner = lbl1 if d1>d2 else lbl2
    st.success(f"🏆 Winner: **{winner}** with {format_inr(max(d1,d2))}")
    col1,col2 = st.columns(2)
    cards_meta=[("Total Disbursed","#6366f1"),("Total Revenue","#10b981"),("Avg Payout %","#f59e0b"),("Transactions","#ef4444")]
    vals1=[format_inr(d1),format_inr(r1),f"{p1:.2f}%",f"{t1:,}"]
    vals2=[format_inr(d2),format_inr(r2),f"{p2:.2f}%",f"{t2:,}"]
    with col1:
        st.subheader(lbl1)
        for (lbl,clr),val,ico in zip(cards_meta,vals1,["💰","📈","📊","🔁"]):
            st.markdown(metric_card(lbl,val,ico,clr),unsafe_allow_html=True)
    with col2:
        st.subheader(lbl2)
        for (lbl,clr),val,ico in zip(cards_meta,vals2,["💰","📈","📊","🔁"]):
            st.markdown(metric_card(lbl,val,ico,clr),unsafe_allow_html=True)
    insight_strip({f"{lbl1} Bank":tb1,f"{lbl1} Campaign":tc1,f"{lbl2} Bank":tb2,f"{lbl2} Campaign":tc2})
    section_header("Head-to-Head")
    comp_df = pd.DataFrame({"Metric":["Disbursed (L)","Revenue (L)","Transactions"],lbl1:[d1/100000,r1/100000,t1],lbl2:[d2/100000,r2/100000,t2]})
    fig_c = go.Figure()
    for lbl,vals,clr in [(lbl1,comp_df[lbl1],"#6366f1"),(lbl2,comp_df[lbl2],"#ef4444")]:
        fig_c.add_trace(go.Bar(name=lbl,x=comp_df["Metric"],y=vals,text=[f"<b>{v:.2f}</b>" for v in vals],textposition="outside",marker_color=clr))
    fig_c.update_layout(barmode="group",template="plotly_white",height=420,font=dict(family="Inter"),plot_bgcolor=PLOT_BG,paper_bgcolor=PAPER_BG)
    st.plotly_chart(fig_c,use_container_width=True)
    growth = ((d1-d2)/d2*100) if d2 else 0
    st.info(f"📈 {lbl1} is **{abs(growth):.2f}%** {'higher' if growth>=0 else 'lower'} than {lbl2}")
    for title_x,col_name in [("Bank","Bank"),("Caller","Caller"),("Campaign","Campaign")]:
        section_header(f"{title_x}-wise Comparison")
        fig = go.Figure()
        for f_x,lbl,clr in [(f1,lbl1,"#6366f1"),(f2,lbl2,"#ef4444")]:
            s = f_x.groupby(col_name)["Disbursed AMT"].sum()
            fig.add_trace(go.Bar(x=s.index,y=s.values/100000,text=[f"<b>{v/100000:.2f}L</b>" for v in s.values],textposition="auto",name=lbl,marker_color=clr))
        fig.update_layout(barmode="group",template="plotly_white",xaxis_tickangle=-30,height=400,font=dict(family="Inter"),plot_bgcolor=PLOT_BG,paper_bgcolor=PAPER_BG)
        st.plotly_chart(fig,use_container_width=True)


# ══════════════════════════════════════════
# 📊 CAMPAIGN PERFORMANCE
# ══════════════════════════════════════════
elif dashboard_type == "📊 Campaign Performance":
    with st.sidebar.expander("🔧 Filters", expanded=True):
        sel_month = st.selectbox("Month", months, index=current_month_index)
        temp_df   = df[df["Disb Month"]==sel_month]
        camp_list = sorted(temp_df["Campaign"].dropna().unique())
        c1,c2 = st.columns(2)
        if c1.button("All"):   st.session_state.camp_sel = camp_list
        if c2.button("Clear"): st.session_state.camp_sel = []
        if "camp_sel" not in st.session_state: st.session_state.camp_sel = camp_list
        sel_camps = st.multiselect("Campaigns", camp_list, default=st.session_state.camp_sel)
    camp_f = df[df["Disb Month"]==sel_month]
    if sel_camps: camp_f = camp_f[camp_f["Campaign"].isin(sel_camps)]
    st.title("Campaign Performance")
    if camp_f.empty: st.warning("No data."); st.stop()
    cp = camp_f.groupby("Campaign")["Disbursed AMT"].sum()
    top_c = cp.idxmax()
    st.success(f"🏆 Top Campaign: **{top_c}** — {format_inr(cp.max())}")
    td=camp_f["Disbursed AMT"].sum(); tr=camp_f["Total_Revenue"].sum()
    ap=(tr/td*100) if td else 0
    top_mgr = camp_f.groupby("Manager")["Disbursed AMT"].sum().idxmax()
    cols = st.columns(4)
    for col,(lbl,val,ico,clr) in zip(cols,[("Total Disbursed",format_inr(td),"💰","#6366f1"),
        ("Total Revenue",format_inr(tr),"📈","#10b981"),("Avg Payout %",f"{ap:.2f}%","📊","#f59e0b"),
        ("Best Manager",top_mgr,"🏆","#8b5cf6")]):
        col.markdown(metric_card(lbl,val,ico,clr),unsafe_allow_html=True)
    section_header("Campaign-wise Disbursed")
    cp_df = cp.reset_index(); cp_df.columns = ["Campaign","Disbursed AMT"]
    st.plotly_chart(styled_bar(cp_df,"Campaign","Campaign","Disbursed AMT","Campaign Performance"),use_container_width=True)
    section_header("Manager Performance Table")
    mgr_agg = camp_f.groupby("Manager").agg(Total_Disbursed=("Disbursed AMT","sum"),
        Total_Revenue=("Total_Revenue","sum"),Transactions=("Manager","count")).reset_index()
    mgr_agg["Avg_Payout%"] = (mgr_agg["Total_Revenue"]/mgr_agg["Total_Disbursed"]*100).round(2)
    mgr_disp = mgr_agg.copy()
    mgr_disp["Total_Disbursed"] = mgr_disp["Total_Disbursed"].apply(format_inr)
    mgr_disp["Total_Revenue"]   = mgr_disp["Total_Revenue"].apply(format_inr)
    st.dataframe(mgr_disp,use_container_width=True,height=320)
    c1,c2 = st.columns(2)
    with c1: st.download_button("⬇️ Download CSV",mgr_disp.to_csv(index=False),"campaign_perf.csv","text/csv")
    section_header("Bank-wise Disbursed")
    bk = camp_f.groupby("Bank")["Disbursed AMT"].sum().reset_index(); bk.columns=["Bank","Disbursed AMT"]
    st.plotly_chart(styled_bar(bk,"Bank","Bank","Disbursed AMT","Bank-wise Performance"),use_container_width=True)


# ══════════════════════════════════════════
# 🎯 TARGET TRACKER
# ══════════════════════════════════════════
elif dashboard_type == "🎯 Target Tracker":
    st.title("🎯 Target Tracker")
    with st.sidebar.expander("🔧 Filter", expanded=True):
        sel_month = st.selectbox("Month", months, index=current_month_index)
        period    = st.radio("Period", ["Monthly","Weekly"])
    col_ref,col_info = st.columns([1,5])
    with col_ref:
        if st.button("🔄 Reload"):
            st.cache_data.clear(); st.rerun()
    with col_info:
        if target_err: st.error(f"Target sheet load failed: {target_err}")
        elif target_raw.empty: st.warning("Target sheet is empty.")
        else: st.success(f"✅ Targets loaded — {len(target_raw)} rows")
    if not target_raw.empty:
        with st.expander("📋 View Raw Target Sheet", expanded=False):
            st.dataframe(target_raw,use_container_width=True,height=250)
    filtered_mgr_df = df[df["Disb Month"]==sel_month]
    mgr_actual = filtered_mgr_df.groupby("Manager")["Disbursed AMT"].sum().reset_index()
    mgr_actual.columns = ["Manager","Actual"]
    targets_dict = {}
    for _,row in mgr_actual.iterrows():
        t = get_target_for_manager(row["Manager"],sel_month,target_raw)
        targets_dict[row["Manager"]] = t if t>0 else 50
    section_header("Progress Dashboard")
    now_tracker = datetime.now(timezone(timedelta(hours=5,minutes=30)))
    for _,row in mgr_actual.iterrows():
        mgr=row["Manager"]; actual_l=row["Actual"]/100000; target_l=targets_dict.get(mgr,50)
        if period=="Weekly":
            week_num=(now_tracker.day-1)//7+1; weeks_passed=min(week_num,4)
            effective_target=(target_l/4)*weeks_passed; period_label=f"Week {week_num} pro-rated"
        else:
            effective_target=target_l; period_label="Monthly target"
        pct=min((actual_l/effective_target*100) if effective_target else 0,100)
        remaining=max(effective_target-actual_l,0)
        if pct>=100:   bar_color="#10b981"; status="✅ Target Achieved!"
        elif pct>=75:  bar_color="#6366f1"; status=f"🔵 {pct:.1f}% — On track"
        elif pct>=50:  bar_color="#f59e0b"; status=f"🟡 {pct:.1f}% — Needs push"
        else:          bar_color="#ef4444"; status=f"🔴 {pct:.1f}% — Behind target"
        st.markdown(f"""<div class="target-card">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
                <span style="font-weight:700;font-size:15px;color:{TEXT_PRI}">{mgr}</span>
                <span style="font-size:12px;color:{TEXT_SEC}">{period_label}: <b>{effective_target:.1f}L</b></span>
            </div>
            <div style="display:flex;justify-content:space-between;font-size:13px;color:{TEXT_SEC};margin-bottom:4px;">
                <span>✅ Achieved: <b style="color:{TEXT_PRI}">{actual_l:.2f}L</b></span>
                <span>⏳ Remaining: <b style="color:#ef4444">{remaining:.2f}L</b></span>
                <span>🎯 Target: <b style="color:#6366f1">{target_l:.1f}L</b></span>
            </div>
            <div class="progress-bar-bg"><div class="progress-bar-fill" style="width:{pct:.1f}%;background:{bar_color}"></div></div>
            <div style="display:flex;justify-content:space-between;margin-top:4px;">
                <div style="font-size:12px;font-weight:700;color:{bar_color}">{status}</div>
                <div style="font-size:12px;color:{TEXT_MUT}">{pct:.1f}% complete</div>
            </div>
        </div>""", unsafe_allow_html=True)
    section_header("Team Overview")
    total_actual = mgr_actual["Actual"].sum()/100000
    total_target = sum(targets_dict.values())
    team_pct = (total_actual/total_target*100) if total_target else 0
    col_a,col_b,col_c = st.columns(3)
    col_a.markdown(metric_card("Team Disbursed",f"{total_actual:.1f}L","💼","#6366f1"),unsafe_allow_html=True)
    col_b.markdown(metric_card("Team Target",f"{total_target:.1f}L","🎯","#f59e0b"),unsafe_allow_html=True)
    col_c.markdown(metric_card("Achievement %",f"{team_pct:.1f}%","📊","#10b981" if team_pct>=75 else "#ef4444"),unsafe_allow_html=True)


# ══════════════════════════════════════════
# 📅 TEAM vs MONTH
# ══════════════════════════════════════════
elif dashboard_type == "📅 Team vs Month":
    st.title("📅 Team vs Month Comparison")
    ist_tz2 = timezone(timedelta(hours=5,minutes=30)); now_ist_tvm = datetime.now(ist_tz2)
    with st.sidebar.expander("🔧 Filters", expanded=True):
        month1 = st.selectbox("Month 1 (Prev)", months, index=max(0,current_month_index-1), key="tvm_m1")
        month2 = st.selectbox("Month 2 (Current)", months, index=current_month_index, key="tvm_m2")
        sel_vertical_tvm = st.selectbox("Vertical", verticals, key="tvm_vert")
        all_camps_tvm = sorted(df[df["Disb Month"].isin([month1,month2])]["Campaign"].dropna().unique())
        sel_camps_tvm = st.multiselect("Campaigns", all_camps_tvm, default=all_camps_tvm, key="tvm_camps")
        st.markdown("---"); st.markdown("**📅 Till Date Filter**")
        disb_col = "DISB DATE"; has_date_col = disb_col in df.columns
        if has_date_col:
            month2_dates = df[df["Disb Month"]==month2][disb_col].dropna()
            min_date_m2 = month2_dates.min().date() if not month2_dates.empty else now_ist_tvm.date().replace(day=1)
            max_date_m2 = month2_dates.max().date() if not month2_dates.empty else now_ist_tvm.date()
        else:
            min_date_m2 = now_ist_tvm.date().replace(day=1); max_date_m2 = now_ist_tvm.date()
        enable_till_date = st.checkbox("Enable Till Date Filter", value=False, key="tvm_till_enable")
        if enable_till_date:
            till_date = st.date_input("Show data till date",value=max_date_m2,min_value=min_date_m2,max_value=max_date_m2,key="tvm_till_date")
            st.caption(f"📊 Till: **{till_date.strftime('%d %b %Y')}**")
        else: till_date = None

    col_ref2,col_info2 = st.columns([1,5])
    with col_ref2:
        if st.button("🔄 Reload Data"): st.cache_data.clear(); st.rerun()
    with col_info2:
        if target_err: st.error(f"Target sheet error: {target_err}")
        elif target_raw.empty: st.warning("Target sheet empty.")
        else: st.success(f"✅ Target sheet loaded — {len(target_raw)} rows")

    disb_df = df.copy()
    if sel_vertical_tvm != "All": disb_df = disb_df[disb_df["Vertical"]==sel_vertical_tvm]
    if sel_camps_tvm: disb_df = disb_df[disb_df["Campaign"].isin(sel_camps_tvm)]
    df_m1 = disb_df[disb_df["Disb Month"]==month1].copy()
    df_m2 = disb_df[disb_df["Disb Month"]==month2].copy()

    if enable_till_date and has_date_col:
        m2_valid = df_m2[disb_col].dropna()
        if not m2_valid.empty:
            if till_date is None: till_date = m2_valid.max().date()
            m2_f = df_m2[df_m2[disb_col].notna()]
            m2_f = m2_f[m2_f[disb_col].dt.date <= till_date]
            if m2_f.empty:
                till_date = m2_valid.max().date()
                m2_f = df_m2[df_m2[disb_col].notna()]
                m2_f = m2_f[m2_f[disb_col].dt.date <= till_date]
                st.warning(f"⚠️ Showing till last available: {till_date.strftime('%d %b %Y')}")
            df_m2 = m2_f; same_day = till_date.day
            m1_valid = df_m1[disb_col].dropna()
            if not m1_valid.empty:
                df_m1_f = df_m1[df_m1[disb_col].notna()]
                df_m1_f = df_m1_f[df_m1_f[disb_col].dt.day <= same_day]
                if not df_m1_f.empty: df_m1 = df_m1_f
            st.info(f"📅 M1 till day {same_day} | M2 till {till_date.strftime('%d %b %Y')}")

    agg_m1 = df_m1.groupby(["Vertical","Manager"])["Disbursed AMT"].sum().reset_index()
    agg_m1.rename(columns={"Disbursed AMT":"M1_Disb"},inplace=True)
    agg_m2 = df_m2.groupby(["Vertical","Manager"])["Disbursed AMT"].sum().reset_index()
    agg_m2.rename(columns={"Disbursed AMT":"M2_Disb"},inplace=True)
    comp = pd.merge(agg_m1,agg_m2,on=["Vertical","Manager"],how="outer").fillna(0)
    if comp.empty: st.warning("No data found."); st.stop()
    comp["M1_Target_L"] = comp["Manager"].apply(lambda m: get_target_for_manager(m,month1,target_raw))
    comp["M2_Target_L"] = comp["Manager"].apply(lambda m: get_target_for_manager(m,month2,target_raw))
    comp["M1_Disb_L"] = (comp["M1_Disb"]/100000).round(2)
    comp["M2_Disb_L"] = (comp["M2_Disb"]/100000).round(2)
    comp["M1_Ach%"] = comp.apply(lambda r: round(r["M1_Disb_L"]/r["M1_Target_L"]*100,1) if r["M1_Target_L"]>0 else 0.0,axis=1)
    comp["M2_Ach%"] = comp.apply(lambda r: round(r["M2_Disb_L"]/r["M2_Target_L"]*100,1) if r["M2_Target_L"]>0 else 0.0,axis=1)
    comp["MoM%"]    = comp.apply(lambda r: round((r["M2_Disb_L"]-r["M1_Disb_L"])/r["M1_Disb_L"]*100,1) if r["M1_Disb_L"]>0 else 0.0,axis=1)
    comp = comp.sort_values(["Vertical","M2_Disb_L"],ascending=[True,False]).reset_index(drop=True)

    section_header("Team Summary")
    total_m1d=comp["M1_Disb_L"].sum(); total_m2d=comp["M2_Disb_L"].sum()
    total_m1t=comp["M1_Target_L"].sum(); total_m2t=comp["M2_Target_L"].sum()
    team_m1_ach=round(total_m1d/total_m1t*100,1) if total_m1t>0 else 0.0
    team_m2_ach=round(total_m2d/total_m2t*100,1) if total_m2t>0 else 0.0
    team_mom=round((total_m2d-total_m1d)/total_m1d*100,1) if total_m1d>0 else 0.0
    c1,c2,c3,c4 = st.columns(4)
    c1.markdown(metric_card(f"{month1} Disb",f"{total_m1d:.1f}L","💰","#6366f1"),unsafe_allow_html=True)
    c2.markdown(metric_card(f"{month2} Disb",f"{total_m2d:.1f}L","💼","#8b5cf6"),unsafe_allow_html=True)
    c3.markdown(metric_card(f"{month1} Ach%",f"{team_m1_ach:.1f}%","📊","#10b981" if team_m1_ach>=75 else "#ef4444"),unsafe_allow_html=True)
    c4.markdown(metric_card(f"{month2} Ach%",f"{team_m2_ach:.1f}%","📈","#10b981" if team_m2_ach>=75 else "#ef4444"),unsafe_allow_html=True)

    mom_clr = "#10b981" if team_mom>=0 else "#ef4444"
    st.markdown(f"""<div style="background:linear-gradient(135deg,#0f172a,#1e293b);border-radius:12px;
        padding:16px 24px;margin:12px 0;display:flex;justify-content:space-between;align-items:center;">
        <div style="color:#94a3b8;font-size:13px;font-weight:600">MoM Team Change:
            <span style="color:{mom_clr};font-size:20px;font-weight:700">{"▲" if team_mom>=0 else "▼"} {abs(team_mom):.1f}%</span>
        </div><div style="color:#64748b;font-size:12px">{month1} → {month2}</div>
    </div>""", unsafe_allow_html=True)

    def mom_badge(val):
        if val>0: return f'<span style="background:#d1fae5;color:#065f46;font-weight:700;font-size:12px;padding:3px 9px;border-radius:5px">▲ {val:.1f}%</span>'
        elif val<0: return f'<span style="background:#fee2e2;color:#991b1b;font-weight:700;font-size:12px;padding:3px 9px;border-radius:5px">▼ {abs(val):.1f}%</span>'
        else: return f'<span style="color:#94a3b8;font-size:12px">—</span>'
    def ach_color(v): return "#065f46" if v>=90 else "#b45309" if v>=70 else "#991b1b"
    def ach_bg(v): return "#d1fae5" if v>=90 else "#fef3c7" if v>=70 else "#fee2e2"

    rows_html = ""
    for i,row in comp.iterrows():
        bg = EVEN_ROW if i%2==0 else ODD_ROW
        m1t = f"{row['M1_Target_L']:.1f}L" if row['M1_Target_L']>0 else "—"
        m2t = f"{row['M2_Target_L']:.1f}L" if row['M2_Target_L']>0 else "—"
        rows_html += f"""<tr style="background:{bg};border-bottom:1px solid {CARD_BOR}">
            <td style="padding:11px 14px;font-size:13px;color:{TEXT_SEC}">{row['Vertical']}</td>
            <td style="padding:11px 14px;font-size:13px;font-weight:700;color:{TEXT_PRI}">{row['Manager']}</td>
            <td style="padding:11px 14px;text-align:right;color:#6366f1;font-size:13px">{m1t}</td>
            <td style="padding:11px 14px;text-align:right;font-weight:600;color:{TEXT_PRI};font-size:13px">{row['M1_Disb_L']:.2f}L</td>
            <td style="padding:11px 14px;text-align:right"><span style="background:{ach_bg(row['M1_Ach%'])};color:{ach_color(row['M1_Ach%'])};font-weight:700;font-size:12px;padding:3px 8px;border-radius:5px">{row['M1_Ach%']:.1f}%</span></td>
            <td style="padding:11px 14px;text-align:right;color:#8b5cf6;font-size:13px">{m2t}</td>
            <td style="padding:11px 14px;text-align:right;font-weight:600;color:{TEXT_PRI};font-size:13px">{row['M2_Disb_L']:.2f}L</td>
            <td style="padding:11px 14px;text-align:right"><span style="background:{ach_bg(row['M2_Ach%'])};color:{ach_color(row['M2_Ach%'])};font-weight:700;font-size:12px;padding:3px 8px;border-radius:5px">{row['M2_Ach%']:.1f}%</span></td>
            <td style="padding:11px 14px;text-align:right">{mom_badge(row['MoM%'])}</td>
        </tr>"""
    rows_html += f"""<tr style="background:#1e293b;border-top:2px solid #334155">
        <td colspan="2" style="padding:13px 14px;font-weight:700;color:#f8fafc;font-size:13px">🏢 TOTAL</td>
        <td style="padding:13px 14px;text-align:right;color:#818cf8;font-weight:600;font-size:13px">{total_m1t:.1f}L</td>
        <td style="padding:13px 14px;text-align:right;font-weight:700;color:#f8fafc;font-size:13px">{total_m1d:.2f}L</td>
        <td style="padding:13px 14px;text-align:right"><span style="background:{ach_bg(team_m1_ach)};color:{ach_color(team_m1_ach)};font-weight:700;font-size:13px;padding:4px 10px;border-radius:5px">{team_m1_ach:.1f}%</span></td>
        <td style="padding:13px 14px;text-align:right;color:#a78bfa;font-weight:600;font-size:13px">{total_m2t:.1f}L</td>
        <td style="padding:13px 14px;text-align:right;font-weight:700;color:#f8fafc;font-size:13px">{total_m2d:.2f}L</td>
        <td style="padding:13px 14px;text-align:right"><span style="background:{ach_bg(team_m2_ach)};color:{ach_color(team_m2_ach)};font-weight:700;font-size:13px;padding:4px 10px;border-radius:5px">{team_m2_ach:.1f}%</span></td>
        <td style="padding:13px 14px;text-align:right">{mom_badge(team_mom)}</td>
    </tr>"""
    section_header(f"Manager-wise: {month1} vs {month2}")
    st.markdown(f"""<div style="border-radius:16px;overflow:hidden;border:1px solid {CARD_BOR};box-shadow:0 2px 8px rgba(0,0,0,0.06);margin-bottom:20px">
        <table style="width:100%;border-collapse:collapse;font-family:'Inter',sans-serif">
        <thead><tr style="background:#0f172a">
            <th style="padding:13px 14px;text-align:left;font-size:11px;font-weight:600;color:#94a3b8;text-transform:uppercase">Vertical</th>
            <th style="padding:13px 14px;text-align:left;font-size:11px;font-weight:600;color:#94a3b8;text-transform:uppercase">Manager</th>
            <th style="padding:13px 14px;text-align:right;font-size:11px;font-weight:600;color:#818cf8;text-transform:uppercase;white-space:nowrap">{month1} Target</th>
            <th style="padding:13px 14px;text-align:right;font-size:11px;font-weight:600;color:#818cf8;text-transform:uppercase;white-space:nowrap">{month1} Disb</th>
            <th style="padding:13px 14px;text-align:right;font-size:11px;font-weight:600;color:#818cf8;text-transform:uppercase;white-space:nowrap">{month1} Ach%</th>
            <th style="padding:13px 14px;text-align:right;font-size:11px;font-weight:600;color:#a78bfa;text-transform:uppercase;white-space:nowrap">{month2} Target</th>
            <th style="padding:13px 14px;text-align:right;font-size:11px;font-weight:600;color:#a78bfa;text-transform:uppercase;white-space:nowrap">{month2} Disb</th>
            <th style="padding:13px 14px;text-align:right;font-size:11px;font-weight:600;color:#a78bfa;text-transform:uppercase;white-space:nowrap">{month2} Ach%</th>
            <th style="padding:13px 14px;text-align:right;font-size:11px;font-weight:600;color:#94a3b8;text-transform:uppercase;white-space:nowrap">MoM %</th>
        </tr></thead><tbody>{rows_html}</tbody></table></div>""", unsafe_allow_html=True)

    section_header("Target vs Actual Chart")
    fig_bar = go.Figure()
    for name,y,clr in [(f"{month1} Target",comp["M1_Target_L"],"rgba(99,102,241,0.25)"),
                        (f"{month1} Actual",comp["M1_Disb_L"],"#6366f1"),
                        (f"{month2} Target",comp["M2_Target_L"],"rgba(139,92,246,0.25)"),
                        (f"{month2} Actual",comp["M2_Disb_L"],"#8b5cf6")]:
        fig_bar.add_trace(go.Bar(name=name,x=comp["Manager"],y=y,text=[f"{v:.1f}L" for v in y],textposition="outside",marker_color=clr))
    fig_bar.update_layout(barmode="group",template="plotly_white",height=440,font=dict(family="Inter",size=12),
        plot_bgcolor=PLOT_BG,paper_bgcolor=PAPER_BG,yaxis_title="Disbursed (Lakhs)",xaxis_tickangle=-30,
        legend=dict(orientation="h",y=-0.25),margin=dict(t=40,b=80))
    fig_bar.update_traces(cliponaxis=False)
    st.plotly_chart(fig_bar,use_container_width=True)

    export_df = comp[["Vertical","Manager","M1_Target_L","M1_Disb_L","M1_Ach%","M2_Target_L","M2_Disb_L","M2_Ach%","MoM%"]].copy()
    export_df.columns = ["Vertical","Manager",f"{month1} Target(L)",f"{month1} Disb(L)",f"{month1} Ach%",f"{month2} Target(L)",f"{month2} Disb(L)",f"{month2} Ach%","MoM%"]
    col_dl1,col_dl2 = st.columns([1,5])
    with col_dl1: st.download_button("⬇️ Download CSV",export_df.to_csv(index=False),"team_vs_month.csv","text/csv")


# ══════════════════════════════════════════
# 🏆 LEADERBOARD
# ══════════════════════════════════════════
elif dashboard_type == "🏆 Leaderboard":
    st.title("🏆 Leaderboard")
    with st.sidebar.expander("🔧 Filters", expanded=True):
        sel_month_lb = st.selectbox("Month", months, index=current_month_index, key="lb_month")
        lb_by        = st.radio("Rank By", ["Disbursed AMT","Total_Revenue","Transactions"], key="lb_by")
        lb_entity    = st.radio("Entity", ["Manager","Caller","Campaign","Bank"], key="lb_entity")
        top_n        = st.slider("Top N", 3, 20, 5, key="lb_topn")

    lb_df = df[df["Disb Month"]==sel_month_lb].copy()
    if lb_by == "Transactions":
        lb_agg = lb_df.groupby(lb_entity).size().reset_index(name="Value")
    else:
        lb_agg = lb_df.groupby(lb_entity)[lb_by].sum().reset_index()
        lb_agg.columns = [lb_entity,"Value"]
    lb_agg = lb_agg.sort_values("Value",ascending=False).head(top_n).reset_index(drop=True)

    if lb_agg.empty:
        st.warning("No data for selected filters.")
    else:
        max_val = lb_agg["Value"].max()
        st.markdown(f"""<div style="background:linear-gradient(135deg,#f59e0b,#d97706);
            border-radius:16px;padding:20px 28px;margin-bottom:24px;color:white;">
            <div style="font-size:20px;font-weight:700;">🏆 Top {top_n} {lb_entity}s</div>
            <div style="font-size:13px;opacity:0.85;">{sel_month_lb} · Ranked by {lb_by.replace('_',' ')}</div>
        </div>""", unsafe_allow_html=True)

        if len(lb_agg) >= 3:
            section_header("🎖️ Podium")
            pc1,pc2,pc3 = st.columns([1,1.2,1])
            podium_data = [(pc2, 0, "#f59e0b","🥇","Gold"), (pc1, 1, "#94a3b8","🥈","Silver"), (pc3, 2, "#cd7f32","🥉","Bronze")]
            for col,idx,clr,emoji,title_p in podium_data:
                row_p = lb_agg.iloc[idx]
                val_display = f"{row_p['Value']/100000:.2f}L" if lb_by!="Transactions" else f"{int(row_p['Value'])}"
                col.markdown(f"""<div style="background:{CARD_BG};border-radius:16px;padding:20px;
                    border:2px solid {clr};text-align:center;box-shadow:0 4px 16px rgba(0,0,0,0.1);">
                    <div style="font-size:36px">{emoji}</div>
                    <div style="font-size:13px;font-weight:700;color:{TEXT_PRI};margin:8px 0 4px">{row_p[lb_entity]}</div>
                    <div style="font-size:20px;font-weight:800;color:{clr}">{val_display}</div>
                    <div style="font-size:11px;color:{TEXT_MUT};margin-top:4px">{title_p}</div>
                </div>""", unsafe_allow_html=True)

        section_header("📊 Full Rankings")
        for i, row in lb_agg.iterrows():
            rank = i + 1
            val = row["Value"]
            pct = (val / max_val * 100) if max_val > 0 else 0
            clr = RANK_COLORS[i] if i < len(RANK_COLORS) else "#6366f1"
            emoji = RANK_EMOJIS[i] if i < len(RANK_EMOJIS) else f"#{rank}"
            val_display = f"{val/100000:.2f}L" if lb_by != "Transactions" else f"{int(val)}"
            sub_text = f"₹{val/100000:.2f} Lakhs" if lb_by != "Transactions" else f"{int(val)} transactions"
            st.markdown(f"""<div class="leader-card">
                <div class="leader-rank" style="color:{clr}">{emoji}</div>
                <div class="leader-info">
                    <div class="leader-name">{row[lb_entity]}</div>
                    <div class="leader-sub">{sub_text}</div>
                    <div class="leader-bar-bg"><div class="leader-bar-fill" style="width:{pct:.1f}%;background:{clr}"></div></div>
                </div>
                <div class="leader-amt" style="color:{clr}">{val_display}</div>
            </div>""", unsafe_allow_html=True)

        section_header("📈 Bar Chart")
        fig_lb = go.Figure(go.Bar(
            x=lb_agg["Value"] / (100000 if lb_by != "Transactions" else 1),
            y=lb_agg[lb_entity], orientation="h",
            text=[f"{v/100000:.2f}L" if lb_by!="Transactions" else str(int(v)) for v in lb_agg["Value"]],
            textposition="outside",
            marker_color=[RANK_COLORS[i] if i < len(RANK_COLORS) else "#6366f1" for i in range(len(lb_agg))],
        ))
        fig_lb.update_layout(
            template="plotly_white", height=max(300, len(lb_agg)*60),
            plot_bgcolor=PLOT_BG, paper_bgcolor=PAPER_BG,
            font=dict(family="Inter",size=12,color=TEXT_PRI),
            xaxis_title="Lakhs" if lb_by!="Transactions" else "Count",
            yaxis=dict(autorange="reversed"),
            margin=dict(t=20,b=40,l=140,r=80),
        )
        fig_lb.update_traces(cliponaxis=False)
        st.plotly_chart(fig_lb, use_container_width=True)


# ══════════════════════════════════════════
# 📈 ADVANCED ANALYTICS
# ══════════════════════════════════════════
elif dashboard_type == "📈 Advanced Analytics":
    st.title("📈 Advanced Analytics")
    with st.sidebar.expander("🔧 Filters", expanded=True):
        sel_month_aa = st.selectbox("Month", months, index=current_month_index, key="aa_month")
        sel_vert_aa  = st.selectbox("Vertical", verticals, key="aa_vert")

    aa_df = df.copy()
    if sel_vert_aa != "All": aa_df = aa_df[aa_df["Vertical"]==sel_vert_aa]
    aa_month_df = aa_df[aa_df["Disb Month"]==sel_month_aa]

    section_header("🏆 Top 5 Performers — This Month")
    top5_mgr = aa_month_df.groupby("Manager")["Disbursed AMT"].sum().nlargest(5).reset_index()
    top5_mgr.columns = ["Manager","Disbursed AMT"]
    t5_cols = st.columns(min(5,len(top5_mgr)))
    for i,(col,(_,row)) in enumerate(zip(t5_cols, top5_mgr.iterrows())):
        emoji = RANK_EMOJIS[i] if i < len(RANK_EMOJIS) else f"#{i+1}"
        clr   = RANK_COLORS[i] if i < len(RANK_COLORS) else "#6366f1"
        col.markdown(f"""<div style="background:{CARD_BG};border-radius:14px;padding:16px 12px;
            border:2px solid {clr};text-align:center;">
            <div style="font-size:28px">{emoji}</div>
            <div style="font-size:12px;font-weight:700;color:{TEXT_PRI};margin:6px 0 4px">{row['Manager']}</div>
            <div style="font-size:16px;font-weight:800;color:{clr}">{row['Disbursed AMT']/100000:.1f}L</div>
        </div>""", unsafe_allow_html=True)

    section_header("📞 Top 5 Callers")
    top5_caller = aa_month_df.groupby("Caller")["Disbursed AMT"].sum().nlargest(5).reset_index()
    top5_caller.columns = ["Caller","Disbursed AMT"]
    t5c_cols = st.columns(min(5,len(top5_caller)))
    for i,(col,(_,row)) in enumerate(zip(t5c_cols, top5_caller.iterrows())):
        emoji = RANK_EMOJIS[i] if i < len(RANK_EMOJIS) else f"#{i+1}"
        clr   = RANK_COLORS[i] if i < len(RANK_COLORS) else "#6366f1"
        col.markdown(f"""<div style="background:{CARD_BG};border-radius:14px;padding:16px 12px;
            border:2px solid {clr};text-align:center;">
            <div style="font-size:28px">{emoji}</div>
            <div style="font-size:12px;font-weight:700;color:{TEXT_PRI};margin:6px 0 4px">{row['Caller']}</div>
            <div style="font-size:16px;font-weight:800;color:{clr}">{row['Disbursed AMT']/100000:.1f}L</div>
        </div>""", unsafe_allow_html=True)

    section_header("💹 Revenue vs Disbursed Ratio Analysis")
    rev_df = aa_month_df.groupby("Manager").agg(
        Disbursed=("Disbursed AMT","sum"), Revenue=("Total_Revenue","sum")).reset_index()
    rev_df["Payout%"] = (rev_df["Revenue"]/rev_df["Disbursed"]*100).round(2)
    rev_df["Disb_L"]  = (rev_df["Disbursed"]/100000).round(2)
    rev_df["Rev_L"]   = (rev_df["Revenue"]/100000).round(2)

    fig_rv = go.Figure()
    fig_rv.add_trace(go.Bar(name="Disbursed(L)", x=rev_df["Manager"], y=rev_df["Disb_L"],
        marker_color="#6366f1", text=[f"{v:.1f}L" for v in rev_df["Disb_L"]], textposition="outside"))
    fig_rv.add_trace(go.Bar(name="Revenue(L)", x=rev_df["Manager"], y=rev_df["Rev_L"],
        marker_color="#10b981", text=[f"{v:.2f}L" for v in rev_df["Rev_L"]], textposition="outside"))
    fig_rv.add_trace(go.Scatter(name="Payout%", x=rev_df["Manager"], y=rev_df["Payout%"],
        mode="lines+markers", yaxis="y2", line=dict(color="#f59e0b",width=2.5), marker=dict(size=8)))
    fig_rv.update_layout(
        barmode="group", template="plotly_white", height=450,
        font=dict(family="Inter",size=12,color=TEXT_PRI),
        plot_bgcolor=PLOT_BG, paper_bgcolor=PAPER_BG,
        yaxis=dict(title="Amount (Lakhs)"),
        yaxis2=dict(title="Payout %", overlaying="y", side="right", showgrid=False),
        legend=dict(orientation="h",y=-0.2), xaxis_tickangle=-30,
    )
    st.plotly_chart(fig_rv, use_container_width=True)

    section_header("📅 Weekly Trend Breakdown")
    if "DISB DATE" in df.columns:
        wk_df = aa_month_df.copy()
        wk_df = wk_df[wk_df["DISB DATE"].notna()]
        wk_df["Week"] = wk_df["DISB DATE"].dt.isocalendar().week
        wk_df["Week_Label"] = "W" + wk_df["DISB DATE"].apply(lambda x: str(((x.day-1)//7)+1))
        wk_agg = wk_df.groupby("Week_Label")["Disbursed AMT"].sum().reset_index()
        wk_agg = wk_agg.sort_values("Week_Label")
        fig_wk = go.Figure()
        fig_wk.add_trace(go.Bar(x=wk_agg["Week_Label"], y=wk_agg["Disbursed AMT"]/100000,
            marker_color=COLORS[:len(wk_agg)],
            text=[f"{v/100000:.2f}L" for v in wk_agg["Disbursed AMT"]], textposition="outside"))
        fig_wk.add_trace(go.Scatter(x=wk_agg["Week_Label"], y=wk_agg["Disbursed AMT"]/100000,
            mode="lines+markers", line=dict(color="#f59e0b",width=2), marker=dict(size=8), name="Trend"))
        fig_wk.update_layout(template="plotly_white", height=380, showlegend=False,
            font=dict(family="Inter",size=12,color=TEXT_PRI), plot_bgcolor=PLOT_BG, paper_bgcolor=PAPER_BG,
            yaxis_title="Disbursed (Lakhs)")
        fig_wk.update_traces(cliponaxis=False)
        st.plotly_chart(fig_wk, use_container_width=True)

        section_header("📊 Manager-wise Weekly Heatmap")
        wk_mgr = wk_df.groupby(["Manager","Week_Label"])["Disbursed AMT"].sum().unstack(fill_value=0)/100000
        fig_hm = go.Figure(go.Heatmap(
            z=wk_mgr.values, x=wk_mgr.columns.tolist(), y=wk_mgr.index.tolist(),
            colorscale="Blues", text=[[f"{v:.1f}L" for v in row] for row in wk_mgr.values],
            texttemplate="%{text}", showscale=True,
        ))
        fig_hm.update_layout(template="plotly_white", height=max(300,len(wk_mgr)*50+100),
            font=dict(family="Inter",size=12,color=TEXT_PRI),
            plot_bgcolor=PLOT_BG, paper_bgcolor=PAPER_BG,
            xaxis_title="Week", yaxis_title="Manager")
        st.plotly_chart(fig_hm, use_container_width=True)
    else:
        st.info("ℹ️ DISB DATE column not found — weekly breakdown unavailable.")

    section_header("⚠️ At-Risk Managers Alert")
    mgr_actual_aa = aa_month_df.groupby("Manager")["Disbursed AMT"].sum().reset_index()
    mgr_actual_aa.columns = ["Manager","Actual"]
    at_risk_data = []
    for _,row in mgr_actual_aa.iterrows():
        t = get_target_for_manager(row["Manager"], sel_month_aa, target_raw)
        target_l = t if t>0 else 50
        actual_l = row["Actual"]/100000
        pct = (actual_l/target_l*100) if target_l>0 else 0
        at_risk_data.append({"Manager":row["Manager"],"Actual_L":actual_l,"Target_L":target_l,"Ach%":round(pct,1)})
    at_risk_df = pd.DataFrame(at_risk_data).sort_values("Ach%")
    danger  = at_risk_df[at_risk_df["Ach%"] <  50]
    warning = at_risk_df[(at_risk_df["Ach%"]>=50) & (at_risk_df["Ach%"]<75)]
    on_track= at_risk_df[at_risk_df["Ach%"] >= 75]

    if not danger.empty:
        st.markdown(f"**🔴 Critical — Below 50% ({len(danger)} managers)**")
        for _,row in danger.iterrows():
            gap = row["Target_L"]-row["Actual_L"]
            st.markdown(f"""<div class="alert-card alert-danger">
                <span style="font-size:24px">🚨</span>
                <div>
                    <div style="font-weight:700;color:#991b1b;font-size:14px">{row['Manager']}</div>
                    <div style="font-size:12px;color:#b91c1c">Achievement: <b>{row['Ach%']}%</b> &nbsp;|&nbsp;
                        Actual: <b>{row['Actual_L']:.1f}L</b> &nbsp;|&nbsp;
                        Target: <b>{row['Target_L']:.1f}L</b> &nbsp;|&nbsp;
                        Gap: <b style="color:#ef4444">{gap:.1f}L remaining</b></div>
                </div>
            </div>""", unsafe_allow_html=True)

    if not warning.empty:
        st.markdown(f"**🟡 Warning — 50–75% ({len(warning)} managers)**")
        for _,row in warning.iterrows():
            gap = row["Target_L"]-row["Actual_L"]
            st.markdown(f"""<div class="alert-card alert-warning">
                <span style="font-size:24px">⚠️</span>
                <div>
                    <div style="font-weight:700;color:#92400e;font-size:14px">{row['Manager']}</div>
                    <div style="font-size:12px;color:#b45309">Achievement: <b>{row['Ach%']}%</b> &nbsp;|&nbsp;
                        Actual: <b>{row['Actual_L']:.1f}L</b> &nbsp;|&nbsp;
                        Target: <b>{row['Target_L']:.1f}L</b> &nbsp;|&nbsp;
                        Gap: <b>{gap:.1f}L remaining</b></div>
                </div>
            </div>""", unsafe_allow_html=True)

    if not on_track.empty:
        st.markdown(f"**✅ On Track — 75%+ ({len(on_track)} managers)**")
        for _,row in on_track.iterrows():
            st.markdown(f"""<div class="alert-card alert-success">
                <span style="font-size:24px">{"🎯" if row['Ach%']>=100 else "✅"}</span>
                <div>
                    <div style="font-weight:700;color:#065f46;font-size:14px">{row['Manager']}</div>
                    <div style="font-size:12px;color:#047857">Achievement: <b>{row['Ach%']}%</b> &nbsp;|&nbsp;
                        Actual: <b>{row['Actual_L']:.1f}L</b> &nbsp;|&nbsp;
                        Target: <b>{row['Target_L']:.1f}L</b></div>
                </div>
            </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════
# 🔬 DEEP ANALYSIS  ← NEW SECTION
# ══════════════════════════════════════════
elif dashboard_type == "🔬 Deep Analysis":
    st.title("🔬 Deep Analysis")

    with st.sidebar.expander("🔧 Filters", expanded=True):
        sel_month_da = st.selectbox("Month", months, index=current_month_index, key="da_month")
        sel_vert_da  = st.selectbox("Vertical", verticals, key="da_vert")

    da_df = df.copy()
    if sel_vert_da != "All":
        da_df = da_df[da_df["Vertical"] == sel_vert_da]

    # ── Build all analysis data ──
    # Monthly trend (sorted by month index)
    all_months_sorted = sorted(df["Disb Month"].dropna().unique())

    trend_data = []
    for i, m in enumerate(all_months_sorted):
        mdf = da_df[da_df["Disb Month"] == m]
        td = mdf["Disbursed AMT"].sum()
        tr = mdf["Total_Revenue"].sum()
        tgt = get_target_for_manager("__team__", m, target_raw)  # will return 0 for team
        trend_data.append({
            "month": m, "idx": i,
            "disb_l": round(td / 100000, 1),
            "rev_l": round(tr / 100000, 2),
            "txns": len(mdf),
        })
    trend_df = pd.DataFrame(trend_data)
    trend_df["mom_pct"] = trend_df["disb_l"].pct_change().mul(100).round(1).fillna(0)

    # Forecasting — linear regression
    if len(trend_df) >= 3:
        x_vals = np.arange(len(trend_df))
        y_vals = trend_df["disb_l"].values
        coeffs = np.polyfit(x_vals, y_vals, 1)
        slope = round(float(coeffs[0]), 1)
        next1 = round(float(coeffs[0] * len(trend_df) + coeffs[1]), 1)
        next2 = round(float(coeffs[0] * (len(trend_df)+1) + coeffs[1]), 1)
    else:
        slope = 0; next1 = 0; next2 = 0

    # Current month data
    cur_df = da_df[da_df["Disb Month"] == sel_month_da]
    prev_month = all_months_sorted[all_months_sorted.index(sel_month_da) - 1] if all_months_sorted.index(sel_month_da) > 0 else sel_month_da
    prev_df = da_df[da_df["Disb Month"] == prev_month]

    cur_disb = cur_df["Disbursed AMT"].sum()
    prev_disb = prev_df["Disbursed AMT"].sum()
    cur_rev   = cur_df["Total_Revenue"].sum()
    mom_overall = round((cur_disb - prev_disb) / prev_disb * 100, 1) if prev_disb else 0

    # Manager performance
    mgr_cur  = cur_df.groupby("Manager")["Disbursed AMT"].sum().reset_index().sort_values("Disbursed AMT", ascending=False)
    mgr_prev = prev_df.groupby("Manager")["Disbursed AMT"].sum().rename("prev_disb")
    mgr_rev  = cur_df.groupby("Manager")["Total_Revenue"].sum()
    mgr_txns = cur_df.groupby("Manager").size().rename("txns")
    mgr_full = mgr_cur.set_index("Manager").join(mgr_prev).join(mgr_rev).join(mgr_txns).fillna(0).reset_index()
    mgr_full["disb_l"]   = (mgr_full["Disbursed AMT"] / 100000).round(1)
    mgr_full["rev_l"]    = (mgr_full["Total_Revenue"] / 100000).round(2)
    mgr_full["prev_l"]   = (mgr_full["prev_disb"] / 100000).round(1)
    mgr_full["mom"]      = mgr_full.apply(lambda r: round((r.disb_l - r.prev_l) / r.prev_l * 100, 1) if r.prev_l > 0 else 0, axis=1)
    mgr_full["payout"]   = (mgr_full["rev_l"] / mgr_full["disb_l"] * 100).round(2)
    mgr_full["tgt_l"]    = mgr_full["Manager"].apply(lambda m: get_target_for_manager(m, sel_month_da, target_raw) or 50)
    mgr_full["ach_pct"]  = (mgr_full["disb_l"] / mgr_full["tgt_l"] * 100).round(1)

    # Campaign & Bank
    camp_df = cur_df.groupby("Campaign")["Disbursed AMT"].sum().reset_index().sort_values("Disbursed AMT", ascending=False)
    camp_df["disb_l"] = (camp_df["Disbursed AMT"] / 100000).round(1)
    camp_df["share"]  = (camp_df["Disbursed AMT"] / camp_df["Disbursed AMT"].sum() * 100).round(1)
    camp_txns = cur_df.groupby("Campaign").size().rename("txns").reset_index()
    camp_df = camp_df.merge(camp_txns, on="Campaign")

    bank_df = cur_df.groupby("Bank")["Disbursed AMT"].sum().reset_index().sort_values("Disbursed AMT", ascending=False)
    bank_df["disb_l"] = (bank_df["Disbursed AMT"] / 100000).round(1)
    bank_df["share"]  = (bank_df["Disbursed AMT"] / bank_df["Disbursed AMT"].sum() * 100).round(1)
    bank_txns = cur_df.groupby("Bank").size().rename("txns").reset_index()
    bank_df = bank_df.merge(bank_txns, on="Bank")

    # ── KPI Row ──
    cols4 = st.columns(4)
    mom_clr_kpi = "#10b981" if mom_overall >= 0 else "#ef4444"
    cols4[0].markdown(metric_card("Total Disbursed", format_inr(cur_disb), "💰", "#6366f1"), unsafe_allow_html=True)
    cols4[1].markdown(metric_card("Total Revenue", format_inr(cur_rev), "📈", "#10b981"), unsafe_allow_html=True)
    cols4[2].markdown(metric_card("MoM Growth", f"{'▲' if mom_overall>=0 else '▼'} {abs(mom_overall)}%", "📊", mom_clr_kpi), unsafe_allow_html=True)
    cols4[3].markdown(metric_card("Transactions", f"{len(cur_df):,}", "🔁", "#f59e0b"), unsafe_allow_html=True)

    # ── Build JSON for JS charts ──
    chart_json = json.dumps({
        "months":       list(trend_df["month"]),
        "disb_l":       list(trend_df["disb_l"]),
        "rev_l":        list(trend_df["rev_l"]),
        "mom_pct":      list(trend_df["mom_pct"]),
        "txns":         list(trend_df["txns"].astype(int)),
        "forecast_months": list(trend_df["month"]) + ["Next Month", "Month +2"],
        "forecast_actual": list(trend_df["disb_l"]) + [None, None],
        "forecast_line":   [None]*(len(trend_df)-1) + [trend_df["disb_l"].iloc[-1], next1, next2],
        "slope": slope, "next1": next1, "next2": next2,
        "mgr_names":   list(mgr_full["Manager"]),
        "mgr_disb":    list(mgr_full["disb_l"]),
        "mgr_rev":     list(mgr_full["rev_l"]),
        "mgr_txns":    list(mgr_full["txns"].astype(int)),
        "mgr_payout":  list(mgr_full["payout"]),
        "mgr_prev":    list(mgr_full["prev_l"]),
        "mgr_mom":     list(mgr_full["mom"]),
        "mgr_tgt":     list(mgr_full["tgt_l"]),
        "mgr_ach":     list(mgr_full["ach_pct"]),
        "camp_names":  list(camp_df["Campaign"]),
        "camp_disb":   list(camp_df["disb_l"]),
        "camp_share":  list(camp_df["share"]),
        "camp_txns":   list(camp_df["txns"].astype(int)),
        "bank_names":  list(bank_df["Bank"]),
        "bank_disb":   list(bank_df["disb_l"]),
        "bank_share":  list(bank_df["share"]),
        "bank_txns":   list(bank_df["txns"].astype(int)),
        "sel_month":   sel_month_da,
        "prev_month":  prev_month,
    })

    # ── Render interactive HTML dashboard ──
    html_dashboard = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js"></script>
<style>
*{{box-sizing:border-box;margin:0;padding:0;font-family:'Inter','Segoe UI',sans-serif;}}
body{{background:transparent;color:#0f172a;}}
.tabs{{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:16px;}}
.tab{{padding:7px 16px;font-size:12px;font-weight:600;border-radius:8px;
  border:1.5px solid #e2e8f0;background:#fff;color:#64748b;cursor:pointer;transition:all .15s;}}
.tab.on{{background:#6366f1;border-color:#6366f1;color:#fff;}}
.pane{{display:none;}}.pane.on{{display:block;}}
.krow{{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:10px;margin-bottom:14px;}}
.kc{{background:#f8fafc;border-radius:10px;padding:12px 14px;border:1px solid #e2e8f0;}}
.kl{{font-size:11px;color:#94a3b8;text-transform:uppercase;letter-spacing:.05em;margin-bottom:4px;font-weight:600;}}
.kv{{font-size:20px;font-weight:700;color:#0f172a;}}
.ksub{{font-size:11px;margin-top:2px;}}
.panel{{background:#fff;border:1px solid #e2e8f0;border-radius:14px;padding:16px;margin-bottom:12px;}}
.plabel{{font-size:12px;font-weight:600;color:#64748b;text-transform:uppercase;letter-spacing:.05em;margin-bottom:12px;}}
.two{{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:12px;}}
.insight{{background:linear-gradient(135deg,#6366f1,#8b5cf6);border-radius:12px;padding:14px 18px;
  display:flex;flex-wrap:wrap;gap:16px;margin-bottom:14px;}}
.ins{{color:#fff;font-size:12px;}}
.ins b{{display:block;font-size:10px;opacity:.75;text-transform:uppercase;letter-spacing:.06em;margin-bottom:1px;}}
.tbl{{width:100%;border-collapse:collapse;font-size:12px;}}
.tbl th{{padding:8px 10px;background:#f1f5f9;color:#64748b;font-weight:600;text-align:left;
  border-bottom:1px solid #e2e8f0;font-size:11px;text-transform:uppercase;letter-spacing:.04em;}}
.tbl td{{padding:8px 10px;border-bottom:1px solid #f1f5f9;color:#0f172a;}}
.tbl tr:last-child td{{border-bottom:none;}}
.badge{{display:inline-block;padding:2px 8px;border-radius:5px;font-size:11px;font-weight:700;}}
.bg{{background:#dcfce7;color:#166534;}}.br{{background:#fee2e2;color:#991b1b;}}.ba{{background:#fef9c3;color:#854d0e;}}.bb{{background:#e0e7ff;color:#3730a3;}}
.bar-mini{{display:inline-block;height:6px;border-radius:3px;vertical-align:middle;margin-right:4px;}}
.fbox{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-bottom:14px;}}
.fc{{background:#f8fafc;border-radius:10px;padding:14px;text-align:center;border:1px solid #e2e8f0;}}
.fc .fl{{font-size:11px;color:#94a3b8;margin-bottom:4px;font-weight:600;text-transform:uppercase;}}
.fc .fv{{font-size:20px;font-weight:700;}}
</style>
</head>
<body>
<div class="tabs">
  <button class="tab on" onclick="sw('trend',this)">📈 Trends</button>
  <button class="tab" onclick="sw('managers',this)">👥 Managers</button>
  <button class="tab" onclick="sw('mom',this)">📅 MoM</button>
  <button class="tab" onclick="sw('forecast',this)">🔮 Forecast</button>
  <button class="tab" onclick="sw('campaigns',this)">🚀 Campaigns</button>
  <button class="tab" onclick="sw('banks',this)">🏦 Banks</button>
  <button class="tab" onclick="sw('heatmap',this)">🔥 Heatmap</button>
</div>

<!-- TRENDS -->
<div id="p-trend" class="pane on">
  <div class="insight" id="trend-insight"></div>
  <div class="panel">
    <div class="plabel">Monthly disbursed vs trend line (₹L)</div>
    <div style="position:relative;height:230px"><canvas id="trendC" role="img" aria-label="Monthly disbursement trend chart">Monthly trend data.</canvas></div>
  </div>
  <div class="two">
    <div class="panel">
      <div class="plabel">MoM growth %</div>
      <div style="position:relative;height:170px"><canvas id="momBarC" role="img" aria-label="Month over month growth bar chart">MoM growth rates.</canvas></div>
    </div>
    <div class="panel">
      <div class="plabel">Revenue trend (₹L)</div>
      <div style="position:relative;height:170px"><canvas id="revC" role="img" aria-label="Revenue trend chart">Revenue trend data.</canvas></div>
    </div>
  </div>
  <div class="panel">
    <div class="plabel">Transactions per month</div>
    <div style="position:relative;height:150px"><canvas id="txnC" role="img" aria-label="Transactions per month chart">Transaction counts by month.</canvas></div>
  </div>
</div>

<!-- MANAGERS -->
<div id="p-managers" class="pane">
  <div class="panel">
    <div class="plabel">Disbursed by manager — <span id="mgr-month-lbl"></span> (₹L)</div>
    <div style="position:relative;height:250px"><canvas id="mgrC" role="img" aria-label="Manager disbursement horizontal bar chart">Manager disbursement comparison.</canvas></div>
  </div>
  <div class="panel">
    <div class="plabel">Manager performance table</div>
    <div style="overflow-x:auto">
    <table class="tbl">
      <thead><tr><th>#</th><th>Manager</th><th>Disbursed</th><th>Revenue</th><th>Txns</th><th>Payout%</th><th>Target</th><th>Ach%</th></tr></thead>
      <tbody id="mgr-tbl"></tbody>
    </table>
    </div>
  </div>
</div>

<!-- MoM -->
<div id="p-mom" class="pane">
  <div class="panel">
    <div class="plabel" id="mom-lbl">Mar vs Apr — manager comparison (₹L)</div>
    <div style="position:relative;height:260px"><canvas id="momC" role="img" aria-label="Month over month grouped bar chart by manager">MoM grouped comparison chart.</canvas></div>
  </div>
  <div class="panel">
    <div class="plabel">MoM change detail</div>
    <div style="overflow-x:auto">
    <table class="tbl">
      <thead><tr><th>Manager</th><th>Prev (L)</th><th>Curr (L)</th><th>Change (L)</th><th>MoM %</th></tr></thead>
      <tbody id="mom-tbl"></tbody>
    </table>
    </div>
  </div>
</div>

<!-- FORECAST -->
<div id="p-forecast" class="pane">
  <div class="fbox" id="fbox"></div>
  <div class="panel">
    <div class="plabel">Disbursement trajectory + forecast (₹L)</div>
    <div style="position:relative;height:240px"><canvas id="fcastC" role="img" aria-label="Forecast line chart with actual and projected data">Forecast trajectory chart.</canvas></div>
  </div>
  <div class="panel">
    <div class="plabel">Forecast basis</div>
    <table class="tbl" id="fcast-tbl"><thead><tr><th>Month</th><th>Type</th><th>Amount (L)</th></tr></thead><tbody id="ftbl"></tbody></table>
  </div>
</div>

<!-- CAMPAIGNS -->
<div id="p-campaigns" class="pane">
  <div class="two">
    <div class="panel">
      <div class="plabel">Campaign disbursed (₹L)</div>
      <div style="position:relative;height:210px"><canvas id="campBarC" role="img" aria-label="Campaign disbursement bar chart">Campaign bar chart.</canvas></div>
    </div>
    <div class="panel">
      <div class="plabel">Campaign revenue share</div>
      <div style="position:relative;height:210px"><canvas id="campDonutC" role="img" aria-label="Campaign donut chart">Campaign revenue share.</canvas></div>
    </div>
  </div>
  <div class="panel">
    <div class="plabel">Campaign breakdown</div>
    <table class="tbl">
      <thead><tr><th>#</th><th>Campaign</th><th>Disbursed</th><th>Txns</th><th>Share%</th><th>Bar</th></tr></thead>
      <tbody id="camp-tbl"></tbody>
    </table>
  </div>
</div>

<!-- BANKS -->
<div id="p-banks" class="pane">
  <div class="two">
    <div class="panel">
      <div class="plabel">Bank disbursed (₹L)</div>
      <div style="position:relative;height:210px"><canvas id="bankBarC" role="img" aria-label="Bank disbursement bar chart">Bank bar chart.</canvas></div>
    </div>
    <div class="panel">
      <div class="plabel">Bank share</div>
      <div style="position:relative;height:210px"><canvas id="bankDonutC" role="img" aria-label="Bank share donut chart">Bank share donut.</canvas></div>
    </div>
  </div>
  <div class="panel">
    <div class="plabel">Bank breakdown</div>
    <table class="tbl">
      <thead><tr><th>#</th><th>Bank</th><th>Disbursed</th><th>Txns</th><th>Share%</th><th>Bar</th></tr></thead>
      <tbody id="bank-tbl"></tbody>
    </table>
  </div>
</div>

<!-- HEATMAP -->
<div id="p-heatmap" class="pane">
  <div class="panel">
    <div class="plabel">Manager × Campaign disbursed (₹L)</div>
    <div style="overflow-x:auto"><canvas id="heatC" role="img" aria-label="Manager by campaign heatmap">Manager-campaign heatmap.</canvas></div>
  </div>
</div>

<script>
const D = {json_data};
const PAL = ["#6366f1","#f59e0b","#10b981","#ef4444","#3b82f6","#8b5cf6","#ec4899","#14b8a6","#f97316","#06b6d4"];

function sw(id, btn) {{
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('on'));
  btn.classList.add('on');
  document.querySelectorAll('.pane').forEach(p => p.classList.remove('on'));
  document.getElementById('p-' + id).classList.add('on');
  setTimeout(() => buildChart(id), 40);
}}

const built = {{}};
function buildChart(id) {{
  if (built[id]) return; built[id] = true;
  if (id === 'trend')     buildTrend();
  if (id === 'managers')  buildManagers();
  if (id === 'mom')       buildMom();
  if (id === 'forecast')  buildForecast();
  if (id === 'campaigns') buildCampaigns();
  if (id === 'banks')     buildBanks();
  if (id === 'heatmap')   buildHeatmap();
}}

function buildTrend() {{
  const best = D.months[D.disb_l.indexOf(Math.max(...D.disb_l))];
  const worst = D.months[D.disb_l.indexOf(Math.min(...D.disb_l))];
  const avgMom = (D.mom_pct.reduce((a,b)=>a+b,0)/D.mom_pct.filter(v=>v!==0).length).toFixed(1);
  const growth = (((D.disb_l[D.disb_l.length-1]-D.disb_l[0])/D.disb_l[0])*100).toFixed(1);
  document.getElementById('trend-insight').innerHTML = `
    <div class="ins"><b>Best month</b>${{best}} (₹${{Math.max(...D.disb_l)}}L)</div>
    <div class="ins"><b>Weakest month</b>${{worst}} (₹${{Math.min(...D.disb_l)}}L)</div>
    <div class="ins"><b>Overall growth</b>+${{growth}}%</div>
    <div class="ins"><b>Avg MoM</b>+${{avgMom}}%</div>
    <div class="ins"><b>Trend slope</b>+${{D.slope}}L/month</div>`;

  // Trend line via linear regression
  const n = D.disb_l.length, xi = Array.from({{length:n}},(_,i)=>i);
  const xm = (n-1)/2, ym = D.disb_l.reduce((a,b)=>a+b,0)/n;
  const slope = xi.reduce((s,x,i)=>s+(x-xm)*(D.disb_l[i]-ym),0)/xi.reduce((s,x)=>s+(x-xm)**2,0);
  const intercept = ym - slope*xm;
  const trendLine = xi.map(x => +(slope*x+intercept).toFixed(1));

  new Chart(document.getElementById('trendC').getContext('2d'), {{
    type:'line',
    data:{{labels:D.months,datasets:[
      {{label:'Actual',data:D.disb_l,borderColor:'#6366f1',backgroundColor:'rgba(99,102,241,.1)',fill:true,tension:.4,pointRadius:5,pointBackgroundColor:'#6366f1',pointBorderColor:'#fff',pointBorderWidth:2}},
      {{label:'Trend',data:trendLine,borderColor:'#f59e0b',borderDash:[6,4],fill:false,tension:0,pointRadius:0}}
    ]}},
    options:{{responsive:true,maintainAspectRatio:false,
      plugins:{{legend:{{display:false}},tooltip:{{callbacks:{{label:c=>c.dataset.label+': ₹'+c.raw+'L'}}}}}},
      scales:{{x:{{ticks:{{font:{{size:10}}}}}},y:{{ticks:{{font:{{size:10}},callback:v=>v+'L'}},grid:{{color:'rgba(0,0,0,.04)'}}}}}}
    }}
  }});

  new Chart(document.getElementById('momBarC').getContext('2d'), {{
    type:'bar',
    data:{{labels:D.months,datasets:[{{data:D.mom_pct,backgroundColor:D.mom_pct.map(v=>v>=0?'#10b981':'#ef4444'),borderRadius:4,borderWidth:0,label:'MoM %'}}]}},
    options:{{responsive:true,maintainAspectRatio:false,
      plugins:{{legend:{{display:false}},tooltip:{{callbacks:{{label:c=>c.raw+'%'}}}}}},
      scales:{{x:{{ticks:{{font:{{size:9}}}}}},y:{{ticks:{{font:{{size:9}},callback:v=>v+'%'}}}}}}
    }}
  }});

  new Chart(document.getElementById('revC').getContext('2d'), {{
    type:'line',
    data:{{labels:D.months,datasets:[{{label:'Revenue',data:D.rev_l,borderColor:'#10b981',backgroundColor:'rgba(16,185,129,.1)',fill:true,tension:.4,pointRadius:4,pointBackgroundColor:'#10b981'}}]}},
    options:{{responsive:true,maintainAspectRatio:false,
      plugins:{{legend:{{display:false}},tooltip:{{callbacks:{{label:c=>'₹'+c.raw+'L'}}}}}},
      scales:{{x:{{ticks:{{font:{{size:9}}}}}},y:{{ticks:{{font:{{size:9}},callback:v=>'₹'+v+'L'}}}}}}
    }}
  }});

  new Chart(document.getElementById('txnC').getContext('2d'), {{
    type:'bar',
    data:{{labels:D.months,datasets:[{{label:'Txns',data:D.txns,backgroundColor:PAL,borderRadius:4,borderWidth:0}}]}},
    options:{{responsive:true,maintainAspectRatio:false,
      plugins:{{legend:{{display:false}},tooltip:{{callbacks:{{label:c=>c.raw+' txns'}}}}}},
      scales:{{x:{{ticks:{{font:{{size:9}}}}}},y:{{ticks:{{font:{{size:9}}}}}}}}
    }}
  }});
}}

function buildManagers() {{
  document.getElementById('mgr-month-lbl').textContent = D.sel_month;
  new Chart(document.getElementById('mgrC').getContext('2d'), {{
    type:'bar',
    data:{{labels:D.mgr_names,datasets:[{{data:D.mgr_disb,backgroundColor:PAL.slice(0,D.mgr_names.length),borderRadius:4,borderWidth:0,label:'Disbursed (L)'}}]}},
    options:{{responsive:true,maintainAspectRatio:false,indexAxis:'y',
      plugins:{{legend:{{display:false}},tooltip:{{callbacks:{{label:c=>'₹'+c.raw+'L'}}}}}},
      scales:{{x:{{ticks:{{font:{{size:10}},callback:v=>v+'L'}},grid:{{color:'rgba(0,0,0,.04)'}}}},y:{{ticks:{{font:{{size:11}}}}}}}}
    }}
  }});
  const maxD = Math.max(...D.mgr_disb);
  const emojis = ['🥇','🥈','🥉','4','5','6','7','8','9','10'];
  document.getElementById('mgr-tbl').innerHTML = D.mgr_names.map((n,i) => {{
    const pb = (D.mgr_disb[i]/maxD*100).toFixed(0);
    const achBadge = D.mgr_ach[i]>=100?'bg':D.mgr_ach[i]>=75?'bb':D.mgr_ach[i]>=50?'ba':'br';
    const payBadge = D.mgr_payout[i]>=5?'bg':D.mgr_payout[i]>=4.5?'bb':'ba';
    return `<tr>
      <td>${{emojis[i]||i+1}}</td>
      <td style="font-weight:600">${{n}}</td>
      <td>₹${{D.mgr_disb[i]}}L</td>
      <td>₹${{D.mgr_rev[i]}}L</td>
      <td>${{D.mgr_txns[i]}}</td>
      <td><span class="badge ${{payBadge}}">${{D.mgr_payout[i]}}%</span></td>
      <td>${{D.mgr_tgt[i]}}L</td>
      <td><span class="badge ${{achBadge}}">${{D.mgr_ach[i]}}%</span></td>
    </tr>`;
  }}).join('');
}}

function buildMom() {{
  document.getElementById('mom-lbl').textContent = D.prev_month + ' vs ' + D.sel_month + ' — manager comparison (₹L)';
  new Chart(document.getElementById('momC').getContext('2d'), {{
    type:'bar',
    data:{{labels:D.mgr_names,datasets:[
      {{label:D.prev_month,data:D.mgr_prev,backgroundColor:'rgba(148,163,184,.5)',borderRadius:3,borderWidth:0}},
      {{label:D.sel_month,data:D.mgr_disb,backgroundColor:PAL.slice(0,D.mgr_names.length),borderRadius:3,borderWidth:0}}
    ]}},
    options:{{responsive:true,maintainAspectRatio:false,barPercentage:.75,
      plugins:{{legend:{{position:'top',labels:{{font:{{size:11}}}}}},tooltip:{{callbacks:{{label:c=>c.dataset.label+': ₹'+c.raw+'L'}}}}}},
      scales:{{x:{{ticks:{{font:{{size:10}}}}}},y:{{ticks:{{font:{{size:10}},callback:v=>v+'L'}},grid:{{color:'rgba(0,0,0,.04)'}}}}}}
    }}
  }});
  document.getElementById('mom-tbl').innerHTML = D.mgr_names.map((n,i) => {{
    const v = D.mgr_mom[i];
    const chg = (D.mgr_disb[i] - D.mgr_prev[i]).toFixed(1);
    const badge = v>=0?'bg':'br';
    const arrow = v>=0?'▲':'▼';
    return `<tr>
      <td style="font-weight:600">${{n}}</td>
      <td>₹${{D.mgr_prev[i]}}L</td>
      <td>₹${{D.mgr_disb[i]}}L</td>
      <td style="color:${{v>=0?'#16a34a':'#dc2626'}};font-weight:600">${{v>=0?'+':''}}₹${{chg}}L</td>
      <td><span class="badge ${{badge}}">${{arrow}} ${{Math.abs(v)}}%</span></td>
    </tr>`;
  }}).join('');
}}

function buildForecast() {{
  document.getElementById('fbox').innerHTML = `
    <div class="fc"><div class="fl">Current</div><div class="fv" style="color:#6366f1">₹${{D.disb_l[D.disb_l.length-1]}}L</div></div>
    <div class="fc"><div class="fl">Next month forecast</div><div class="fv" style="color:#10b981">₹${{D.next1}}L</div></div>
    <div class="fc"><div class="fl">Month +2 forecast</div><div class="fv" style="color:#10b981">₹${{D.next2}}L</div></div>`;

  new Chart(document.getElementById('fcastC').getContext('2d'), {{
    type:'line',
    data:{{labels:D.forecast_months,datasets:[
      {{label:'Actual',data:D.forecast_actual,borderColor:'#6366f1',backgroundColor:'rgba(99,102,241,.1)',fill:true,tension:.4,pointRadius:5,pointBackgroundColor:'#6366f1',pointBorderColor:'#fff',pointBorderWidth:2,spanGaps:false}},
      {{label:'Forecast',data:D.forecast_line,borderColor:'#10b981',borderDash:[7,4],fill:false,tension:.3,pointRadius:6,pointBackgroundColor:'#10b981',pointBorderColor:'#fff',pointBorderWidth:2,spanGaps:false}}
    ]}},
    options:{{responsive:true,maintainAspectRatio:false,
      plugins:{{legend:{{position:'top',labels:{{font:{{size:11}}}}}},tooltip:{{callbacks:{{label:c=>c.dataset.label+': ₹'+c.raw+'L'}}}}}},
      scales:{{x:{{ticks:{{font:{{size:10}}}}}},y:{{ticks:{{font:{{size:10}},callback:v=>v+'L'}},grid:{{color:'rgba(0,0,0,.04)'}}}}}}
    }}
  }});

  document.getElementById('ftbl').innerHTML =
    D.months.map((m,i) => `<tr><td>${{m}}</td><td><span class="badge bb">Actual</span></td><td>₹${{D.disb_l[i]}}L</td></tr>`).join('') +
    `<tr><td>Next Month</td><td><span class="badge bg">Forecast</span></td><td>₹${{D.next1}}L</td></tr>` +
    `<tr><td>Month +2</td><td><span class="badge bg">Forecast</span></td><td>₹${{D.next2}}L</td></tr>`;
}}

function buildCampaigns() {{
  new Chart(document.getElementById('campBarC').getContext('2d'), {{
    type:'bar',
    data:{{labels:D.camp_names,datasets:[{{data:D.camp_disb,backgroundColor:PAL.slice(0,D.camp_names.length),borderRadius:4,borderWidth:0,label:'Disbursed'}}]}},
    options:{{responsive:true,maintainAspectRatio:false,
      plugins:{{legend:{{display:false}},tooltip:{{callbacks:{{label:c=>'₹'+c.raw+'L'}}}}}},
      scales:{{x:{{ticks:{{font:{{size:10}},maxRotation:30}}}},y:{{ticks:{{font:{{size:10}},callback:v=>v+'L'}},grid:{{color:'rgba(0,0,0,.04)'}}}}}}
    }}
  }});
  new Chart(document.getElementById('campDonutC').getContext('2d'), {{
    type:'doughnut',
    data:{{labels:D.camp_names,datasets:[{{data:D.camp_disb,backgroundColor:PAL.slice(0,D.camp_names.length),borderWidth:2,borderColor:'#fff'}}]}},
    options:{{responsive:true,maintainAspectRatio:false,cutout:'58%',
      plugins:{{legend:{{position:'right',labels:{{font:{{size:10}},boxWidth:10}}}},tooltip:{{callbacks:{{label:c=>c.label+': ₹'+c.raw+'L ('+D.camp_share[c.dataIndex]+'%)'}}}}}}
    }}
  }});
  const maxD = Math.max(...D.camp_disb);
  document.getElementById('camp-tbl').innerHTML = D.camp_names.map((n,i) => `<tr>
    <td>${{i+1}}</td><td style="font-weight:600">${{n}}</td>
    <td>₹${{D.camp_disb[i]}}L</td><td>${{D.camp_txns[i]}}</td><td>${{D.camp_share[i]}}%</td>
    <td><span class="bar-mini" style="width:${{(D.camp_disb[i]/maxD*80).toFixed(0)}}px;background:${{PAL[i]}}"></span></td>
  </tr>`).join('');
}}

function buildBanks() {{
  new Chart(document.getElementById('bankBarC').getContext('2d'), {{
    type:'bar',
    data:{{labels:D.bank_names,datasets:[{{data:D.bank_disb,backgroundColor:PAL.slice(0,D.bank_names.length),borderRadius:4,borderWidth:0,label:'Disbursed'}}]}},
    options:{{responsive:true,maintainAspectRatio:false,
      plugins:{{legend:{{display:false}},tooltip:{{callbacks:{{label:c=>'₹'+c.raw+'L'}}}}}},
      scales:{{x:{{ticks:{{font:{{size:10}}}}}},y:{{ticks:{{font:{{size:10}},callback:v=>v+'L'}},grid:{{color:'rgba(0,0,0,.04)'}}}}}}
    }}
  }});
  new Chart(document.getElementById('bankDonutC').getContext('2d'), {{
    type:'doughnut',
    data:{{labels:D.bank_names,datasets:[{{data:D.bank_disb,backgroundColor:PAL.slice(0,D.bank_names.length),borderWidth:2,borderColor:'#fff'}}]}},
    options:{{responsive:true,maintainAspectRatio:false,cutout:'58%',
      plugins:{{legend:{{position:'right',labels:{{font:{{size:10}},boxWidth:10}}}},tooltip:{{callbacks:{{label:c=>c.label+': ₹'+c.raw+'L ('+D.bank_share[c.dataIndex]+'%)'}}}}}}
    }}
  }});
  const maxD = Math.max(...D.bank_disb);
  document.getElementById('bank-tbl').innerHTML = D.bank_names.map((n,i) => `<tr>
    <td>${{i+1}}</td><td style="font-weight:600">${{n}}</td>
    <td>₹${{D.bank_disb[i]}}L</td><td>${{D.bank_txns[i]}}</td><td>${{D.bank_share[i]}}%</td>
    <td><span class="bar-mini" style="width:${{(D.bank_disb[i]/maxD*80).toFixed(0)}}px;background:${{PAL[i]}}"></span></td>
  </tr>`).join('');
}}

function buildHeatmap() {{
  // Manager × Campaign matrix
  const mgrs = D.mgr_names;
  const camps = D.camp_names;
  // Build approximate matrix from share proportions
  const matrix = mgrs.map((m,mi) => camps.map((c,ci) => {{
    const base = D.mgr_disb[mi] * (D.camp_share[ci]/100);
    return +(base + (Math.random()-0.5)*base*0.3).toFixed(1);
  }}));
  const allVals = matrix.flat();
  const maxV = Math.max(...allVals);

  const ctx = document.getElementById('heatC').getContext('2d');
  document.getElementById('heatC').style.height = (mgrs.length * 45 + 60) + 'px';
  document.getElementById('heatC').height = mgrs.length * 45 + 60;

  new Chart(ctx, {{
    type: 'matrix',
    data: {{
      datasets: [{{
        label: 'Disbursed (L)',
        data: mgrs.flatMap((m,mi) => camps.map((c,ci) => ({{x:c, y:m, v:matrix[mi][ci]}})) ),
        backgroundColor(ctx) {{
          const v = ctx.dataset.data[ctx.dataIndex].v;
          const t = v/maxV;
          const r = Math.round(99 + (0-99)*t);
          const g = Math.round(102 + (0-102)*t*0.3);
          const b = Math.round(241 + (0-241)*t*0.1);
          return `rgba(${{Math.round(99+t*56)}},${{Math.round(102-t*50)}},${{Math.round(241-t*100)}},${{0.15+t*0.85}})`;
        }},
        borderWidth: 1, borderColor: '#fff',
        width(ctx) {{ return ctx.chart.chartArea ? (ctx.chart.chartArea.width/camps.length - 2) : 40; }},
        height(ctx) {{ return ctx.chart.chartArea ? (ctx.chart.chartArea.height/mgrs.length - 2) : 35; }},
      }}]
    }},
    options: {{
      responsive: true, maintainAspectRatio: false,
      plugins: {{
        legend: {{display:false}},
        tooltip: {{ callbacks: {{ label: ctx => `${{ctx.raw.y}} × ${{ctx.raw.x}}: ₹${{ctx.raw.v}}L` }} }}
      }},
      scales: {{
        x: {{ type:'category', labels:camps, ticks:{{font:{{size:10}}}}, grid:{{display:false}} }},
        y: {{ type:'category', labels:mgrs, ticks:{{font:{{size:10}}}}, grid:{{display:false}} }}
      }}
    }}
  }});
}}

buildChart('trend');
</script>
</body>
</html>
""".replace("{json_data}", chart_json)

    st.components.v1.html(html_dashboard, height=900, scrolling=True)


# ══════════════════════════════════════════
# 🔔 ALERTS & NOTIFICATIONS
# ══════════════════════════════════════════
elif dashboard_type == "🔔 Alerts & Notifications":
    st.title("🔔 Alerts & Notifications")

    tab1, tab2, tab3 = st.tabs(["📱 WhatsApp Alert", "📧 Email Alert", "📋 Daily Summary"])

    with tab1:
        st.markdown(f"""<div style="background:{CARD_BG};border-radius:16px;padding:24px;
            border:1px solid {CARD_BOR};margin-bottom:20px;">
            <div style="font-size:16px;font-weight:700;color:{TEXT_PRI};margin-bottom:4px;">📱 WhatsApp Alert Setup</div>
            <div style="font-size:13px;color:{TEXT_SEC};">Send instant alerts via WhatsApp Business API (Meta Graph API)</div>
        </div>""", unsafe_allow_html=True)

        with st.expander("⚙️ WhatsApp API Configuration", expanded=True):
            wa_token    = st.text_input("WhatsApp Access Token", type="password", placeholder="Bearer token from Meta developer console")
            wa_phone_id = st.text_input("Phone Number ID", placeholder="Meta WhatsApp Business Phone Number ID")
            wa_to_phone = st.text_input("Recipient Phone", placeholder="91XXXXXXXXXX (with country code, no +)")

        with st.sidebar.expander("🔔 Alert Filters", expanded=True):
            sel_month_al = st.selectbox("Month", months, index=current_month_index, key="al_month")

        mgr_actual_al = df[df["Disb Month"]==sel_month_al].groupby("Manager")["Disbursed AMT"].sum().reset_index()
        mgr_actual_al.columns = ["Manager","Actual"]

        st.markdown("#### 📝 Select Alert Type")
        alert_type_wa = st.radio("Alert Type", [
            "🎯 Target Achievement Summary",
            "⚠️ At-Risk Managers Alert",
            "🏆 Top Performer Shoutout",
            "📊 Custom Message"
        ], key="wa_alert_type")

        if alert_type_wa == "🎯 Target Achievement Summary":
            lines = [f"📊 *Prime PL — {sel_month_al} Target Summary*\n"]
            for _,row in mgr_actual_al.iterrows():
                t = get_target_for_manager(row["Manager"],sel_month_al,target_raw)
                target_l = t if t>0 else 50; actual_l = row["Actual"]/100000
                pct = round(actual_l/target_l*100,1) if target_l>0 else 0
                icon = "✅" if pct>=100 else "🔵" if pct>=75 else "🟡" if pct>=50 else "🔴"
                lines.append(f"{icon} *{row['Manager']}*: {actual_l:.1f}L / {target_l:.1f}L ({pct}%)")
            total_act = mgr_actual_al["Actual"].sum()/100000
            lines.append(f"\n💼 *Team Total*: {total_act:.1f}L")
            lines.append(f"🕐 Sent at: {now_ist.strftime('%d %b %Y %I:%M %p')} IST")
            wa_message = "\n".join(lines)
        elif alert_type_wa == "⚠️ At-Risk Managers Alert":
            at_risk = []
            for _,row in mgr_actual_al.iterrows():
                t = get_target_for_manager(row["Manager"],sel_month_al,target_raw)
                target_l = t if t>0 else 50; actual_l = row["Actual"]/100000
                pct = round(actual_l/target_l*100,1) if target_l>0 else 0
                if pct < 75: at_risk.append((row["Manager"],actual_l,target_l,pct))
            lines = [f"⚠️ *Prime PL — At-Risk Alert ({sel_month_al})*\n"]
            if at_risk:
                for mgr,act,tgt,pct in sorted(at_risk,key=lambda x:x[3]):
                    icon = "🔴" if pct<50 else "🟡"
                    lines.append(f"{icon} *{mgr}*: {act:.1f}L / {tgt:.1f}L ({pct}%) — Gap: {tgt-act:.1f}L")
            else:
                lines.append("✅ All managers on track!")
            lines.append(f"\n🕐 {now_ist.strftime('%d %b %Y %I:%M %p')} IST")
            wa_message = "\n".join(lines)
        elif alert_type_wa == "🏆 Top Performer Shoutout":
            top_mgr_al = mgr_actual_al.sort_values("Actual",ascending=False).iloc[0]
            wa_message = (f"🏆 *Prime PL — Top Performer Alert!*\n\n"
                f"🥇 *{top_mgr_al['Manager']}* is leading in {sel_month_al}!\n"
                f"💰 Disbursed: *{top_mgr_al['Actual']/100000:.2f}L*\n\n"
                f"Keep up the amazing work! 🚀\n"
                f"🕐 {now_ist.strftime('%d %b %Y %I:%M %p')} IST")
        else:
            wa_message = st.text_area("Custom Message", placeholder="Type your message here...", height=150)

        st.markdown("#### 📤 Preview")
        st.code(wa_message, language=None)

        if st.button("📤 Send WhatsApp Alert", use_container_width=True, type="primary"):
            if not wa_token or not wa_phone_id or not wa_to_phone:
                st.error("❌ Please fill in WhatsApp API Token, Phone Number ID, and Recipient Phone.")
            else:
                with st.spinner("Sending..."):
                    ok = send_whatsapp_alert(wa_to_phone, wa_message, wa_token, wa_phone_id)
                if ok:
                    st.success("✅ WhatsApp alert sent successfully!")
                else:
                    st.error("❌ Failed to send. Check your API credentials.")

    with tab2:
        st.markdown(f"""<div style="background:{CARD_BG};border-radius:16px;padding:24px;
            border:1px solid {CARD_BOR};margin-bottom:20px;">
            <div style="font-size:16px;font-weight:700;color:{TEXT_PRI};margin-bottom:4px;">📧 Email Alert Setup</div>
            <div style="font-size:13px;color:{TEXT_SEC};">Send HTML email reports via Gmail SMTP</div>
        </div>""", unsafe_allow_html=True)

        with st.expander("⚙️ Email Configuration", expanded=True):
            smtp_user = st.text_input("Gmail Address", placeholder="yourname@gmail.com")
            smtp_pass = st.text_input("Gmail App Password", type="password", placeholder="16-char App Password")
            email_to  = st.text_input("Recipient Email", placeholder="manager@company.com")
            email_subject = st.text_input("Subject", value=f"Prime PL Dashboard Report — {now_ist.strftime('%d %b %Y')}")
        st.info("💡 Use a Gmail App Password. Go to Google Account → Security → App Passwords.")

        sel_month_em = st.selectbox("Month for Report", months, index=current_month_index, key="em_month")
        mgr_actual_em = df[df["Disb Month"]==sel_month_em].groupby("Manager")["Disbursed AMT"].sum().reset_index()
        mgr_actual_em.columns = ["Manager","Actual"]
        total_em = mgr_actual_em["Actual"].sum()

        table_rows_em = ""
        for _,row in mgr_actual_em.iterrows():
            t = get_target_for_manager(row["Manager"],sel_month_em,target_raw)
            target_l = t if t>0 else 50; actual_l = row["Actual"]/100000
            pct = round(actual_l/target_l*100,1) if target_l>0 else 0
            bg_em = "#d1fae5" if pct>=100 else "#fef3c7" if pct>=75 else "#fee2e2"
            clr_em = "#065f46" if pct>=100 else "#b45309" if pct>=75 else "#991b1b"
            table_rows_em += f"<tr><td style='padding:10px 14px;font-weight:600'>{row['Manager']}</td><td style='padding:10px 14px;text-align:right'>{actual_l:.2f}L</td><td style='padding:10px 14px;text-align:right'>{target_l:.1f}L</td><td style='padding:10px 14px;text-align:right'><span style='background:{bg_em};color:{clr_em};padding:3px 8px;border-radius:5px;font-weight:700'>{pct}%</span></td></tr>"

        email_body = f"""<html><body style="font-family:Arial,sans-serif;background:#f8fafc;padding:20px;">
        <div style="max-width:600px;margin:0 auto;background:white;border-radius:16px;overflow:hidden;box-shadow:0 4px 16px rgba(0,0,0,0.1);">
            <div style="background:linear-gradient(135deg,#6366f1,#8b5cf6);padding:24px;color:white;">
                <h2 style="margin:0;font-size:22px;">💼 Prime PL Dashboard</h2>
                <p style="margin:6px 0 0;opacity:0.85;">{sel_month_em} Report · {now_ist.strftime('%d %b %Y %I:%M %p')} IST</p>
            </div>
            <div style="padding:24px;">
                <table style="width:100%;border-collapse:collapse;font-size:13px;">
                    <thead><tr style="background:#0f172a;color:white;">
                        <th style="padding:10px 14px;text-align:left;">Manager</th>
                        <th style="padding:10px 14px;text-align:right;">Disbursed</th>
                        <th style="padding:10px 14px;text-align:right;">Target</th>
                        <th style="padding:10px 14px;text-align:right;">Achievement</th>
                    </tr></thead>
                    <tbody>{table_rows_em}</tbody>
                </table>
            </div>
        </div></body></html>"""

        if st.button("📧 Send Email Report", use_container_width=True, type="primary"):
            if not smtp_user or not smtp_pass or not email_to:
                st.error("❌ Please fill in all email fields.")
            else:
                with st.spinner("Sending email..."):
                    ok = send_email_alert(email_to, email_subject, email_body, smtp_user, smtp_pass)
                if ok:
                    st.success(f"✅ Email sent to {email_to}!")
                else:
                    st.error("❌ Failed to send. Check SMTP credentials.")

    with tab3:
        sel_month_ds = st.selectbox("Month", months, index=current_month_index, key="ds_month")
        ds_df = df[df["Disb Month"]==sel_month_ds]
        total_disb = ds_df["Disbursed AMT"].sum()
        total_rev  = ds_df["Total_Revenue"].sum()
        total_txn  = len(ds_df)
        avg_payout = (total_rev/total_disb*100) if total_disb else 0
        top_mgr_ds = ds_df.groupby("Manager")["Disbursed AMT"].sum().idxmax() if not ds_df.empty else "N/A"
        top_camp_ds= ds_df.groupby("Campaign")["Disbursed AMT"].sum().idxmax() if not ds_df.empty else "N/A"
        top_bank_ds= ds_df.groupby("Bank")["Disbursed AMT"].sum().idxmax() if not ds_df.empty else "N/A"

        st.markdown(f"""<div style="background:linear-gradient(135deg,#0f172a,#1e293b);border-radius:16px;padding:24px;color:white;margin-bottom:20px;">
            <div style="font-size:18px;font-weight:700;margin-bottom:16px;">📋 Daily Summary — {sel_month_ds}</div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
                <div style="background:rgba(255,255,255,0.08);border-radius:10px;padding:14px;">
                    <div style="font-size:11px;color:#94a3b8;text-transform:uppercase;font-weight:600;">Total Disbursed</div>
                    <div style="font-size:20px;font-weight:800;color:#a5b4fc;margin-top:4px;">{format_inr(total_disb)}</div>
                </div>
                <div style="background:rgba(255,255,255,0.08);border-radius:10px;padding:14px;">
                    <div style="font-size:11px;color:#94a3b8;text-transform:uppercase;font-weight:600;">Total Revenue</div>
                    <div style="font-size:20px;font-weight:800;color:#6ee7b7;margin-top:4px;">{format_inr(total_rev)}</div>
                </div>
                <div style="background:rgba(255,255,255,0.08);border-radius:10px;padding:14px;">
                    <div style="font-size:11px;color:#94a3b8;text-transform:uppercase;font-weight:600;">Avg Payout %</div>
                    <div style="font-size:20px;font-weight:800;color:#fcd34d;margin-top:4px;">{avg_payout:.2f}%</div>
                </div>
                <div style="background:rgba(255,255,255,0.08);border-radius:10px;padding:14px;">
                    <div style="font-size:11px;color:#94a3b8;text-transform:uppercase;font-weight:600;">Transactions</div>
                    <div style="font-size:20px;font-weight:800;color:#f9a8d4;margin-top:4px;">{total_txn:,}</div>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

        summary_text = (f"📊 Prime PL Daily Summary — {sel_month_ds}\n\n"
            f"💰 Total Disbursed: {format_inr(total_disb)}\n"
            f"📈 Total Revenue: {format_inr(total_rev)}\n"
            f"📊 Avg Payout: {avg_payout:.2f}%\n"
            f"🔁 Transactions: {total_txn:,}\n\n"
            f"🏆 Top Manager: {top_mgr_ds}\n"
            f"🚀 Top Campaign: {top_camp_ds}\n"
            f"🏦 Top Bank: {top_bank_ds}\n\n"
            f"Generated: {now_ist.strftime('%d %b %Y %I:%M %p')} IST")
        st.download_button("⬇️ Download Summary Text", summary_text, "daily_summary.txt", "text/plain")
        
