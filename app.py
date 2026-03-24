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
st.sidebar.title("Filters")
dashboard_type = st.sidebar.radio("Select Dashboard", ["All Managers", "Single Manager", "Comparison"])

verticals = ["All"] + sorted(df["Vertical"].dropna().unique())
months = sorted(df["Disb Month"].dropna().unique())

latest_month_index = len(months)-1

# Filters
if dashboard_type == "All Managers":
    selected_month = st.sidebar.selectbox("Select Month", months, index=latest_month_index)
    selected_vertical = st.sidebar.selectbox("Business Vertical", verticals)
    
    filtered_for_campaigns = df.copy()
    if selected_vertical != "All":
        filtered_for_campaigns = filtered_for_campaigns[filtered_for_campaigns["Vertical"]==selected_vertical]
    if selected_month:
        filtered_for_campaigns = filtered_for_campaigns[filtered_for_campaigns["Disb Month"]==selected_month]
    campaigns_available = sorted(filtered_for_campaigns["Campaign"].dropna().unique())
    selected_campaigns = st.sidebar.multiselect("Campaigns", campaigns_available, default=campaigns_available)

elif dashboard_type == "Single Manager":
    managers = sorted(df["Manager"].dropna().unique())
    selected_manager = st.sidebar.selectbox("Select Manager", managers)
    selected_month = st.sidebar.selectbox("Select Month", months, index=latest_month_index)
    
    filtered_for_campaigns = df[(df["Manager"]==selected_manager)]
    if selected_month:
        filtered_for_campaigns = filtered_for_campaigns[filtered_for_campaigns["Disb Month"]==selected_month]
    campaigns_available = sorted(filtered_for_campaigns["Campaign"].dropna().unique())
    selected_campaigns = st.sidebar.multiselect("Campaigns", campaigns_available, default=campaigns_available)

elif dashboard_type == "Comparison":
    managers = sorted(df["Manager"].dropna().unique())
    selected_manager1 = st.sidebar.selectbox("Select First Manager", managers)
    selected_month1 = st.sidebar.selectbox("Month for First Manager", months, index=latest_month_index)
    
    selected_manager2 = st.sidebar.selectbox("Select Second Manager", managers)
    selected_month2 = st.sidebar.selectbox("Month for Second Manager", months, index=latest_month_index)

# -----------------------------
# Single Manager Dashboard
# -----------------------------
if dashboard_type == "Single Manager":
    st.header(f"📈 Insights - {selected_manager}")

    f = df[(df["Manager"]==selected_manager)&(df["Disb Month"]==selected_month)]
    if selected_campaigns:
        f = f[f["Campaign"].isin(selected_campaigns)]

    if f.empty:
        st.warning("No data available")
    else:
        total_disb,total_rev,avg_payout,txn_count,avg_disb,top_bank,top_campaign,top_caller = calc_metrics(f)
        
        # ✅ Insights Card
        st.markdown("### 📝 Key Metrics")
        col1, col2, col3, col4 = st.columns(4)
        with col1: colored_metric("Total Disbursed", format_inr(total_disb), "#636EFA")
        with col2: colored_metric("Total Revenue", format_inr(total_rev), "#00CC96")
        with col3: colored_metric("Avg Payout %", f"{avg_payout:.2f}%", "#EF553B")
        with col4: colored_metric("Transactions", txn_count, "#FFA15A")
        
        # Graphs & Pie
        st.plotly_chart(plot_bar(f,"Bank",top_bank,selected_manager,"bank1"), use_container_width=True)
        st.plotly_chart(plot_bar(f,"Caller",top_caller,selected_manager,"caller1"), use_container_width=True)
        summary = f.groupby("Campaign")["Disbursed AMT"].sum()
        fig = go.Figure(go.Pie(labels=summary.index, values=summary.values/100000, hole=0.4))
        fig.update_layout(title="Campaign Distribution")
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("### 📄 Data")
        st.dataframe(f, use_container_width=True, height=400)
        st.download_button("Download CSV", f.to_csv(index=False), "single_manager.csv", "text/csv")

# -----------------------------
# Comparison Dashboard
# -----------------------------
if dashboard_type == "Comparison":
    st.header("⚖️ Manager Benchmark")

    if selected_manager1 == selected_manager2:
        st.warning("Select different managers")
        st.stop()

    f1 = df[(df["Manager"]==selected_manager1)&(df["Disb Month"]==selected_month1)]
    f2 = df[(df["Manager"]==selected_manager2)&(df["Disb Month"]==selected_month2)]

    d1,r1,p1,txn1,avg1,top_bank1,top_camp1,top_caller1 = calc_metrics(f1)
    d2,r2,p2,txn2,avg2,top_bank2,top_camp2,top_caller2 = calc_metrics(f2)

    # ✅ Two Cards Side by Side
    st.markdown("### 📝 Key Metrics Comparison")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**{selected_manager1}**")
        colored_metric("Total Disbursed", format_inr(d1), "#636EFA")
        colored_metric("Total Revenue", format_inr(r1), "#00CC96")
        colored_metric("Avg Payout %", f"{p1:.2f}%", "#EF553B")
        colored_metric("Transactions", txn1, "#FFA15A")
    with col2:
        st.markdown(f"**{selected_manager2}**")
        colored_metric("Total Disbursed", format_inr(d2), "#636EFA")
        colored_metric("Total Revenue", format_inr(r2), "#00CC96")
        colored_metric("Avg Payout %", f"{p2:.2f}%", "#EF553B")
        colored_metric("Transactions", txn2, "#FFA15A")

    # Graphs remain
    st.plotly_chart(plot_bar(f1,"Bank",top_bank1,selected_manager1,"bank_cmp1"), use_container_width=True)
    st.plotly_chart(plot_bar(f2,"Bank",top_bank2,selected_manager2,"bank_cmp2"), use_container_width=True)
    st.plotly_chart(plot_bar(f1,"Caller",top_caller1,selected_manager1,"caller_cmp1"), use_container_width=True)
    st.plotly_chart(plot_bar(f2,"Caller",top_caller2,selected_manager2,"caller_cmp2"), use_container_width=True)

    st.markdown("### 📄 Insights")
    st.write(f"{selected_manager1}: Top Bank {top_bank1}, Top Campaign {top_camp1}, Top Caller {top_caller1}, Transactions {txn1}")
    st.write(f"{selected_manager2}: Top Bank {top_bank2}, Top Campaign {top_camp2}, Top Caller {top_caller2}, Transactions {txn2}")
