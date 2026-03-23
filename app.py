import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from streamlit_autorefresh import st_autorefresh

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(page_title="Manager Dashboard", layout="wide")

# Auto-refresh every 60 sec
st_autorefresh(interval=60*1000, key="refresh")

# -----------------------------
# Load Data from Google Sheets
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

def plot_bar(f, col, top_value, manager_name, chart_key):
    summary = f.groupby(col)["Disbursed AMT"].sum()
    colors = get_colors(summary.index, top_value)
    fig = go.Figure(go.Bar(
        x=summary.index,
        y=summary.values/100000,
        text=[f"{v/100000:.2f}L" for v in summary.values],
        textposition="auto",
        marker_color=colors,
        name=manager_name,
        width=0.5
    ))
    fig.update_layout(title=f"{col} Disbursed Amount - {manager_name}", yaxis_title="Amount (L)", template="plotly_white", height=400)
    return fig

# -----------------------------
# Sidebar Filters (Month First)
# -----------------------------
st.sidebar.title("Dashboard Selection")
selected_month = st.sidebar.selectbox("Select Month", sorted(df["Disb Month"].dropna().unique()))
dashboard_type = st.sidebar.radio("Select Dashboard", ["All Managers", "Single Manager", "Comparison"])

# -----------------------------
# ALL MANAGERS DASHBOARD
# -----------------------------
if dashboard_type=="All Managers":
    st.header("📋 All Managers Dashboard")
    filtered_df = df[df["Disb Month"] == selected_month]

    agg_df = filtered_df.groupby(["Vertical","Manager"]).agg(
        Total_Disbursed=("Disbursed AMT","sum"),
        Total_Revenue=("Total_Revenue","sum"),
        Transactions=("Manager","count")
    ).reset_index()
    agg_df["Avg_Payout_%"] = (agg_df["Total_Revenue"] / agg_df["Total_Disbursed"] * 100).round(2)
    agg_df = agg_df.sort_values(by=["Vertical", "Total_Disbursed"], ascending=[True, False]).reset_index(drop=True)
    agg_df.insert(0, "No", range(1, len(agg_df)+1))

    def highlight_top(row):
        style = ['']*len(row)
        if row["Total_Disbursed"] == agg_df[agg_df["Vertical"]==row["Vertical"]]["Total_Disbursed"].max():
            style[2] = 'background-color: #FFD700; font-weight:bold;'
        if row["Avg_Payout_%"] > 10:
            style[5] = 'background-color: #90EE90; font-weight:bold;'
        return style

    st.dataframe(
        agg_df.style.format({
            "Total_Disbursed": "₹{:,.0f}",
            "Total_Revenue": "₹{:,.0f}",
            "Avg_Payout_%": "{:.2f}%"
        }).apply(highlight_top, axis=1),
        width='stretch'
    )

    csv = agg_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name=f'all_managers_{selected_month}.csv',
        mime='text/csv'
    )

# -----------------------------
# SINGLE MANAGER DASHBOARD
# -----------------------------
if dashboard_type=="Single Manager":
    st.header("📊 Single Manager Dashboard")
    managers = sorted(df["Manager"].dropna().unique())
    selected_manager = st.selectbox("Select Manager", managers)

    f = df[(df["Manager"]==selected_manager)&(df["Disb Month"]==selected_month)]
    if f.empty:
        st.warning("No data available")
    else:
        total_disb,total_rev,avg_payout,txn_count,avg_disb,top_bank,top_campaign,top_caller = calc_metrics(f)
        col1,col2,col3 = st.columns(3)
        col1.metric("Total Disbursed", format_inr(total_disb))
        col2.metric("Total Revenue", format_inr(total_rev))
        col3.metric("Avg Payout %", f"{avg_payout:.2f}%")

        st.plotly_chart(plot_bar(f,"Bank",top_bank,selected_manager,"single_bank"), width='stretch')
        st.plotly_chart(plot_bar(f,"Caller",top_caller,selected_manager,"single_caller"), width='stretch')

        summary_df = pd.DataFrame({
            "Metric":["Top Bank","Top Campaign","Top Caller","Transactions","Avg Disbursed"],
            "Value":[top_bank, top_campaign, top_caller, txn_count, format_inr(avg_disb)]
        })
        st.table(summary_df)

# -----------------------------
# COMPARISON DASHBOARD
# -----------------------------
if dashboard_type=="Comparison":
    st.header("📊 Comparison Dashboard")
    managers = sorted(df["Manager"].dropna().unique())
    selected_manager1 = st.selectbox("Select Manager 1", managers)
    selected_manager2 = st.selectbox("Select Manager 2", managers, index=1)

    if selected_manager1 == selected_manager2:
        st.warning("Select different managers")
        st.stop()

    f1 = df[(df["Manager"]==selected_manager1)&(df["Disb Month"]==selected_month)]
    f2 = df[(df["Manager"]==selected_manager2)&(df["Disb Month"]==selected_month)]

    d1,r1,p1,txn1,avg1,top_bank1,top_camp1,top_caller1 = calc_metrics(f1)
    d2,r2,p2,txn2,avg2,top_bank2,top_camp2,top_caller2 = calc_metrics(f2)

    # KPI cards side-by-side
    col1,col2,col3 = st.columns(3)
    col1.metric(f"{selected_manager1} Total Disb", format_inr(d1))
    col2.metric(f"{selected_manager2} Total Disb", format_inr(d2))
    delta_payout = p1 - p2
    arrow = "▲" if delta_payout >=0 else "▼"
    color = "green" if delta_payout >=0 else "red"
    col3.markdown(f"<h3 style='color:{color}'>{arrow} Payout % Delta: {abs(delta_payout):.2f}%</h3>", unsafe_allow_html=True)

    # Charts
    st.plotly_chart(plot_bar(f1,"Bank",top_bank1,selected_manager1,"comp_bank1"), width='stretch')
    st.plotly_chart(plot_bar(f2,"Bank",top_bank2,selected_manager2,"comp_bank2"), width='stretch')

    # Summary table
    summary_df = pd.DataFrame({
        "Metric":["Top Bank","Top Campaign","Top Caller","Transactions","Avg Disbursed"],
        selected_manager1:[top_bank1,top_camp1,top_caller1,txn1,format_inr(avg1)],
        selected_manager2:[top_bank2,top_camp2,top_caller2,txn2,format_inr(avg2)]
    })
    st.table(summary_df)
