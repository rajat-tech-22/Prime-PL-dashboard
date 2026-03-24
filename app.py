import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from streamlit_autorefresh import st_autorefresh

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(page_title="Manager Dashboard", layout="wide")
st_autorefresh(interval=60*1000, key="refresh")  # Auto-refresh every 60s

# -----------------------------
# Sidebar Dark Theme CSS
# -----------------------------
st.markdown("""
<style>
/* Sidebar dark background */
[data-testid="stSidebar"] {
    background-color: #111111;
    color: white;
}

/* Sidebar title and headers */
[data-testid="stSidebar"] .css-1d391kg,
[data-testid="stSidebar"] .stExpanderHeader {
    color: white;
    font-weight: bold;
    font-size: 18px;
}

/* Sidebar expanders */
[data-testid="stSidebar"] .st-expander {
    background-color: #1a1a1a;
    border-radius: 8px;
    margin-bottom: 8px;
}

/* Input texts and select boxes inside sidebar */
[data-testid="stSidebar"] .stTextInput input,
[data-testid="stSidebar"] .stSelectbox select,
[data-testid="stSidebar"] .stMultiselect select,
[data-testid="stSidebar"] .stRadio input + label {
    color: white !important;
    background-color: #111111 !important;
}

/* Selected item highlight for dropdowns / multiselects */
[data-baseweb="select"] .baseweb-select__control.baseweb-select__control--is-focused {
    background-color: #333333 !important;
    color: white !important;
}
[data-baseweb="select"] .baseweb-select__menu .baseweb-option--is-focused {
    background-color: #555555 !important;
    color: white !important;
}
[data-baseweb="select"] .baseweb-select__menu .baseweb-option--is-selected {
    background-color: #007acc !important;
    color: white !important;
}

/* Radio button selected */
[data-testid="stSidebar"] .stRadio input:checked + label {
    background-color: #007acc !important;
    color: white !important;
    border-radius: 5px;
    padding: 2px 8px;
}

/* Scrollbar */
[data-testid="stSidebar"] ::-webkit-scrollbar {
    width: 8px;
}
[data-testid="stSidebar"] ::-webkit-scrollbar-thumb {
    background-color: rgba(255,255,255,0.2);
    border-radius: 4px;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Load Data
# -----------------------------
@st.cache_data(ttl=60)
def load_data():
    url = "https://docs.google.com/spreadsheets/d/1I1ql5NwFafbWXYkVOvv0yvMM9GKnJ5954R4zif2owGI/export?format=csv"
    df = pd.read_csv(url)
    df.replace("null", None, inplace=True)
    return df

df = load_data()

# -----------------------------
# Helper Functions
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

base_colors = ["#636EFA","#EF553B","#00CC96","#AB63FA","#FFA15A","#19D3F3","#FF6692","#B6E880"]

def get_colors(index_list, top_value):
    colors = []
    for i, val in enumerate(index_list):
        if val == top_value:
            colors.append("#FFD700")
        else:
            colors.append(base_colors[i % len(base_colors)])
    return colors

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

def plot_bar(f, col, top_value, manager_name, key_val):
    summary = f.groupby(col)["Disbursed AMT"].sum()
    colors = get_colors(summary.index, top_value)
    fig = go.Figure(go.Bar(
        x=summary.index,
        y=summary.values/100000,
        text=[f"{v/100000:.2f}L" for v in summary.values],
        textposition="auto",
        marker_color=colors,
        name=manager_name
    ))
    fig.update_layout(
        yaxis_title="Amount (L)",
        template="plotly_white",
        height=400,
        title=f"{manager_name} - {col} Summary"
    )
    return fig

def colored_metric(label, value, color="#000000"):
    st.markdown(f"""
        <div style="background-color:{color}; padding:20px; border-radius:10px; text-align:center; color:white; margin-bottom:10px;">
            <h4 style="margin:0">{label}</h4>
            <h2 style="margin:0">{value}</h2>
        </div>
        """, unsafe_allow_html=True)

# -----------------------------
# Sidebar Filters
# -----------------------------
st.sidebar.title("📊 Dashboard Filters")
with st.sidebar.expander("Select Dashboard Type", expanded=True):
    dashboard_type = st.radio("Dashboard", ["All Managers", "Single Manager", "Comparison"])

verticals = ["All"] + sorted(df["Vertical"].dropna().unique())
months = sorted(df["Disb Month"].dropna().unique())
managers = sorted(df["Manager"].dropna().unique())
latest_month_index = len(months)-1

# -----------------------------
# Filters Logic
# -----------------------------
if dashboard_type == "All Managers":
    with st.sidebar.expander("Month & Vertical Filters", expanded=True):
        selected_month = st.selectbox("Select Month", months, index=latest_month_index)
        selected_vertical = st.selectbox("Business Vertical", verticals)
    
    filtered_df = df.copy()
    if selected_vertical != "All":
        filtered_df = filtered_df[filtered_df["Vertical"]==selected_vertical]
    if selected_month:
        filtered_df = filtered_df[filtered_df["Disb Month"]==selected_month]

    campaigns_available = sorted(filtered_df["Campaign"].dropna().unique())
    with st.sidebar.expander("Campaign Filter", expanded=True):
        selected_campaigns = st.multiselect("Select Campaigns", campaigns_available, default=campaigns_available)
    if selected_campaigns:
        filtered_df = filtered_df[filtered_df["Campaign"].isin(selected_campaigns)]

elif dashboard_type == "Single Manager":
    with st.sidebar.expander("Manager & Month Filters", expanded=True):
        selected_manager = st.selectbox("Select Manager", managers)
        selected_month = st.selectbox("Select Month", months, index=latest_month_index)

    filtered_df = df[df["Manager"]==selected_manager]
    if selected_month:
        filtered_df = filtered_df[filtered_df["Disb Month"]==selected_month]

    campaigns_available = sorted(filtered_df["Campaign"].dropna().unique())
    with st.sidebar.expander("Campaign Filter", expanded=True):
        selected_campaigns = st.multiselect("Select Campaigns", campaigns_available, default=campaigns_available)
    if selected_campaigns:
        filtered_df = filtered_df[filtered_df["Campaign"].isin(selected_campaigns)]

elif dashboard_type == "Comparison":
    with st.sidebar.expander("Manager & Month Selection", expanded=True):
        selected_manager1 = st.selectbox("First Manager", managers)
        selected_month1 = st.selectbox("Month for First Manager", months, index=latest_month_index)
        selected_manager2 = st.selectbox("Second Manager", managers)
        selected_month2 = st.selectbox("Month for Second Manager", months, index=latest_month_index)

    filtered_df1 = df[(df["Manager"]==selected_manager1) & (df["Disb Month"]==selected_month1)]
    filtered_df2 = df[(df["Manager"]==selected_manager2) & (df["Disb Month"]==selected_month2)]

# -----------------------------
# All Managers Dashboard
# -----------------------------
if dashboard_type == "All Managers":
    st.header("📊 Enterprise Overview")
    agg_df = filtered_df.groupby(["Vertical","Manager"]).agg(
        Total_Disbursed=("Disbursed AMT","sum"),
        Total_Revenue=("Total_Revenue","sum"),
        Transactions=("Manager","count")
    ).reset_index()
    agg_df["Avg_Payout"] = (agg_df["Total_Revenue"]/agg_df["Total_Disbursed"]*100).round(2)
    agg_df.sort_values(["Vertical","Total_Disbursed"], ascending=[True,False], inplace=True)
    agg_df["Total_Disbursed"] = agg_df["Total_Disbursed"].apply(format_inr)
    agg_df["Total_Revenue"] = agg_df["Total_Revenue"].apply(format_inr)

    st.dataframe(agg_df, use_container_width=True, height=500)
    st.download_button("Download CSV", agg_df.to_csv(index=False), "all_managers.csv", "text/csv")
