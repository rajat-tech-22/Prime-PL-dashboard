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
import base64

# ─────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────
st.set_page_config(
    page_title="Prime PL - Ultra Dashboard 🚀",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)
st_autorefresh(interval=60 * 1000, key="refresh")

# ─────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True  # Always dark for that cyberpunk feel
if "sound_enabled" not in st.session_state:
    st.session_state.sound_enabled = True
if "particles_enabled" not in st.session_state:
    st.session_state.particles_enabled = True
if "celebration_mode" not in st.session_state:
    st.session_state.celebration_mode = False

# ─────────────────────────────────────────
# ULTRA MODERN CSS WITH ANIMATIONS
# ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800;900&family=Rajdhani:wght@300;400;500;600;700&display=swap');

* { margin: 0; padding: 0; box-sizing: border-box; }

html, body, [class*="css"] { 
    font-family: 'Rajdhani', sans-serif !important;
}

/* ANIMATED BACKGROUND */
.stApp {
    background: linear-gradient(135deg, #0a0e27 0%, #1a1a2e 25%, #16213e 50%, #0f3460 75%, #0a0e27 100%) !important;
    background-size: 400% 400% !important;
    animation: gradientShift 15s ease infinite !important;
    position: relative;
    overflow-x: hidden;
}

@keyframes gradientShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* PARTICLE CANVAS */
#particles-js {
    position: fixed;
    width: 100%;
    height: 100%;
    top: 0;
    left: 0;
    z-index: 0;
    pointer-events: none;
}

/* GLASSMORPHISM CARDS */
.glass-card {
    background: rgba(255, 255, 255, 0.05) !important;
    backdrop-filter: blur(10px) !important;
    -webkit-backdrop-filter: blur(10px) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 20px !important;
    padding: 24px !important;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3) !important;
    transition: all 0.3s ease !important;
    position: relative;
    overflow: hidden;
}

.glass-card::before {
    content: '';
    position: absolute;
    top: -2px;
    left: -2px;
    right: -2px;
    bottom: -2px;
    background: linear-gradient(45deg, #00f5ff, #ff00ff, #00f5ff);
    border-radius: 20px;
    z-index: -1;
    opacity: 0;
    transition: opacity 0.3s ease;
}

.glass-card:hover::before {
    opacity: 0.3;
}

.glass-card:hover {
    transform: translateY(-5px) scale(1.02);
    box-shadow: 0 12px 40px rgba(0, 255, 255, 0.2), 0 0 20px rgba(255, 0, 255, 0.2);
}

/* NEON TEXT */
.neon-text {
    color: #fff;
    text-shadow: 0 0 10px #00f5ff, 0 0 20px #00f5ff, 0 0 30px #00f5ff;
    animation: neonGlow 2s ease-in-out infinite alternate;
}

@keyframes neonGlow {
    from { text-shadow: 0 0 10px #00f5ff, 0 0 20px #00f5ff, 0 0 30px #00f5ff; }
    to { text-shadow: 0 0 20px #ff00ff, 0 0 30px #ff00ff, 0 0 40px #ff00ff; }
}

/* METRIC CARDS WITH ANIMATION */
.metric-glass {
    background: rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(15px);
    border: 2px solid rgba(0, 245, 255, 0.3);
    border-radius: 20px;
    padding: 20px;
    text-align: center;
    transition: all 0.3s ease;
    animation: slideUp 0.5s ease-out;
    position: relative;
    overflow: hidden;
}

@keyframes slideUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

.metric-glass::after {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: linear-gradient(45deg, transparent, rgba(0, 245, 255, 0.1), transparent);
    transform: rotate(45deg);
    animation: shine 3s infinite;
}

@keyframes shine {
    0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
    100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
}

.metric-glass:hover {
    transform: scale(1.05);
    border-color: rgba(255, 0, 255, 0.6);
    box-shadow: 0 0 30px rgba(0, 245, 255, 0.5);
}

.metric-label {
    font-family: 'Orbitron', sans-serif;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: #00f5ff;
    margin-bottom: 10px;
}

.metric-value {
    font-family: 'Orbitron', sans-serif;
    font-size: 32px;
    font-weight: 900;
    background: linear-gradient(135deg, #00f5ff 0%, #ff00ff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: valueCounter 0.5s ease-out;
}

@keyframes valueCounter {
    from { opacity: 0; transform: scale(0.5); }
    to { opacity: 1; transform: scale(1); }
}

.metric-icon {
    font-size: 28px;
    margin-bottom: 8px;
    animation: bounce 2s infinite;
}

@keyframes bounce {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-10px); }
}

/* PROGRESS BARS WITH GLOW */
.progress-container {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 50px;
    height: 20px;
    overflow: hidden;
    position: relative;
    margin: 15px 0;
}

.progress-bar {
    height: 100%;
    background: linear-gradient(90deg, #00f5ff 0%, #ff00ff 50%, #00f5ff 100%);
    background-size: 200% 100%;
    border-radius: 50px;
    animation: progressGlow 2s linear infinite;
    position: relative;
    box-shadow: 0 0 20px rgba(0, 245, 255, 0.5);
}

@keyframes progressGlow {
    0% { background-position: 0% 50%; }
    100% { background-position: 200% 50%; }
}

.progress-text {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    font-weight: 700;
    color: #fff;
    font-size: 12px;
    text-shadow: 0 0 5px rgba(0, 0, 0, 0.8);
}

/* LEADERBOARD CARDS */
.leader-card {
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(0, 245, 255, 0.2);
    border-radius: 15px;
    padding: 15px 20px;
    margin: 10px 0;
    display: flex;
    align-items: center;
    gap: 15px;
    transition: all 0.3s ease;
    animation: fadeInLeft 0.5s ease-out;
}

@keyframes fadeInLeft {
    from { opacity: 0; transform: translateX(-30px); }
    to { opacity: 1; transform: translateX(0); }
}

.leader-card:hover {
    transform: translateX(10px);
    border-color: rgba(255, 0, 255, 0.5);
    box-shadow: 0 0 25px rgba(0, 245, 255, 0.3);
}

.rank-badge {
    font-family: 'Orbitron', sans-serif;
    font-size: 24px;
    font-weight: 900;
    min-width: 50px;
    text-align: center;
    background: linear-gradient(135deg, #00f5ff, #ff00ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* ACHIEVEMENT BADGES */
.badge-container {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(255, 215, 0, 0.1);
    border: 2px solid #ffd700;
    border-radius: 25px;
    padding: 6px 14px;
    margin: 5px;
    animation: badgePop 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

@keyframes badgePop {
    0% { transform: scale(0) rotate(0deg); }
    50% { transform: scale(1.2) rotate(10deg); }
    100% { transform: scale(1) rotate(0deg); }
}

.badge-container:hover {
    transform: scale(1.1) rotate(5deg);
    box-shadow: 0 0 20px rgba(255, 215, 0, 0.6);
}

/* ALERT CARDS WITH PULSE */
.alert-card {
    border-radius: 15px;
    padding: 16px 20px;
    margin: 12px 0;
    display: flex;
    align-items: center;
    gap: 15px;
    animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
    0%, 100% { box-shadow: 0 0 10px rgba(255, 0, 0, 0.3); }
    50% { box-shadow: 0 0 25px rgba(255, 0, 0, 0.6); }
}

.alert-critical {
    background: rgba(255, 0, 0, 0.1);
    border: 2px solid #ff0055;
}

.alert-warning {
    background: rgba(255, 165, 0, 0.1);
    border: 2px solid #ffa500;
}

.alert-success {
    background: rgba(0, 255, 0, 0.1);
    border: 2px solid #00ff88;
}

/* SIDEBAR STYLING */
[data-testid="stSidebar"] {
    background: rgba(10, 14, 39, 0.9) !important;
    backdrop-filter: blur(20px) !important;
    border-right: 2px solid rgba(0, 245, 255, 0.3) !important;
}

[data-testid="stSidebar"] * {
    color: #e0e0e0 !important;
}

[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
    background: rgba(255, 255, 255, 0.05) !important;
    border: 1px solid rgba(0, 245, 255, 0.2) !important;
    border-radius: 10px !important;
    padding: 10px 15px !important;
    margin: 5px 0 !important;
    transition: all 0.3s ease !important;
}

[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {
    background: rgba(0, 245, 255, 0.1) !important;
    border-color: rgba(0, 245, 255, 0.5) !important;
    transform: translateX(5px);
}

/* BUTTON STYLES */
.stButton > button {
    background: linear-gradient(135deg, #00f5ff 0%, #ff00ff 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 12px 24px !important;
    font-weight: 700 !important;
    font-family: 'Orbitron', sans-serif !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
    box-shadow: 0 0 20px rgba(0, 245, 255, 0.4) !important;
    transition: all 0.3s ease !important;
}

.stButton > button:hover {
    transform: scale(1.05);
    box-shadow: 0 0 30px rgba(255, 0, 255, 0.6) !important;
}

/* CONFETTI ANIMATION */
@keyframes confetti-fall {
    to {
        transform: translateY(100vh) rotate(360deg);
    }
}

.confetti {
    position: fixed;
    width: 10px;
    height: 10px;
    background: #ffd700;
    animation: confetti-fall 3s linear forwards;
    z-index: 9999;
}

/* LEVEL UP ANIMATION */
.level-up {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: rgba(0, 0, 0, 0.9);
    border: 3px solid #ffd700;
    border-radius: 20px;
    padding: 40px 60px;
    z-index: 10000;
    animation: levelUpAnimation 0.5s ease-out;
    box-shadow: 0 0 50px rgba(255, 215, 0, 0.8);
}

@keyframes levelUpAnimation {
    0% { transform: translate(-50%, -50%) scale(0); opacity: 0; }
    50% { transform: translate(-50%, -50%) scale(1.2); }
    100% { transform: translate(-50%, -50%) scale(1); opacity: 1; }
}

/* FLOATING ANIMATION */
.floating {
    animation: floating 3s ease-in-out infinite;
}

@keyframes floating {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-20px); }
}

/* TEXT EFFECTS */
h1, h2, h3 {
    font-family: 'Orbitron', sans-serif !important;
    color: #fff !important;
    font-weight: 900 !important;
}

.cyber-title {
    font-size: 48px;
    font-weight: 900;
    background: linear-gradient(135deg, #00f5ff 0%, #ff00ff 50%, #00f5ff 100%);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: textShine 3s linear infinite;
    text-align: center;
    margin: 20px 0;
    text-transform: uppercase;
    letter-spacing: 3px;
}

@keyframes textShine {
    to { background-position: 200% center; }
}

/* LOADING SPINNER */
.spinner {
    border: 4px solid rgba(255, 255, 255, 0.1);
    border-top: 4px solid #00f5ff;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    animation: spin 1s linear infinite;
    margin: 20px auto;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/* CUSTOM SCROLLBAR */
::-webkit-scrollbar {
    width: 10px;
}

::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.05);
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, #00f5ff, #ff00ff);
    border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(180deg, #ff00ff, #00f5ff);
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# PARTICLE BACKGROUND
# ─────────────────────────────────────────
if st.session_state.particles_enabled:
    st.markdown("""
    <div id="particles-js"></div>
    <script src="https://cdn.jsdelivr.net/particles.js/2.0.0/particles.min.js"></script>
    <script>
    particlesJS('particles-js', {
        particles: {
            number: { value: 80, density: { enable: true, value_area: 800 } },
            color: { value: ['#00f5ff', '#ff00ff', '#ffd700'] },
            shape: { type: ['circle', 'triangle', 'edge'] },
            opacity: { value: 0.5, random: true },
            size: { value: 3, random: true },
            line_linked: {
                enable: true,
                distance: 150,
                color: '#00f5ff',
                opacity: 0.2,
                width: 1
            },
            move: {
                enable: true,
                speed: 2,
                direction: 'none',
                random: true,
                straight: false,
                out_mode: 'out',
                bounce: false
            }
        },
        interactivity: {
            detect_on: 'canvas',
            events: {
                onhover: { enable: true, mode: 'repulse' },
                onclick: { enable: true, mode: 'push' },
                resize: true
            }
        },
        retina_detect: true
    });
    </script>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────
# CONFETTI FUNCTION
# ─────────────────────────────────────────
def trigger_confetti():
    st.markdown("""
    <script>
    function createConfetti() {
        const colors = ['#ffd700', '#ff00ff', '#00f5ff', '#ff0055', '#00ff88'];
        for (let i = 0; i < 100; i++) {
            const confetti = document.createElement('div');
            confetti.className = 'confetti';
            confetti.style.left = Math.random() * 100 + 'vw';
            confetti.style.background = colors[Math.floor(Math.random() * colors.length)];
            confetti.style.animationDelay = Math.random() * 3 + 's';
            confetti.style.animationDuration = (Math.random() * 3 + 2) + 's';
            document.body.appendChild(confetti);
            setTimeout(() => confetti.remove(), 5000);
        }
    }
    createConfetti();
    </script>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────
# SOUND EFFECTS
# ─────────────────────────────────────────
def play_sound(sound_type="success"):
    if st.session_state.sound_enabled:
        sounds = {
            "success": "https://freesound.org/data/previews/270/270319_5123851-lq.mp3",
            "levelup": "https://freesound.org/data/previews/341/341695_5858296-lq.mp3",
            "alert": "https://freesound.org/data/previews/387/387232_7255534-lq.mp3"
        }
        st.markdown(f"""
        <audio autoplay>
            <source src="{sounds.get(sound_type, sounds['success'])}" type="audio/mpeg">
        </audio>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────
# VOICE ANNOUNCEMENT
# ─────────────────────────────────────────
def speak_announcement(text):
    if st.session_state.sound_enabled:
        st.markdown(f"""
        <script>
        const utterance = new SpeechSynthesisUtterance("{text}");
        utterance.rate = 1.2;
        utterance.pitch = 1.0;
        speechSynthesis.speak(utterance);
        </script>
        """, unsafe_allow_html=True)

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

NEON_COLORS = ["#00f5ff", "#ff00ff", "#ffd700", "#ff0055", "#00ff88"]

def metric_card_ultra(label, value, icon="", color="#00f5ff"):
    return f"""
    <div class="metric-glass">
        <div class="metric-icon">{icon}</div>
        <div class="metric-label">{label}</div>
        <div class="metric-value" style="color:{color}">{value}</div>
    </div>
    """

def create_neon_chart(df_group, x_col, y_col, title):
    """Create charts with neon glow effect"""
    total = df_group[y_col].sum()
    percentages = (df_group[y_col] / total * 100).round(1) if total > 0 else [0] * len(df_group)
    
    text_labels = [
        f"<b>{v/100000:.2f}L</b><br>({p:.1f}%)" 
        for v, p in zip(df_group[y_col], percentages)
    ]
    
    fig = go.Figure(go.Bar(
        x=df_group[x_col], 
        y=df_group[y_col] / 100000,
        text=text_labels,
        textposition="outside",
        marker=dict(
            color=NEON_COLORS[:len(df_group)],
            line=dict(color='rgba(0, 245, 255, 0.5)', width=2)
        ),
        hovertemplate="<b>%{x}</b><br>Amount: ₹%{y:.2f}L<br>Share: %{customdata:.1f}%<extra></extra>",
        customdata=percentages
    ))
    
    fig.update_layout(
        title=dict(
            text=title, 
            font=dict(size=18, color='#00f5ff', family='Orbitron', weight=900)
        ),
        yaxis_title="Amount (Lakhs)",
        template="plotly_dark",
        height=450,
        plot_bgcolor='rgba(0, 0, 0, 0.3)',
        paper_bgcolor='rgba(0, 0, 0, 0.2)',
        font=dict(family="Rajdhani", size=13, color='#e0e0e0'),
        margin=dict(t=60, b=60, l=50, r=30),
        xaxis=dict(tickangle=-30, gridcolor='rgba(0, 245, 255, 0.1)'),
        yaxis=dict(gridcolor='rgba(0, 245, 255, 0.1)'),
    )
    
    fig.update_traces(cliponaxis=False)
    return fig

def calculate_xp_and_level(disbursed_amount):
    """Calculate gaming-style XP and level"""
    xp = int(disbursed_amount / 100000)  # 1 XP per lakh
    level = int(xp / 100) + 1
    xp_in_level = xp % 100
    return xp, level, xp_in_level

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

def get_current_month_index(months_list):
    if not months_list: return 0
    ist = timezone(timedelta(hours=5, minutes=30))
    now = datetime.now(ist)
    return len(months_list) - 1

# ─────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────
USERNAME = os.getenv("APP_USERNAME", "Mymoneymantra")
PASSWORD = os.getenv("APP_PASSWORD", "Prime110")

for key, val in [("login", False), ("attempts", 0)]:
    if key not in st.session_state:
        st.session_state[key] = val

# ─────────────────────────────────────────
# LOGIN PAGE WITH CYBER THEME
# ─────────────────────────────────────────
if not st.session_state.login:
    st.markdown("""
    <style>
    [data-testid='stSidebar']{display:none!important;}
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="cyber-title">
        🚀 PRIME PL ULTRA 🚀
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div class="glass-card" style="text-align:center;margin-top:50px;">
            <div class="neon-text" style="font-size:36px;margin-bottom:20px;">⚡ ACCESS PORTAL ⚡</div>
            <div style="color:#00f5ff;font-size:14px;margin-bottom:30px;">
                ENTER CREDENTIALS TO ACCESS DASHBOARD
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        u = st.text_input("👤 USERNAME", placeholder="Enter username", key="login_user")
        p = st.text_input("🔐 PASSWORD", type="password", placeholder="Enter password", key="login_pass")
        
        if st.button("🚀 LAUNCH DASHBOARD", use_container_width=True, key="login_btn"):
            if u == USERNAME and p == PASSWORD:
                st.session_state.login = True
                trigger_confetti()
                speak_announcement("Access granted. Welcome to Prime PL Ultra!")
                st.rerun()
            else:
                st.error("❌ ACCESS DENIED - Invalid Credentials")
                play_sound("alert")
    
    st.stop()

# ─────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────
df = load_data()
target_raw, target_err = load_targets()
months = sorted(df["Disb Month"].dropna().unique())
current_month_index = get_current_month_index(months)

# ─────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="neon-text" style="text-align:center;font-size:24px;margin-bottom:20px;">
        ⚡ CONTROL PANEL ⚡
    </div>
    """, unsafe_allow_html=True)
    
    dashboard_type = st.radio(
        "SELECT MODULE",
        ["🎮 Gaming Dashboard", "🚀 Ultra Leaderboard", "💎 VIP Manager View", 
         "🎯 Target Wars", "🤖 AI Assistant"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    st.markdown("### ⚙️ SETTINGS")
    st.session_state.sound_enabled = st.checkbox("🔊 Sound Effects", value=True)
    st.session_state.particles_enabled = st.checkbox("✨ Particles", value=True)
    
    st.markdown("---")
    
    if st.button("🚪 LOGOUT", use_container_width=True):
        st.session_state.login = False
        st.rerun()

# ─────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────
ist_tz = timezone(timedelta(hours=5, minutes=30))
now_ist = datetime.now(ist_tz)
hour = now_ist.hour
greet = ("RISE & SHINE 🌅" if 5 <= hour < 12 else "PEAK PERFORMANCE ☀️" if hour < 16
         else "EVENING GRIND 🌇" if hour < 20 else "NIGHT OWL 🌙")

st.markdown(f"""
<div class="glass-card">
    <div style="display:flex;justify-content:space-between;align-items:center;">
        <div>
            <div class="neon-text" style="font-size:28px;margin-bottom:5px;">{greet}</div>
            <div style="color:#00f5ff;font-size:14px;">
                {now_ist.strftime("%A, %d %B %Y  •  %I:%M %p")} IST
            </div>
        </div>
        <div class="floating" style="font-size:48px;">🚀</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ══════════════════════════════════════════
# 🎮 GAMING DASHBOARD
# ══════════════════════════════════════════
if dashboard_type == "🎮 Gaming Dashboard":
    st.markdown('<div class="cyber-title" style="font-size:36px;">🎮 GAMING DASHBOARD 🎮</div>', unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown("### 🎯 FILTERS")
        selected_month = st.selectbox("📅 Month", months, index=current_month_index)
    
    filtered_df = df[df["Disb Month"] == selected_month]
    
    if filtered_df.empty:
        st.warning("⚠️ NO DATA LOADED")
    else:
        # TOP METRICS
        total_disb = filtered_df["Disbursed AMT"].sum()
        total_rev = filtered_df["Total_Revenue"].sum()
        total_txns = len(filtered_df)
        avg_payout = (total_rev / total_disb * 100) if total_disb else 0
        
        cols = st.columns(4)
        metrics = [
            ("💰 TOTAL DISBURSED", format_inr(total_disb), "💎", "#00f5ff"),
            ("📈 TOTAL REVENUE", format_inr(total_rev), "💸", "#ff00ff"),
            ("📊 AVG PAYOUT", f"{avg_payout:.2f}%", "🎯", "#ffd700"),
            ("🔁 TRANSACTIONS", f"{total_txns:,}", "⚡", "#ff0055")
        ]
        
        for col, (label, value, icon, color) in zip(cols, metrics):
            col.markdown(metric_card_ultra(label, value, icon, color), unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # MANAGER LEADERBOARD WITH XP
        st.markdown("""
        <div class="glass-card">
            <div class="neon-text" style="font-size:24px;margin-bottom:20px;">
                🏆 MANAGER LEADERBOARD - XP RANKINGS 🏆
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        mgr_data = filtered_df.groupby("Manager").agg({
            "Disbursed AMT": "sum",
            "Total_Revenue": "sum",
            "Manager": "count"
        }).reset_index()
        mgr_data.columns = ["Manager", "Disbursed", "Revenue", "Transactions"]
        mgr_data = mgr_data.sort_values("Disbursed", ascending=False).reset_index(drop=True)
        
        for idx, row in mgr_data.head(10).iterrows():
            xp, level, xp_in_level = calculate_xp_and_level(row["Disbursed"])
            
            rank_emoji = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"][idx]
            
            st.markdown(f"""
            <div class="leader-card">
                <div class="rank-badge">{rank_emoji}</div>
                <div style="flex:1;">
                    <div style="font-size:18px;font-weight:700;color:#fff;">{row['Manager']}</div>
                    <div style="display:flex;gap:10px;margin-top:5px;">
                        <span style="color:#00f5ff;font-size:12px;">💎 Level {level}</span>
                        <span style="color:#ffd700;font-size:12px;">⚡ {xp:,} XP</span>
                        <span style="color:#ff00ff;font-size:12px;">💰 {format_inr(row['Disbursed'])}</span>
                    </div>
                    <div class="progress-container" style="margin-top:10px;">
                        <div class="progress-bar" style="width:{xp_in_level}%;"></div>
                        <div class="progress-text">{xp_in_level}/100 XP to Level {level+1}</div>
                    </div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:24px;font-weight:900;color:#00f5ff;">{row['Disbursed']/100000:.1f}L</div>
                    <div style="font-size:12px;color:#ff00ff;">🎯 {row['Transactions']} kills</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # ACHIEVEMENT WALL
        st.markdown("""
        <div class="glass-card">
            <div class="neon-text" style="font-size:24px;margin-bottom:20px;">
                🏅 ACHIEVEMENT UNLOCKED 🏅
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        achievements = [
            ("⭐ FIRST BLOOD", "First transaction of the month", "#ffd700"),
            ("🔥 HOT STREAK", "5 consecutive days with transactions", "#ff0055"),
            ("💎 DIAMOND HAND", "Crossed 50L in a month", "#00f5ff"),
            ("🚀 TO THE MOON", "200% target achievement", "#ff00ff"),
            ("👑 KING OF THE HILL", "Top rank for 3 consecutive months", "#ffd700"),
        ]
        
        cols = st.columns(5)
        for col, (name, desc, color) in zip(cols, achievements):
            col.markdown(f"""
            <div class="badge-container" style="border-color:{color};flex-direction:column;text-align:center;">
                <div style="font-size:32px;margin-bottom:5px;">{name.split()[0]}</div>
                <div style="font-size:10px;font-weight:700;color:{color};">{name.split(maxsplit=1)[1]}</div>
                <div style="font-size:8px;color:#888;margin-top:5px;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # NEON CHARTS
        col1, col2 = st.columns(2)
        
        with col1:
            campaign_data = filtered_df.groupby("Campaign")["Disbursed AMT"].sum().reset_index()
            campaign_data.columns = ["Campaign", "Disbursed AMT"]
            st.plotly_chart(
                create_neon_chart(campaign_data, "Campaign", "Disbursed AMT", "🚀 CAMPAIGN POWER RANKINGS"),
                use_container_width=True
            )
        
        with col2:
            bank_data = filtered_df.groupby("Bank")["Disbursed AMT"].sum().reset_index()
            bank_data.columns = ["Bank", "Disbursed AMT"]
            st.plotly_chart(
                create_neon_chart(bank_data, "Bank", "Disbursed AMT", "🏦 BANK DOMINATION"),
                use_container_width=True
            )


# ══════════════════════════════════════════
# 🚀 ULTRA LEADERBOARD
# ══════════════════════════════════════════
elif dashboard_type == "🚀 Ultra Leaderboard":
    st.markdown('<div class="cyber-title" style="font-size:36px;">🚀 ULTRA LEADERBOARD 🚀</div>', unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown("### 🎯 FILTERS")
        lb_month = st.selectbox("📅 Month", months, index=current_month_index, key="lb_m")
        lb_metric = st.radio("📊 Rank By", ["Disbursed AMT", "Total_Revenue", "Transactions"])
    
    lb_df = df[df["Disb Month"] == lb_month]
    
    if lb_metric == "Transactions":
        lb_agg = lb_df.groupby("Manager").size().reset_index(name="Value")
    else:
        lb_agg = lb_df.groupby("Manager")[lb_metric].sum().reset_index()
        lb_agg.columns = ["Manager", "Value"]
    
    lb_agg = lb_agg.sort_values("Value", ascending=False).reset_index(drop=True)
    
    if not lb_agg.empty and len(lb_agg) >= 3:
        # PODIUM WITH CELEBRATION
        st.markdown("""
        <div class="glass-card">
            <div class="neon-text" style="text-align:center;font-size:32px;margin-bottom:30px;">
                👑 HALL OF FAME 👑
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        trigger_confetti()
        
        col_silver, col_gold, col_bronze = st.columns([1, 1.5, 1])
        
        podium = [
            (col_gold, 0, "🥇", "#ffd700", "220px", "1.2"),
            (col_silver, 1, "🥈", "#c0c0c0", "180px", "1.0"),
            (col_bronze, 2, "🥉", "#cd7f32", "180px", "1.0")
        ]
        
        for col, idx, emoji, color, height, scale in podium:
            if idx < len(lb_agg):
                row = lb_agg.iloc[idx]
                val_display = f"{row['Value']/100000:.1f}L" if lb_metric != "Transactions" else f"{int(row['Value'])}"
                
                col.markdown(f"""
                <div style="text-align:center;transform:scale({scale});">
                    <div style="font-size:80px;animation:bounce 1s infinite;">{emoji}</div>
                    <div class="glass-card" style="height:{height};display:flex;flex-direction:column;justify-content:center;">
                        <div style="font-size:18px;font-weight:900;color:#fff;margin-bottom:10px;">
                            {row['Manager']}
                        </div>
                        <div style="font-size:32px;font-weight:900;color:{color};text-shadow:0 0 20px {color};">
                            {val_display}
                        </div>
                        <div style="margin-top:15px;font-size:12px;color:#888;">
                            RANK #{idx+1}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # FULL RANKINGS
        st.markdown("""
        <div class="glass-card">
            <div class="neon-text" style="font-size:24px;margin-bottom:20px;">
                📊 FULL RANKINGS
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        for idx, row in lb_agg.iterrows():
            rank = idx + 1
            val = row["Value"]
            val_display = f"{val/100000:.2f}L" if lb_metric != "Transactions" else f"{int(val)}"
            
            rank_emojis = ["🥇", "🥈", "🥉"] + [f"{i}️⃣" for i in range(4, 11)]
            emoji = rank_emojis[idx] if idx < len(rank_emojis) else f"#{rank}"
            
            st.markdown(f"""
            <div class="leader-card">
                <div style="font-size:24px;min-width:50px;text-align:center;">{emoji}</div>
                <div style="flex:1;">
                    <div style="font-size:16px;font-weight:700;color:#fff;">{row['Manager']}</div>
                    <div style="font-size:12px;color:#888;margin-top:3px;">
                        {lb_metric.replace('_', ' ').title()}
                    </div>
                </div>
                <div style="font-size:22px;font-weight:900;color:#00f5ff;text-shadow:0 0 10px #00f5ff;">
                    {val_display}
                </div>
            </div>
            """, unsafe_allow_html=True)


# ══════════════════════════════════════════
# 💎 VIP MANAGER VIEW
# ══════════════════════════════════════════
elif dashboard_type == "💎 VIP Manager View":
    st.markdown('<div class="cyber-title" style="font-size:36px;">💎 VIP MANAGER VIEW 💎</div>', unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown("### 🎯 FILTERS")
        sel_month = st.selectbox("📅 Month", months, index=current_month_index, key="vip_m")
        mgr_list = sorted(df[df["Disb Month"] == sel_month]["Manager"].dropna().unique())
        sel_mgr = st.selectbox("👤 Manager", mgr_list, key="vip_mgr")
    
    mgr_df = df[(df["Disb Month"] == sel_month) & (df["Manager"] == sel_mgr)]
    
    if mgr_df.empty:
        st.warning("⚠️ NO DATA")
    else:
        total_disb = mgr_df["Disbursed AMT"].sum()
        total_rev = mgr_df["Total_Revenue"].sum()
        txns = len(mgr_df)
        avg_payout = (total_rev / total_disb * 100) if total_disb else 0
        
        target_val = get_target_for_manager(sel_mgr, sel_month, target_raw)
        achievement = (total_disb/100000 / target_val * 100) if target_val > 0 else 0
        
        xp, level, xp_in_level = calculate_xp_and_level(total_disb)
        
        # VIP HEADER
        st.markdown(f"""
        <div class="glass-card">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <div>
                    <div class="neon-text" style="font-size:32px;">{sel_mgr}</div>
                    <div style="display:flex;gap:15px;margin-top:10px;">
                        <span style="color:#ffd700;font-size:16px;">💎 Level {level}</span>
                        <span style="color:#00f5ff;font-size:16px;">⚡ {xp:,} XP</span>
                        <span style="color:#ff00ff;font-size:16px;">🎯 {achievement:.1f}% Target</span>
                    </div>
                </div>
                <div class="floating" style="font-size:64px;">👑</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # METRICS
        cols = st.columns(4)
        vip_metrics = [
            ("💰 DISBURSED", format_inr(total_disb), "💎", "#00f5ff"),
            ("📈 REVENUE", format_inr(total_rev), "💸", "#ff00ff"),
            ("📊 PAYOUT", f"{avg_payout:.2f}%", "🎯", "#ffd700"),
            ("🔁 DEALS", f"{txns:,}", "⚡", "#ff0055")
        ]
        
        for col, (label, value, icon, color) in zip(cols, vip_metrics):
            col.markdown(metric_card_ultra(label, value, icon, color), unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # XP PROGRESS
        st.markdown("""
        <div class="glass-card">
            <div class="neon-text" style="font-size:20px;margin-bottom:15px;">
                ⚡ XP PROGRESS TO NEXT LEVEL ⚡
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="progress-container" style="height:30px;">
            <div class="progress-bar" style="width:{xp_in_level}%;"></div>
            <div class="progress-text" style="font-size:14px;">{xp_in_level}/100 XP → Level {level+1}</div>
        </div>
        """, unsafe_allow_html=True)
        
        if achievement >= 100:
            trigger_confetti()
            speak_announcement(f"{sel_mgr} has crushed the target!")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # CHARTS
        col1, col2 = st.columns(2)
        
        with col1:
            campaign_mgr = mgr_df.groupby("Campaign")["Disbursed AMT"].sum().reset_index()
            campaign_mgr.columns = ["Campaign", "Disbursed AMT"]
            st.plotly_chart(
                create_neon_chart(campaign_mgr, "Campaign", "Disbursed AMT", "🚀 YOUR CAMPAIGNS"),
                use_container_width=True
            )
        
        with col2:
            bank_mgr = mgr_df.groupby("Bank")["Disbursed AMT"].sum().reset_index()
            bank_mgr.columns = ["Bank", "Disbursed AMT"]
            st.plotly_chart(
                create_neon_chart(bank_mgr, "Bank", "Disbursed AMT", "🏦 YOUR BANKS"),
                use_container_width=True
            )


# ══════════════════════════════════════════
# 🎯 TARGET WARS
# ══════════════════════════════════════════
elif dashboard_type == "🎯 Target Wars":
    st.markdown('<div class="cyber-title" style="font-size:36px;">🎯 TARGET WARS 🎯</div>', unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown("### 🎯 FILTERS")
        war_month = st.selectbox("📅 Month", months, index=current_month_index, key="war_m")
    
    war_df = df[df["Disb Month"] == war_month]
    mgr_actual = war_df.groupby("Manager")["Disbursed AMT"].sum().reset_index()
    mgr_actual.columns = ["Manager", "Actual"]
    
    st.markdown("""
    <div class="glass-card">
        <div class="neon-text" style="text-align:center;font-size:28px;margin-bottom:20px;">
            ⚔️ BATTLE ROYALE - WHO WILL WIN? ⚔️
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    for _, row in mgr_actual.iterrows():
        manager = row["Manager"]
        actual_l = row["Actual"] / 100000
        target_l = get_target_for_manager(manager, war_month, target_raw)
        
        if target_l == 0:
            target_l = 50
        
        achievement = (actual_l / target_l * 100)
        
        if achievement >= 100:
            status = "🏆 VICTORY"
            color = "#00ff88"
            border_color = "#00ff88"
        elif achievement >= 75:
            status = "⚡ BATTLE MODE"
            color = "#00f5ff"
            border_color = "#00f5ff"
        elif achievement >= 50:
            status = "⚠️ NEED BACKUP"
            color = "#ffa500"
            border_color = "#ffa500"
        else:
            status = "🚨 CRITICAL"
            color = "#ff0055"
            border_color = "#ff0055"
        
        st.markdown(f"""
        <div class="glass-card" style="border:2px solid {border_color};margin-bottom:15px;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:15px;">
                <div>
                    <div style="font-size:20px;font-weight:900;color:#fff;">{manager}</div>
                    <div style="font-size:14px;color:{color};margin-top:5px;">{status}</div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:24px;font-weight:900;color:{color};text-shadow:0 0 10px {color};">
                        {achievement:.1f}%
                    </div>
                    <div style="font-size:12px;color:#888;">
                        ₹{actual_l:.1f}L / ₹{target_l:.1f}L
                    </div>
                </div>
            </div>
            <div class="progress-container">
                <div class="progress-bar" style="width:{min(achievement, 100):.1f}%;background:{color};box-shadow:0 0 20px {color};"></div>
                <div class="progress-text">{achievement:.1f}% Complete</div>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════
# 🤖 AI ASSISTANT
# ══════════════════════════════════════════
elif dashboard_type == "🤖 AI Assistant":
    st.markdown('<div class="cyber-title" style="font-size:36px;">🤖 AI ASSISTANT 🤖</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="glass-card">
        <div class="neon-text" style="text-align:center;font-size:24px;margin-bottom:15px;">
            💬 ASK ME ANYTHING ABOUT YOUR DATA 💬
        </div>
        <div style="text-align:center;color:#888;font-size:14px;">
            Coming Soon: Natural language queries powered by Claude AI
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    user_query = st.text_input("🎤 Your Question", placeholder="e.g., Who is the top performer this month?")
    
    if st.button("🚀 ASK AI", use_container_width=True):
        st.markdown("""
        <div class="glass-card">
            <div style="color:#00f5ff;font-size:16px;margin-bottom:10px;">🤖 AI Response:</div>
            <div style="color:#fff;font-size:14px;line-height:1.8;">
                This feature is under development. Soon you'll be able to:
                <br>• Ask questions in natural language
                <br>• Get AI-powered insights
                <br>• Generate custom reports
                <br>• Predict future trends
            </div>
        </div>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center;padding:30px;color:#888;font-size:12px;">
    <div class="neon-text" style="font-size:20px;margin-bottom:10px;">
        ⚡ PRIME PL ULTRA ⚡
    </div>
    <div>
        Powered by Next-Gen Analytics • MyMoneyMantra © 2025
    </div>
</div>
""", unsafe_allow_html=True)
