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
from scipy import stats
import base64

# ─────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────
st.set_page_config(
    page_title="Prime PL Dashboard Pro",
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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
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

.alert-card {{
    border-radius: 12px; padding: 14px 18px; margin-bottom: 10px;
    display: flex; align-items: flex-start; gap: 12px;
}}
.alert-danger {{ background: {"#2d1515" if DM else "#fef2f2"}; border: 1px solid #fca5a5; }}
.alert-warning {{ background: {"#2d2415" if DM else "#fffbeb"}; border: 1px solid #fcd34d; }}
.alert-success {{ background: {"#152d1e" if DM else "#f0fdf4"}; border: 1px solid #86efac; }}

.badge {{
    display: inline-flex; align-items: center; gap: 6px;
    padding: 6px 14px; border-radius: 20px; margin: 4px;
    font-weight: 600; font-size: 12px;
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

# ═══════════════════════════════════════════════════════════════
# ADVANCED VISUALIZATION FUNCTIONS WITH % LABELS
# ═══════════════════════════════════════════════════════════════

def styled_bar_with_percent(df_group, x_col, y_col, title, show_percent=True, height=400):
    """Enhanced bar chart with percentage labels"""
    total = df_group[y_col].sum()
    colors = get_colors(df_group[x_col], df_group.loc[df_group[y_col].idxmax(), x_col])
    
    # Calculate percentages
    percentages = (df_group[y_col] / total * 100).round(1) if total > 0 else [0] * len(df_group)
    
    # Create text labels with both value and percentage
    if show_percent:
        text_labels = [
            f"<b>{v/100000:.2f}L</b><br>({p:.1f}%)" 
            for v, p in zip(df_group[y_col], percentages)
        ]
    else:
        text_labels = [f"<b>{v/100000:.2f}L</b>" for v in df_group[y_col]]
    
    fig = go.Figure(go.Bar(
        x=df_group[x_col], 
        y=df_group[y_col] / 100000,
        text=text_labels,
        textposition="outside", 
        marker_color=colors, 
        marker_line_width=0,
        hovertemplate="<b>%{x}</b><br>" +
                      "Amount: ₹%{y:.2f}L<br>" +
                      "Share: %{customdata:.1f}%<extra></extra>",
        customdata=percentages
    ))
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=15, color=TEXT_PRI, weight=600)),
        yaxis_title="Amount (Lakhs)", 
        template="plotly_white", 
        height=height,
        plot_bgcolor=PLOT_BG, 
        paper_bgcolor=PAPER_BG,
        font=dict(family="Inter, sans-serif", size=12, color=TEXT_PRI),
        margin=dict(t=50, b=60, l=40, r=20), 
        xaxis=dict(tickangle=-30),
    )
    
    if DM:
        fig.update_layout(
            xaxis=dict(tickangle=-30, color=TEXT_SEC, gridcolor="#334155"),
            yaxis=dict(color=TEXT_SEC, gridcolor="#334155"),
        )
    
    fig.update_traces(cliponaxis=False)
    return fig


def create_pie_chart_with_percent(df_group, names_col, values_col, title, height=400):
    """Create pie chart with percentage labels"""
    fig = go.Figure(go.Pie(
        labels=df_group[names_col],
        values=df_group[values_col],
        textposition='auto',
        textinfo='label+percent',
        textfont=dict(size=11, color='white', family='Inter'),
        marker=dict(
            colors=COLORS[:len(df_group)],
            line=dict(color=PAPER_BG, width=2)
        ),
        hovertemplate="<b>%{label}</b><br>" +
                      "Amount: ₹%{value:,.0f}<br>" +
                      "Share: %{percent}<extra></extra>",
        pull=[0.05 if i == 0 else 0 for i in range(len(df_group))]
    ))
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=15, color=TEXT_PRI, weight=600)),
        template="plotly_white",
        height=height,
        paper_bgcolor=PAPER_BG,
        font=dict(family="Inter, sans-serif", size=12, color=TEXT_PRI),
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.02,
            font=dict(size=10, color=TEXT_PRI)
        )
    )
    
    return fig


def create_performance_bubble_chart(df_month):
    """3D bubble chart: Disbursed vs Revenue vs Transactions"""
    
    mgr_metrics = df_month.groupby("Manager").agg({
        "Disbursed AMT": "sum",
        "Total_Revenue": "sum",
        "Manager": "count"
    }).reset_index()
    
    mgr_metrics.columns = ["Manager", "Disbursed", "Revenue", "Transactions"]
    mgr_metrics["Disbursed_L"] = mgr_metrics["Disbursed"] / 100000
    mgr_metrics["Revenue_L"] = mgr_metrics["Revenue"] / 100000
    
    fig = px.scatter(
        mgr_metrics,
        x="Disbursed_L",
        y="Revenue_L",
        size="Transactions",
        color="Manager",
        hover_name="Manager",
        hover_data={
            "Disbursed_L": ":.2f",
            "Revenue_L": ":.2f",
            "Transactions": ":,",
            "Manager": False
        },
        labels={
            "Disbursed_L": "Disbursed (₹L)",
            "Revenue_L": "Revenue (₹L)"
        },
        title="📊 Performance Matrix: Disbursed vs Revenue vs Transaction Volume",
        color_discrete_sequence=COLORS
    )
    
    fig.update_traces(
        marker=dict(
            line=dict(width=2, color='DarkSlateGrey'),
            opacity=0.8
        )
    )
    
    fig.update_layout(
        template="plotly_white",
        height=500,
        plot_bgcolor=PLOT_BG,
        paper_bgcolor=PAPER_BG,
        font=dict(family="Inter", size=12, color=TEXT_PRI),
        title=dict(font=dict(size=16, color=TEXT_PRI))
    )
    
    return fig


def create_correlation_heatmap(df):
    """Correlation matrix heatmap"""
    
    mgr_pivot = df.groupby("Manager").agg({
        "Disbursed AMT": "sum",
        "Total_Revenue": "sum",
        "Manager": "count"
    })
    mgr_pivot.columns = ["Disbursed", "Revenue", "Transactions"]
    
    corr_matrix = mgr_pivot.corr()
    
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.index,
        colorscale="RdBu",
        zmid=0,
        text=corr_matrix.values.round(2),
        texttemplate="%{text}",
        textfont={"size": 14, "color": "white"},
        colorbar=dict(title="Correlation")
    ))
    
    fig.update_layout(
        title="Correlation Matrix: Key Metrics",
        template="plotly_white",
        height=400,
        plot_bgcolor=PLOT_BG,
        paper_bgcolor=PAPER_BG,
        font=dict(family="Inter", size=12, color=TEXT_PRI)
    )
    
    return fig


def create_manager_campaign_heatmap(df):
    """Manager x Campaign performance heatmap"""
    
    pivot = df.pivot_table(
        values="Disbursed AMT",
        index="Manager",
        columns="Campaign",
        aggfunc="sum",
        fill_value=0
    ) / 100000
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns,
        y=pivot.index,
        colorscale="Viridis",
        text=pivot.values.round(1),
        texttemplate="₹%{text}L",
        textfont={"size": 10},
        colorbar=dict(title="Disbursed (₹L)")
    ))
    
    fig.update_layout(
        title="Manager × Campaign Performance Heatmap",
        template="plotly_white",
        height=max(400, len(pivot) * 40),
        plot_bgcolor=PLOT_BG,
        paper_bgcolor=PAPER_BG,
        font=dict(family="Inter", size=11, color=TEXT_PRI),
        xaxis_tickangle=-45
    )
    
    return fig


def create_radar_comparison_chart(mgr1_data, mgr2_data, mgr1_name, mgr2_name):
    """Radar chart for multi-dimensional comparison"""
    
    categories = ['Disbursed', 'Revenue', 'Transactions', 'Avg Ticket', 'Payout %']
    
    max_vals = {
        'Disbursed': max(mgr1_data.get('disbursed', 1), mgr2_data.get('disbursed', 1)),
        'Revenue': max(mgr1_data.get('revenue', 1), mgr2_data.get('revenue', 1)),
        'Transactions': max(mgr1_data.get('txns', 1), mgr2_data.get('txns', 1)),
        'Avg Ticket': max(mgr1_data.get('avg_ticket', 1), mgr2_data.get('avg_ticket', 1)),
        'Payout %': max(mgr1_data.get('payout_pct', 1), mgr2_data.get('payout_pct', 1))
    }
    
    mgr1_scores = [
        (mgr1_data.get('disbursed', 0) / max_vals['Disbursed'] * 100) if max_vals['Disbursed'] > 0 else 0,
        (mgr1_data.get('revenue', 0) / max_vals['Revenue'] * 100) if max_vals['Revenue'] > 0 else 0,
        (mgr1_data.get('txns', 0) / max_vals['Transactions'] * 100) if max_vals['Transactions'] > 0 else 0,
        (mgr1_data.get('avg_ticket', 0) / max_vals['Avg Ticket'] * 100) if max_vals['Avg Ticket'] > 0 else 0,
        (mgr1_data.get('payout_pct', 0) / max_vals['Payout %'] * 100) if max_vals['Payout %'] > 0 else 0
    ]
    
    mgr2_scores = [
        (mgr2_data.get('disbursed', 0) / max_vals['Disbursed'] * 100) if max_vals['Disbursed'] > 0 else 0,
        (mgr2_data.get('revenue', 0) / max_vals['Revenue'] * 100) if max_vals['Revenue'] > 0 else 0,
        (mgr2_data.get('txns', 0) / max_vals['Transactions'] * 100) if max_vals['Transactions'] > 0 else 0,
        (mgr2_data.get('avg_ticket', 0) / max_vals['Avg Ticket'] * 100) if max_vals['Avg Ticket'] > 0 else 0,
        (mgr2_data.get('payout_pct', 0) / max_vals['Payout %'] * 100) if max_vals['Payout %'] > 0 else 0
    ]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=mgr1_scores + [mgr1_scores[0]],
        theta=categories + [categories[0]],
        fill='toself',
        name=mgr1_name,
        fillcolor='rgba(99, 102, 241, 0.2)',
        line=dict(color='#6366f1', width=3)
    ))
    
    fig.add_trace(go.Scatterpolar(
        r=mgr2_scores + [mgr2_scores[0]],
        theta=categories + [categories[0]],
        fill='toself',
        name=mgr2_name,
        fillcolor='rgba(239, 68, 68, 0.2)',
        line=dict(color='#ef4444', width=3)
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100]),
            bgcolor=PLOT_BG
        ),
        showlegend=True,
        title="Multi-Dimensional Performance Comparison",
        template="plotly_white",
        height=500,
        paper_bgcolor=PAPER_BG,
        font=dict(family="Inter", size=12, color=TEXT_PRI)
    )
    
    return fig


# ═══════════════════════════════════════════════════════════════
# STATISTICAL ANALYSIS
# ═══════════════════════════════════════════════════════════════

def perform_statistical_analysis(df_current, df_previous):
    """Comprehensive statistical analysis"""
    
    results = {}
    
    try:
        current_disbursed = df_current.groupby("Manager")["Disbursed AMT"].sum()
        previous_disbursed = df_previous.groupby("Manager")["Disbursed AMT"].sum()
        
        common_managers = current_disbursed.index.intersection(previous_disbursed.index)
        
        if len(common_managers) > 1:
            curr = current_disbursed[common_managers].values
            prev = previous_disbursed[common_managers].values
            
            t_stat, p_value = stats.ttest_rel(curr, prev)
            
            results['t_test'] = {
                't_statistic': round(float(t_stat), 3),
                'p_value': round(float(p_value), 4),
                'significant': p_value < 0.05,
                'interpretation': "Significant improvement" if (t_stat > 0 and p_value < 0.05) 
                                 else "Significant decline" if (t_stat < 0 and p_value < 0.05)
                                 else "No significant change"
            }
        else:
            results['t_test'] = {
                't_statistic': 0,
                'p_value': 1.0,
                'significant': False,
                'interpretation': "Insufficient data"
            }
        
        mgr_stats = df_current.groupby("Manager").agg({
            "Disbursed AMT": "sum",
            "Total_Revenue": "sum",
            "Manager": "count"
        }).rename(columns={"Manager": "Transactions"})
        
        if len(mgr_stats) > 1:
            corr_disb_txn = mgr_stats["Disbursed AMT"].corr(mgr_stats["Transactions"])
            corr_disb_rev = mgr_stats["Disbursed AMT"].corr(mgr_stats["Total_Revenue"])
            
            results['correlations'] = {
                'disbursed_vs_transactions': round(float(corr_disb_txn), 3) if not np.isnan(corr_disb_txn) else 0,
                'disbursed_vs_revenue': round(float(corr_disb_rev), 3) if not np.isnan(corr_disb_rev) else 0
            }
        else:
            results['correlations'] = {
                'disbursed_vs_transactions': 0,
                'disbursed_vs_revenue': 0
            }
        
        disbursed_values = df_current.groupby("Manager")["Disbursed AMT"].sum()
        if len(disbursed_values) > 2:
            z_scores = np.abs(stats.zscore(disbursed_values))
            outliers = disbursed_values[z_scores > 2]
            
            results['outliers'] = {
                'managers': outliers.index.tolist(),
                'values': (outliers / 100000).round(1).tolist(),
                'interpretation': "Exceptionally high performers" if len(outliers) > 0 else "No outliers"
            }
        else:
            results['outliers'] = {
                'managers': [],
                'values': [],
                'interpretation': "No outliers"
            }
        
        if len(disbursed_values) > 1:
            cv = (disbursed_values.std() / disbursed_values.mean()) * 100 if disbursed_values.mean() > 0 else 0
            results['consistency'] = {
                'cv': round(float(cv), 1),
                'interpretation': "Highly consistent" if cv < 20 
                                 else "Moderately consistent" if cv < 40
                                 else "High variability"
            }
        else:
            results['consistency'] = {
                'cv': 0,
                'interpretation': "Insufficient data"
            }
        
    except Exception as e:
        st.error(f"Statistical analysis error: {str(e)}")
        results = {
            't_test': {'t_statistic': 0, 'p_value': 1.0, 'significant': False, 'interpretation': 'Error'},
            'correlations': {'disbursed_vs_transactions': 0, 'disbursed_vs_revenue': 0},
            'outliers': {'managers': [], 'values': [], 'interpretation': 'Error'},
            'consistency': {'cv': 0, 'interpretation': 'Error'}
        }
    
    return results


def display_statistical_dashboard(stats_results):
    """Display statistical analysis results"""
    
    st.markdown("### 📈 Statistical Analysis Report")
    
    col1, col2, col3, col4 = st.columns(4)
    
    t_test = stats_results['t_test']
    t_color = "#10b981" if "improvement" in t_test['interpretation'] else "#ef4444"
    
    with col1:
        st.markdown(f"""
        <div style="background:{CARD_BG};border-radius:12px;padding:16px;border:1px solid {CARD_BOR}">
            <div style="font-size:11px;color:{TEXT_MUT};margin-bottom:6px">T-TEST RESULT</div>
            <div style="font-size:20px;font-weight:700;color:{t_color}">
                {'✓ Significant' if t_test['significant'] else '✗ Not Significant'}
            </div>
            <div style="font-size:11px;color:{TEXT_SEC};margin-top:4px">
                p-value: {t_test['p_value']:.4f}
            </div>
            <div style="font-size:10px;color:{TEXT_MUT};margin-top:4px">
                {t_test['interpretation']}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    corr = stats_results['correlations']
    with col2:
        st.markdown(f"""
        <div style="background:{CARD_BG};border-radius:12px;padding:16px;border:1px solid {CARD_BOR}">
            <div style="font-size:11px;color:{TEXT_MUT};margin-bottom:6px">CORRELATION</div>
            <div style="font-size:20px;font-weight:700;color:#6366f1">
                {corr['disbursed_vs_transactions']:.2f}
            </div>
            <div style="font-size:11px;color:{TEXT_SEC};margin-top:4px">
                Disb vs Txns
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    outliers = stats_results['outliers']
    with col3:
        st.markdown(f"""
        <div style="background:{CARD_BG};border-radius:12px;padding:16px;border:1px solid {CARD_BOR}">
            <div style="font-size:11px;color:{TEXT_MUT};margin-bottom:6px">OUTLIERS</div>
            <div style="font-size:20px;font-weight:700;color:#f59e0b">
                {len(outliers['managers'])}
            </div>
            <div style="font-size:11px;color:{TEXT_SEC};margin-top:4px">
                High Performers
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    consistency = stats_results['consistency']
    with col4:
        st.markdown(f"""
        <div style="background:{CARD_BG};border-radius:12px;padding:16px;border:1px solid {CARD_BOR}">
            <div style="font-size:11px;color:{TEXT_MUT};margin-bottom:6px">CONSISTENCY</div>
            <div style="font-size:20px;font-weight:700;color:#8b5cf6">
                {consistency['cv']:.1f}%
            </div>
            <div style="font-size:11px;color:{TEXT_SEC};margin-top:4px">
                {consistency['interpretation']}
            </div>
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# GAMIFICATION & BADGES
# ═══════════════════════════════════════════════════════════════

def calculate_manager_badges(achievement_pct, txns, consistency_score=None):
    """Award badges based on achievements"""
    
    badges = []
    
    if achievement_pct >= 150:
        badges.append({"name": "Superstar", "icon": "⭐", "color": "#f59e0b"})
    elif achievement_pct >= 120:
        badges.append({"name": "Overachiever", "icon": "🚀", "color": "#6366f1"})
    elif achievement_pct >= 100:
        badges.append({"name": "Target Crusher", "icon": "🎯", "color": "#10b981"})
    
    if consistency_score and consistency_score < 15:
        badges.append({"name": "Mr. Consistent", "icon": "📊", "color": "#8b5cf6"})
    
    if txns > 100:
        badges.append({"name": "High Volume", "icon": "💼", "color": "#14b8a6"})
    
    return badges


def display_badge_showcase(badges):
    """Display earned badges beautifully"""
    
    if not badges:
        return
    
    badges_html = "".join([
        f"""<div class="badge" style="background:linear-gradient(135deg,{b['color']}22,{b['color']}44);
            border:2px solid {b['color']}">
            <span style="font-size:18px">{b['icon']}</span>
            <span style="color:{b['color']}">{b['name']}</span>
        </div>"""
        for b in badges
    ])
    
    st.markdown(f"""
    <div style="background:{CARD_BG};border-radius:12px;padding:16px;border:1px solid {CARD_BOR};margin:16px 0">
        <div style="font-size:13px;font-weight:600;color:{TEXT_PRI};margin-bottom:12px">
            🏆 Earned Badges
        </div>
        <div style="display:flex;flex-wrap:wrap;gap:8px">
            {badges_html}
        </div>
    </div>
    """, unsafe_allow_html=True)


def create_circular_progress(percentage, size=120, title="", subtitle=""):
    """SVG circular progress indicator"""
    
    if percentage >= 100:
        color = "#10b981"
        bg_color = "rgba(16, 185, 129, 0.1)"
    elif percentage >= 75:
        color = "#6366f1"
        bg_color = "rgba(99, 102, 241, 0.1)"
    elif percentage >= 50:
        color = "#f59e0b"
        bg_color = "rgba(245, 158, 11, 0.1)"
    else:
        color = "#ef4444"
        bg_color = "rgba(239, 68, 68, 0.1)"
    
    radius = 50
    circumference = 2 * np.pi * radius
    offset = circumference - (min(percentage, 100) / 100 * circumference)
    
    svg = f"""
    <svg width="{size}" height="{size}" viewBox="0 0 120 120" style="transform:rotate(-90deg)">
        <circle cx="60" cy="60" r="{radius}" fill="none" stroke="{bg_color}" stroke-width="10"/>
        <circle cx="60" cy="60" r="{radius}" fill="none" stroke="{color}" stroke-width="10"
                stroke-dasharray="{circumference}" stroke-dashoffset="{offset}"
                stroke-linecap="round" style="transition: stroke-dashoffset 0.5s ease"/>
        <text x="60" y="60" text-anchor="middle" dy="7" font-size="20" font-weight="700" 
              fill="{color}" style="transform:rotate(90deg);transform-origin:60px 60px">
            {percentage:.0f}%
        </text>
    </svg>
    """
    
    return f"""
    <div style="text-align:center">
        {svg}
        <div style="font-size:13px;font-weight:600;color:{TEXT_PRI};margin-top:8px">{title}</div>
        <div style="font-size:11px;color:{TEXT_SEC}">{subtitle}</div>
    </div>
    """


# ═══════════════════════════════════════════════════════════════
# ALERT SYSTEM
# ═══════════════════════════════════════════════════════════════

def check_performance_alerts(df_current_month, target_df, month_name):
    """Generate automated performance alerts"""
    alerts = []
    
    mgr_performance = df_current_month.groupby("Manager").agg({
        "Disbursed AMT": "sum",
        "Total_Revenue": "sum"
    }).reset_index()
    
    for _, row in mgr_performance.iterrows():
        manager = row["Manager"]
        actual = row["Disbursed AMT"] / 100000
        target = get_target_for_manager(manager, month_name, target_df)
        
        if target > 0:
            achievement = (actual / target) * 100
            
            if achievement < 40:
                alerts.append({
                    "severity": "critical",
                    "manager": manager,
                    "achievement": achievement,
                    "actual": actual,
                    "target": target,
                    "message": f"🚨 CRITICAL: {manager} at {achievement:.1f}% ({actual:.1f}L / {target:.1f}L)"
                })
            
            elif achievement < 60:
                alerts.append({
                    "severity": "warning",
                    "manager": manager,
                    "achievement": achievement,
                    "actual": actual,
                    "target": target,
                    "message": f"⚠️ WARNING: {manager} at {achievement:.1f}% ({actual:.1f}L / {target:.1f}L)"
                })
            
            elif achievement >= 100:
                alerts.append({
                    "severity": "success",
                    "manager": manager,
                    "achievement": achievement,
                    "actual": actual,
                    "target": target,
                    "message": f"🎉 SUCCESS: {manager} achieved {achievement:.1f}% ({actual:.1f}L / {target:.1f}L)"
                })
    
    return alerts


def display_alert_dashboard(alerts):
    """Display alerts in organized sections"""
    if not alerts:
        st.success("✅ No alerts — All managers performing well!")
        return
    
    critical = [a for a in alerts if a["severity"] == "critical"]
    warnings = [a for a in alerts if a["severity"] == "warning"]
    success = [a for a in alerts if a["severity"] == "success"]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div style="background:#fee2e2;border:1px solid #f87171;border-radius:10px;padding:12px;text-align:center">
            <div style="font-size:24px;font-weight:700;color:#991b1b">{len(critical)}</div>
            <div style="font-size:11px;color:#991b1b;font-weight:600">CRITICAL ALERTS</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background:#fef3c7;border:1px solid #fbbf24;border-radius:10px;padding:12px;text-align:center">
            <div style="font-size:24px;font-weight:700;color:#92400e">{len(warnings)}</div>
            <div style="font-size:11px;color:#92400e;font-weight:600">WARNINGS</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="background:#d1fae5;border:1px solid #4ade80;border-radius:10px;padding:12px;text-align:center">
            <div style="font-size:24px;font-weight:700;color:#065f46">{len(success)}</div>
            <div style="font-size:11px;color:#065f46;font-weight:600">HIGH PERFORMERS</div>
        </div>
        """, unsafe_allow_html=True)
    
    for alert_list, title, bg_class in [
        (critical, "🚨 Critical Alerts", "alert-danger"),
        (warnings, "⚠️ Warnings", "alert-warning"),
        (success, "🎉 High Performers", "alert-success")
    ]:
        if alert_list:
            st.markdown(f"### {title}")
            for alert in alert_list:
                st.markdown(f"""<div class="alert-card {bg_class}">
                    <span style="font-size:20px">{"🚨" if alert['severity']=='critical' else "⚠️" if alert['severity']=='warning' else "🎉"}</span>
                    <div>
                        <div style="font-weight:700;font-size:13px">{alert['manager']}</div>
                        <div style="font-size:12px">Achievement: <b>{alert['achievement']:.1f}%</b> | 
                        Actual: <b>{alert['actual']:.1f}L</b> | Target: <b>{alert['target']:.1f}L</b></div>
                    </div>
                </div>""", unsafe_allow_html=True)


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

ist = timezone(timedelta(hours=5, minutes=30))
now_ist = datetime.now(ist)

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
            <span style="font-size:12px;font-weight:600;color:#e0e7ff;">Prime PL Dashboard Pro</span>
        </span></div>""", unsafe_allow_html=True)

    st.markdown(f"""<div style="text-align:center;margin-bottom:14px;">
        <div style="font-size:19px;font-weight:700;color:#fff;line-height:1.3;margin-bottom:4px;">
            Track. Analyze.<br><span style="color:#a5b4fc;">Grow your portfolio.</span></div>
        <div style="font-size:11px;color:#7c8cba;">Real-time disbursement · AI Insights · Advanced Analytics</div>
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
        f"</div><div style='font-size:10px;color:#475569;padding-top:8px;border-top:1px solid rgba(255,255,255,0.06);'>Prime PL Pro · MyMoneyMantra · {time_str} IST</div></div>"
    )
    st.markdown(chips_html, unsafe_allow_html=True)
    st.stop()

# ─────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────
df = load_data()
target_raw, target_err = load_targets()
months = sorted(df["Disb Month"].dropna().unique())
verticals = ["All"] + sorted(df["Vertical"].dropna().unique())
managers = sorted(df["Manager"].dropna().unique())
current_month_index = get_current_month_index(months)

# ─────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────
with st.sidebar:
    st.markdown("## 💼 Prime PL Pro")
    dm_label = "☀️ Light Mode" if DM else "🌙 Dark Mode"
    if st.button(dm_label, key="dm_toggle"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()
    st.markdown("---")
    dashboard_type = st.radio(
        "Navigation",
        ["🏠 Overview", "👤 Single Manager", "⚖️ Comparison",
         "🎯 Target Tracker", "📊 Statistical Analysis",
         "🔮 Interactive Explorer", "🏆 Leaderboard & Gamification"],
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
    <div style="font-size:22px;font-weight:700;">{greet}, Welcome to Prime PL Pro!</div>
    <div style="font-size:13px;opacity:0.85;margin-top:4px;">
        {now_ist2.strftime("%A, %d %B %Y  •  %I:%M %p")} IST  •  Advanced Analytics Dashboard
    </div>
</div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════
# 🏠 OVERVIEW WITH ADVANCED FEATURES
# ══════════════════════════════════════════
if dashboard_type == "🏠 Overview":
    st.title("Overview — All Managers")
    with st.sidebar.expander("🔧 Filters", expanded=True):
        selected_month   = st.selectbox("Month", months, index=current_month_index)
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
        agg = filtered_df.groupby(["Vertical","Manager"]).agg(
            Total_Disbursed=("Disbursed AMT","sum"), 
            Total_Revenue=("Total_Revenue","sum"),
            Transactions=("Manager","count")
        ).reset_index()
        
        td = agg["Total_Disbursed"].sum()
        tr = agg["Total_Revenue"].sum()
        tt = int(agg["Transactions"].sum())
        ap = (tr/td*100) if td else 0
        
        cols = st.columns(4)
        for col, (lbl,val,icon,clr) in zip(cols,[
            ("Total Disbursed",format_inr(td),"💰","#6366f1"),
            ("Total Revenue",format_inr(tr),"📈","#10b981"),
            ("Avg Payout %",f"{ap:.2f}%","📊","#f59e0b"),
            ("Transactions",f"{tt:,}","🔁","#ef4444")
        ]):
            col.markdown(metric_card(lbl,val,icon,clr),unsafe_allow_html=True)
        
        top_bank = filtered_df.groupby("Bank")["Disbursed AMT"].sum().idxmax()
        top_campaign = filtered_df.groupby("Campaign")["Disbursed AMT"].sum().idxmax()
        top_caller = filtered_df.groupby("Caller")["Disbursed AMT"].sum().idxmax()
        insight_strip({
            "🏦 Top Bank":top_bank,
            "🚀 Top Campaign":top_campaign,
            "🏆 Top Caller":top_caller,
            "📅 Month":selected_month
        })
        
        # PERFORMANCE ALERTS
        section_header("⚡ Real-Time Performance Alerts")
        alerts = check_performance_alerts(filtered_df, target_raw, selected_month)
        display_alert_dashboard(alerts)
        
        # PIE CHARTS WITH PERCENTAGES
        section_header("Campaign & Bank Distribution")
        col_pie1, col_pie2 = st.columns(2)
        
        with col_pie1:
            cs = filtered_df.groupby("Campaign")["Disbursed AMT"].sum().reset_index()
            cs.columns = ["Campaign", "Disbursed AMT"]
            st.plotly_chart(
                create_pie_chart_with_percent(cs, "Campaign", "Disbursed AMT", "Campaign Share (%)"),
                use_container_width=True
            )
        
        with col_pie2:
            bs = filtered_df.groupby("Bank")["Disbursed AMT"].sum().reset_index()
            bs.columns = ["Bank", "Disbursed AMT"]
            st.plotly_chart(
                create_pie_chart_with_percent(bs, "Bank", "Disbursed AMT", "Bank Share (%)"),
                use_container_width=True
            )
        
        # BAR CHARTS WITH PERCENTAGES
        section_header("Campaign-wise Disbursed with % Share")
        cs = filtered_df.groupby("Campaign")["Disbursed AMT"].sum().reset_index()
        cs.columns = ["Campaign", "Disbursed AMT"]
        st.plotly_chart(
            styled_bar_with_percent(cs, "Campaign", "Disbursed AMT", 
                                   "Campaign-wise Disbursed Amount", show_percent=True),
            use_container_width=True
        )
        
        section_header("Bank-wise Disbursed with % Share")
        bs = filtered_df.groupby("Bank")["Disbursed AMT"].sum().reset_index()
        bs.columns = ["Bank", "Disbursed AMT"]
        st.plotly_chart(
            styled_bar_with_percent(bs, "Bank", "Disbursed AMT", 
                                   "Bank-wise Disbursed Amount", show_percent=True),
            use_container_width=True
        )
        
        # MANAGER SUMMARY TABLE
        section_header("Manager Summary Table")
        disp = agg.copy()
        disp["Total_Disbursed"] = disp["Total_Disbursed"].apply(format_inr)
        disp["Total_Revenue"]   = disp["Total_Revenue"].apply(format_inr)
        st.dataframe(disp, use_container_width=True, height=300)
        
        st.download_button(
            "⬇️ Download CSV", 
            disp.to_csv(index=False), 
            "overview.csv",
            "text/csv"
        )


# ══════════════════════════════════════════
# 👤 SINGLE MANAGER WITH BADGES
# ══════════════════════════════════════════
elif dashboard_type == "👤 Single Manager":
    with st.sidebar.expander("🔧 Filters", expanded=True):
        sel_month_sm = st.selectbox("Month", months, index=current_month_index, key="sm_month")
        mgr_list = sorted(df[df["Disb Month"]==sel_month_sm]["Manager"].dropna().unique())
        sel_mgr  = st.selectbox("Manager", mgr_list, key="sm_mgr")
        sel_vert_sm = st.selectbox("Vertical", verticals, key="sm_vert")
    
    f_sm = df[(df["Disb Month"]==sel_month_sm)&(df["Manager"]==sel_mgr)]
    if sel_vert_sm != "All": 
        f_sm = f_sm[f_sm["Vertical"]==sel_vert_sm]
    
    camps_sm = sorted(f_sm["Campaign"].dropna().unique())
    with st.sidebar.expander("📌 Campaigns", expanded=False):
        sel_camps_sm = st.multiselect("Campaigns", camps_sm, default=camps_sm, key="sm_camps")
    if sel_camps_sm: 
        f_sm = f_sm[f_sm["Campaign"].isin(sel_camps_sm)]
    
    st.title(f"👤 {sel_mgr} — {sel_month_sm}")
    
    if f_sm.empty:
        st.warning("No data for selected filters.")
    else:
        td,tr,ap,tc,ad,tb,tcamp,tcall = calc_metrics(f_sm)
        
        # Calculate achievement and badges
        target_val = get_target_for_manager(sel_mgr, sel_month_sm, target_raw)
        achievement = (td/100000 / target_val * 100) if target_val > 0 else 0
        
        badges = calculate_manager_badges(achievement, tc)
        display_badge_showcase(badges)
        
        cols = st.columns(4)
        for col,(lbl,val,icon,clr) in zip(cols,[
            ("Total Disbursed",format_inr(td),"💰","#6366f1"),
            ("Total Revenue",format_inr(tr),"📈","#10b981"),
            ("Avg Payout %",f"{ap:.2f}%","📊","#f59e0b"),
            ("Transactions",f"{tc:,}","🔁","#ef4444")
        ]):
            col.markdown(metric_card(lbl,val,icon,clr),unsafe_allow_html=True)
        
        insight_strip({
            "🏦 Top Bank":tb,
            "🚀 Top Campaign":tcamp,
            "🏆 Top Caller":tcall,
            "💵 Avg Ticket":f"₹{ad/100000:.2f}L"
        })
        
        # CIRCULAR PROGRESS
        if target_val > 0:
            section_header("Target Achievement")
            col1, col2, col3 = st.columns([1,1,1])
            with col2:
                st.markdown(
                    create_circular_progress(
                        achievement,
                        title=sel_mgr,
                        subtitle=f"₹{td/100000:.1f}L / ₹{target_val:.1f}L"
                    ),
                    unsafe_allow_html=True
                )
        
        # CHARTS WITH PERCENTAGES
        for title_x, grp_col in [
            ("Campaign-wise Disbursed","Campaign"),
            ("Bank-wise Disbursed","Bank"),
            ("Caller-wise Disbursed","Caller")
        ]:
            section_header(title_x)
            s = f_sm.groupby(grp_col)["Disbursed AMT"].sum().reset_index()
            s.columns = [grp_col,"Disbursed AMT"]
            st.plotly_chart(
                styled_bar_with_percent(s, grp_col, "Disbursed AMT", title_x, show_percent=True), 
                use_container_width=True
            )
        
        # MONTHLY TREND
        section_header("Monthly Trend")
        trend = df[df["Manager"]==sel_mgr].groupby("Disb Month")["Disbursed AMT"].sum().reset_index()
        fig_t = go.Figure(go.Scatter(
            x=trend["Disb Month"],
            y=trend["Disbursed AMT"]/100000,
            mode="lines+markers",
            line=dict(width=2.5,color="#6366f1"),
            marker=dict(size=8)
        ))
        fig_t.update_layout(
            template="plotly_white",
            height=380,
            yaxis_title="Disbursed (L)",
            font=dict(family="Inter"),
            plot_bgcolor=PLOT_BG,
            paper_bgcolor=PAPER_BG
        )
        st.plotly_chart(fig_t,use_container_width=True)
        
        # RAW DATA
        section_header("Raw Data")
        dd = f_sm.dropna(how="all").copy()
        st.dataframe(dd,use_container_width=True,height=300)
        st.download_button(
            "⬇️ Download CSV",
            dd.to_csv(index=False),
            f"{sel_mgr}_{sel_month_sm}.csv",
            "text/csv"
        )


# ══════════════════════════════════════════
# ⚖️ COMPARISON WITH RADAR CHART
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
        sc1 = st.multiselect("Campaigns", sorted(f1["Campaign"].dropna().unique()), 
                            default=sorted(f1["Campaign"].dropna().unique()), key="c1")
    with st.sidebar.expander("📌 Campaigns — 2", expanded=False):
        sc2 = st.multiselect("Campaigns", sorted(f2["Campaign"].dropna().unique()), 
                            default=sorted(f2["Campaign"].dropna().unique()), key="c2")
    
    if sc1: f1 = f1[f1["Campaign"].isin(sc1)]
    if sc2: f2 = f2[f2["Campaign"].isin(sc2)]
    
    lbl1=f"{mgr1} ({m1})"
    lbl2=f"{mgr2} ({m2})"
    
    st.title("⚖️ Comparison")
    
    if f1.empty or f2.empty: 
        st.warning("No data for one or both selections.")
        st.stop()
    
    d1,r1,p1,t1,a1,tb1,tc1,tcall1 = calc_metrics(f1)
    d2,r2,p2,t2,a2,tb2,tc2,tcall2 = calc_metrics(f2)
    
    winner = lbl1 if d1>d2 else lbl2
    st.success(f"🏆 Winner: **{winner}** with {format_inr(max(d1,d2))}")
    
    # RADAR CHART COMPARISON
    section_header("Multi-Dimensional Comparison")
    mgr1_data = {
        'disbursed': d1/100000,
        'revenue': r1/100000,
        'txns': t1,
        'avg_ticket': a1/100000,
        'payout_pct': p1
    }
    
    mgr2_data = {
        'disbursed': d2/100000,
        'revenue': r2/100000,
        'txns': t2,
        'avg_ticket': a2/100000,
        'payout_pct': p2
    }
    
    st.plotly_chart(
        create_radar_comparison_chart(mgr1_data, mgr2_data, lbl1, lbl2),
        use_container_width=True
    )
    
    # METRIC CARDS
    col1,col2 = st.columns(2)
    cards_meta=[
        ("Total Disbursed","#6366f1"),
        ("Total Revenue","#10b981"),
        ("Avg Payout %","#f59e0b"),
        ("Transactions","#ef4444")
    ]
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
    
    insight_strip({
        f"{lbl1} Bank":tb1,
        f"{lbl1} Campaign":tc1,
        f"{lbl2} Bank":tb2,
        f"{lbl2} Campaign":tc2
    })
    
    # HEAD-TO-HEAD BAR
    section_header("Head-to-Head")
    comp_df = pd.DataFrame({
        "Metric":["Disbursed (L)","Revenue (L)","Transactions"],
        lbl1:[d1/100000,r1/100000,t1],
        lbl2:[d2/100000,r2/100000,t2]
    })
    
    fig_c = go.Figure()
    for lbl,vals,clr in [(lbl1,comp_df[lbl1],"#6366f1"),(lbl2,comp_df[lbl2],"#ef4444")]:
        fig_c.add_trace(go.Bar(
            name=lbl,
            x=comp_df["Metric"],
            y=vals,
            text=[f"<b>{v:.2f}</b>" for v in vals],
            textposition="outside",
            marker_color=clr
        ))
    
    fig_c.update_layout(
        barmode="group",
        template="plotly_white",
        height=420,
        font=dict(family="Inter"),
        plot_bgcolor=PLOT_BG,
        paper_bgcolor=PAPER_BG
    )
    st.plotly_chart(fig_c,use_container_width=True)
    
    growth = ((d1-d2)/d2*100) if d2 else 0
    st.info(f"📈 {lbl1} is **{abs(growth):.2f}%** {'higher' if growth>=0 else 'lower'} than {lbl2}")


# ══════════════════════════════════════════
# 🎯 TARGET TRACKER WITH CIRCULAR PROGRESS
# ══════════════════════════════════════════
elif dashboard_type == "🎯 Target Tracker":
    st.title("🎯 Target Tracker")
    
    with st.sidebar.expander("🔧 Filter", expanded=True):
        sel_month = st.selectbox("Month", months, index=current_month_index)
    
    col_ref,col_info = st.columns([1,5])
    with col_ref:
        if st.button("🔄 Reload"):
            st.cache_data.clear()
            st.rerun()
    
    with col_info:
        if target_err: 
            st.error(f"Target sheet load failed: {target_err}")
        elif target_raw.empty: 
            st.warning("Target sheet is empty.")
        else: 
            st.success(f"✅ Targets loaded — {len(target_raw)} rows")
    
    filtered_mgr_df = df[df["Disb Month"]==sel_month]
    mgr_actual = filtered_mgr_df.groupby("Manager")["Disbursed AMT"].sum().reset_index()
    mgr_actual.columns = ["Manager","Actual"]
    
    targets_dict = {}
    for _,row in mgr_actual.iterrows():
        t = get_target_for_manager(row["Manager"],sel_month,target_raw)
        targets_dict[row["Manager"]] = t if t>0 else 50
    
    # CIRCULAR PROGRESS GRID
    section_header("Manager Progress Overview")
    
    mgr_goals = {}
    for _,row in mgr_actual.iterrows():
        mgr_goals[row["Manager"]] = {
            'actual': row["Actual"]/100000,
            'target': targets_dict.get(row["Manager"], 50)
        }
    
    cols_per_row = 4
    mgr_list = list(mgr_goals.keys())
    
    for i in range(0, len(mgr_list), cols_per_row):
        cols = st.columns(cols_per_row)
        for j, col in enumerate(cols):
            if i + j < len(mgr_list):
                mgr = mgr_list[i + j]
                data = mgr_goals[mgr]
                achievement = (data['actual'] / data['target'] * 100) if data['target'] > 0 else 0
                
                with col:
                    st.markdown(
                        create_circular_progress(
                            achievement,
                            title=mgr,
                            subtitle=f"₹{data['actual']:.1f}L / ₹{data['target']:.1f}L"
                        ),
                        unsafe_allow_html=True
                    )
    
    # TEAM OVERVIEW
    section_header("Team Overview")
    total_actual = mgr_actual["Actual"].sum()/100000
    total_target = sum(targets_dict.values())
    team_pct = (total_actual/total_target*100) if total_target else 0
    
    col_a,col_b,col_c = st.columns(3)
    col_a.markdown(metric_card("Team Disbursed",f"{total_actual:.1f}L","💼","#6366f1"),unsafe_allow_html=True)
    col_b.markdown(metric_card("Team Target",f"{total_target:.1f}L","🎯","#f59e0b"),unsafe_allow_html=True)
    col_c.markdown(metric_card("Achievement %",f"{team_pct:.1f}%","📊","#10b981" if team_pct>=75 else "#ef4444"),unsafe_allow_html=True)


# ══════════════════════════════════════════
# 📊 STATISTICAL ANALYSIS
# ══════════════════════════════════════════
elif dashboard_type == "📊 Statistical Analysis":
    st.title("📊 Statistical Analysis")
    
    with st.sidebar.expander("🔧 Filters", expanded=True):
        month_curr = st.selectbox("Current Month", months, index=current_month_index, key="stat_curr")
        month_prev_idx = max(0, current_month_index - 1)
        month_prev = st.selectbox("Previous Month", months, index=month_prev_idx, key="stat_prev")
    
    df_curr = df[df["Disb Month"] == month_curr]
    df_prev = df[df["Disb Month"] == month_prev]
    
    if df_curr.empty or df_prev.empty:
        st.warning("Insufficient data for statistical analysis")
    else:
        # PERFORM ANALYSIS
        stats_results = perform_statistical_analysis(df_curr, df_prev)
        display_statistical_dashboard(stats_results)
        
        # CORRELATION HEATMAP
        section_header("Correlation Analysis")
        st.plotly_chart(create_correlation_heatmap(df_curr), use_container_width=True)
        
        # MANAGER x CAMPAIGN HEATMAP
        section_header("Manager × Campaign Performance Heatmap")
        st.plotly_chart(create_manager_campaign_heatmap(df_curr), use_container_width=True)


# ══════════════════════════════════════════
# 🔮 INTERACTIVE EXPLORER
# ══════════════════════════════════════════
elif dashboard_type == "🔮 Interactive Explorer":
    st.title("🔮 Interactive Data Explorer")
    
    with st.sidebar.expander("🔧 Filters", expanded=True):
        exp_month = st.selectbox("Month", months, index=current_month_index, key="exp_month")
    
    exp_df = df[df["Disb Month"] == exp_month]
    
    if exp_df.empty:
        st.warning("No data available")
    else:
        # BUBBLE CHART
        section_header("Performance Matrix (Bubble Chart)")
        st.plotly_chart(create_performance_bubble_chart(exp_df), use_container_width=True)
        
        # INTERACTIVE FILTERS
        section_header("Dynamic Filtering")
        
        col_f1, col_f2, col_f3 = st.columns(3)
        
        with col_f1:
            selected_managers = st.multiselect(
                "Select Managers",
                sorted(exp_df["Manager"].unique()),
                default=sorted(exp_df["Manager"].unique())[:5]
            )
        
        with col_f2:
            selected_banks = st.multiselect(
                "Select Banks",
                sorted(exp_df["Bank"].unique()),
                default=sorted(exp_df["Bank"].unique())
            )
        
        with col_f3:
            min_disb = float(exp_df["Disbursed AMT"].min())
            max_disb = float(exp_df["Disbursed AMT"].max())
            disb_range = st.slider(
                "Disbursement Range (₹)",
                min_value=min_disb,
                max_value=max_disb,
                value=(min_disb, max_disb)
            )
        
        # APPLY FILTERS
        filtered_exp = exp_df[
            (exp_df["Manager"].isin(selected_managers)) &
            (exp_df["Bank"].isin(selected_banks)) &
            (exp_df["Disbursed AMT"] >= disb_range[0]) &
            (exp_df["Disbursed AMT"] <= disb_range[1])
        ]
        
        # FILTERED RESULTS
        section_header("Filtered Results")
        
        col_r1, col_r2, col_r3 = st.columns(3)
        
        filt_disb = filtered_exp["Disbursed AMT"].sum()
        filt_rev = filtered_exp["Total_Revenue"].sum()
        filt_txns = len(filtered_exp)
        
        col_r1.markdown(metric_card("Filtered Disbursed", format_inr(filt_disb), "💰", "#6366f1"), unsafe_allow_html=True)
        col_r2.markdown(metric_card("Filtered Revenue", format_inr(filt_rev), "📈", "#10b981"), unsafe_allow_html=True)
        col_r3.markdown(metric_card("Filtered Transactions", f"{filt_txns:,}", "🔁", "#ef4444"), unsafe_allow_html=True)
        
        # FILTERED DATA TABLE
        st.dataframe(filtered_exp, use_container_width=True, height=400)


# ══════════════════════════════════════════
# 🏆 LEADERBOARD & GAMIFICATION
# ══════════════════════════════════════════
elif dashboard_type == "🏆 Leaderboard & Gamification":
    st.title("🏆 Leaderboard & Gamification")
    
    with st.sidebar.expander("🔧 Filters", expanded=True):
        lb_month = st.selectbox("Month", months, index=current_month_index, key="lb_month")
        lb_by = st.radio("Rank By", ["Disbursed AMT","Total_Revenue","Transactions"], key="lb_by")
        top_n = st.slider("Top N", 3, 20, 10, key="lb_topn")
    
    lb_df = df[df["Disb Month"]==lb_month].copy()
    
    if lb_by == "Transactions":
        lb_agg = lb_df.groupby("Manager").size().reset_index(name="Value")
    else:
        lb_agg = lb_df.groupby("Manager")[lb_by].sum().reset_index()
        lb_agg.columns = ["Manager","Value"]
    
    lb_agg = lb_agg.sort_values("Value",ascending=False).head(top_n).reset_index(drop=True)
    
    if lb_agg.empty:
        st.warning("No data for selected filters.")
    else:
        # PODIUM
        if len(lb_agg) >= 3:
            section_header("🎖️ Podium")
            pc1,pc2,pc3 = st.columns([1,1.2,1])
            
            podium_data = [
                (pc2, 0, "#f59e0b","🥇","Gold"), 
                (pc1, 1, "#94a3b8","🥈","Silver"), 
                (pc3, 2, "#cd7f32","🥉","Bronze")
            ]
            
            for col,idx,clr,emoji,title_p in podium_data:
                row_p = lb_agg.iloc[idx]
                val_display = f"{row_p['Value']/100000:.2f}L" if lb_by!="Transactions" else f"{int(row_p['Value'])}"
                
                # Calculate badges for podium managers
                target_val = get_target_for_manager(row_p["Manager"], lb_month, target_raw)
                achievement = (row_p['Value']/100000 / target_val * 100) if target_val > 0 and lb_by == "Disbursed AMT" else 0
                
                mgr_txns = lb_df[lb_df["Manager"] == row_p["Manager"]].shape[0]
                badges = calculate_manager_badges(achievement, mgr_txns)
                
                badges_html = "".join([f'<span style="font-size:16px;margin:0 2px">{b["icon"]}</span>' for b in badges[:3]])
                
                col.markdown(f"""<div style="background:{CARD_BG};border-radius:16px;padding:20px;
                    border:2px solid {clr};text-align:center;box-shadow:0 4px 16px rgba(0,0,0,0.1);">
                    <div style="font-size:36px">{emoji}</div>
                    <div style="font-size:13px;font-weight:700;color:{TEXT_PRI};margin:8px 0 4px">{row_p["Manager"]}</div>
                    <div style="font-size:20px;font-weight:800;color:{clr}">{val_display}</div>
                    <div style="font-size:11px;color:{TEXT_MUT};margin-top:4px">{title_p}</div>
                    <div style="margin-top:8px">{badges_html}</div>
                </div>""", unsafe_allow_html=True)
        
        # FULL RANKINGS WITH BADGES
        section_header("📊 Full Rankings")
        
        for i, row in lb_agg.iterrows():
            rank = i + 1
            val = row["Value"]
            
            rank_colors_local = ["#f59e0b","#94a3b8","#cd7f32","#6366f1","#10b981","#8b5cf6","#ec4899"]
            rank_emojis_local = ["🥇","🥈","🥉","4️⃣","5️⃣","6️⃣","7️⃣"]
            
            clr = rank_colors_local[i] if i < len(rank_colors_local) else "#6366f1"
            emoji = rank_emojis_local[i] if i < len(rank_emojis_local) else f"#{rank}"
            val_display = f"{val/100000:.2f}L" if lb_by != "Transactions" else f"{int(val)}"
            sub_text = f"₹{val/100000:.2f} Lakhs" if lb_by != "Transactions" else f"{int(val)} transactions"
            
            # Get badges
            target_val = get_target_for_manager(row["Manager"], lb_month, target_raw)
            achievement = (val/100000 / target_val * 100) if target_val > 0 and lb_by == "Disbursed AMT" else 0
            mgr_txns = lb_df[lb_df["Manager"] == row["Manager"]].shape[0]
            badges = calculate_manager_badges(achievement, mgr_txns)
            
            badges_html = "".join([
                f'<span style="font-size:14px;margin:0 3px" title="{b["name"]}">{b["icon"]}</span>' 
                for b in badges
            ])
            
            st.markdown(f"""<div style="background:{CARD_BG};border-radius:16px;padding:16px 20px;
                border:1px solid {CARD_BOR};margin-bottom:10px;display:flex;align-items:center;gap:16px;
                transition:transform 0.15s">
                <div style="font-size:22px;font-weight:800;min-width:40px;text-align:center;color:{clr}">{emoji}</div>
                <div style="flex:1">
                    <div style="font-size:15px;font-weight:700;color:{TEXT_PRI}">{row["Manager"]}</div>
                    <div style="font-size:12px;color:{TEXT_SEC};margin-top:2px">{sub_text}</div>
                </div>
                <div style="display:flex;gap:4px;align-items:center">
                    {badges_html}
                </div>
                <div style="font-size:18px;font-weight:800;color:{clr}">{val_display}</div>
            </div>""", unsafe_allow_html=True)

st.markdown("---")
st.markdown("""
<div style="text-align:center;padding:20px;color:{};font-size:12px">
    <b>Prime PL Dashboard Pro</b> • Powered by Advanced Analytics & AI 
    <br>MyMoneyMantra © 2025 • All Rights Reserved
</div>
""".format(TEXT_MUT), unsafe_allow_html=True)
