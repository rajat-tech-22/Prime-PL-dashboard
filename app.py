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

# KPI Card
def colored_metric(label, value, color="#000000"):
    st.markdown(f"""
        <div style="background-color:{color}; padding:20px; border-radius:10px; text-align:center; color:white;">
            <h4>{label}</h4>
            <h2>{value}</h2>
        </div>
    """, unsafe_allow_html=True)

# -----------------------------
# Sidebar Filters
# -----------------------------
st.sidebar.title("Filters")

dashboard_type = st.sidebar.radio("Select Dashboard", ["All Managers", "Single Manager", "Comparison"])

verticals = ["All"] + sorted(df["Vertical"].dropna().unique())
months = sorted(df["Disb Month"].dropna().unique())
managers = sorted(df["Manager"].dropna().unique())

if dashboard_type == "All Managers":
    selected_month1 = st.sidebar.selectbox("Select Reporting Month", months)
    selected_vertical = st.sidebar.selectbox("Choose Business Vertical", verticals)

elif dashboard_type == "Single Manager":
    selected_manager1 = st.sidebar.selectbox("Select Manager", managers)
    selected_month1_m1 = st.sidebar.selectbox("Select Performance Month", months)

elif dashboard_type == "Comparison":
    selected_manager1 = st.sidebar.selectbox("Select First Manager", managers)
    selected_month1 = st.sidebar.selectbox("Select Month for First Manager", months)
    selected_manager2 = st.sidebar.selectbox("Select Second Manager", managers)
    selected_month2 = st.sidebar.selectbox("Select Month for Second Manager", months)

# -----------------------------
# SINGLE MANAGER
# -----------------------------
if dashboard_type=="Single Manager":
    st.header("📈 Manager Insights")

    f = df[(df["Manager"]==selected_manager1)&(df["Disb Month"]==selected_month1_m1)]

    if f.empty:
        st.warning("No data available")
    else:
        total_disb,total_rev,avg_payout,txn_count,avg_disb,top_bank,top_campaign,top_caller = calc_metrics(f)

        col1,col2,col3,col4 = st.columns(4)
        with col1: colored_metric("Total Disbursed", format_inr(total_disb), "#636EFA")
        with col2: colored_metric("Total Revenue", format_inr(total_rev), "#00CC96")
        with col3: colored_metric("Avg Payout %", f"{avg_payout:.2f}%", "#EF553B")
        with col4: colored_metric("Transactions", txn_count, "#FFA15A")

        st.plotly_chart(plot_bar(f,"Bank",top_bank,selected_manager1,"bank1"), use_container_width=True)
        st.plotly_chart(plot_bar(f,"Caller",top_caller,selected_manager1,"caller1"), use_container_width=True)

        # ✅ BULLET INSIGHTS
        st.markdown("### 📝 Key Insights")
        st.markdown(f"""
- 🏦 **Top Performing Bank:** {top_bank}  
- 📣 **Best Campaign:** {top_campaign}  
- 📞 **Top Caller:** {top_caller}  
- 🔢 **Total Transactions:** {txn_count}  
- 💰 **Average Disbursed Value:** {format_inr(avg_disb)}  
- 📊 **Payout Efficiency:** {avg_payout:.2f}%  
""")

# -----------------------------
# COMPARISON
# -----------------------------
if dashboard_type=="Comparison":
    st.header("⚖️ Manager Benchmark")

    f1 = df[(df["Manager"]==selected_manager1)&(df["Disb Month"]==selected_month1)]
    f2 = df[(df["Manager"]==selected_manager2)&(df["Disb Month"]==selected_month2)]

    d1,r1,p1,txn1,avg1,top_bank1,top_camp1,top_caller1 = calc_metrics(f1)
    d2,r2,p2,txn2,avg2,top_bank2,top_camp2,top_caller2 = calc_metrics(f2)

    col1,col2,col3,col4 = st.columns(4)
    with col1: colored_metric(selected_manager1, format_inr(d1), "#636EFA")
    with col2: colored_metric(selected_manager2, format_inr(d2), "#00CC96")
    with col3: colored_metric("Revenue", f"{format_inr(r1)} vs {format_inr(r2)}", "#EF553B")
    with col4: colored_metric("Payout %", f"{p1:.2f}% vs {p2:.2f}%", "#FFA15A")

    # ✅ BULLET INSIGHTS
    st.markdown("### 📝 Key Insights")
    st.markdown(f"""
#### 🔹 {selected_manager1}
- 🏦 Top Bank: {top_bank1}  
- 📣 Top Campaign: {top_camp1}  
- 📞 Top Caller: {top_caller1}  
- 🔢 Transactions: {txn1}  
- 💰 Avg Disbursed: {format_inr(avg1)}  

#### 🔹 {selected_manager2}
- 🏦 Top Bank: {top_bank2}  
- 📣 Top Campaign: {top_camp2}  
- 📞 Top Caller: {top_caller2}  
- 🔢 Transactions: {txn2}  
- 💰 Avg Disbursed: {format_inr(avg2)}  
""")
