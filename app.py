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
# Sidebar CSS for Black Theme
# -----------------------------
st.markdown("""
    <style>
    /* Sidebar background */
    [data-testid="stSidebar"] {
        background-color: #0e1117;
        color: white;
    }

    /* Sidebar title */
    [data-testid="stSidebar"] .css-1d391kg {
        color: white;
        font-size: 20px;
        font-weight: bold;
    }

    /* Sidebar expanders */
    [data-testid="stSidebar"] .st-expander {
        background-color: #1a1c23;
        border-radius: 8px;
        margin-bottom: 10px;
    }

    /* Sidebar radio/select/multiselect text */
    [data-testid="stSidebar"] .stRadio > div, 
    [data-testid="stSidebar"] .stSelectbox > div,
    [data-testid="stSidebar"] .stMultiselect > div {
        color: white;
    }

    /* Scrollbar for sidebar */
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
# Filters for All Managers
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

    # ✅ Fix: Ensure All Managers Data Shows
    st.header("📊 Enterprise Overview")
    if filtered_df.empty:
        st.warning("No data available for selected filters")
    else:
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

        bank_summary = filtered_df.groupby("Bank")["Disbursed AMT"].sum()
        if not bank_summary.empty:
            top_bank = bank_summary.idxmax()
            bank_colors = get_colors(bank_summary.index, top_bank)
            fig_bank = go.Figure(go.Bar(
                x=bank_summary.index,
                y=bank_summary.values/100000,
                text=[f"{v/100000:.2f}L" for v in bank_summary.values],
                textposition="auto",
                marker_color=bank_colors,
                name="Banks"
            ))
            fig_bank.update_layout(
                yaxis_title="Amount (L)",
                template="plotly_white",
                height=400,
                title="Bank-wise Disbursed Amount"
            )
            st.plotly_chart(fig_bank, use_container_width=True)

# -----------------------------
# Single Manager Dashboard & Comparison
# (logic remains same as before)
# -----------------------------
# You can keep your original Single Manager and Comparison code here
