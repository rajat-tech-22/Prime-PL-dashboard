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
# Load Data
# -----------------------------
@st.cache_data(ttl=60)
def load_data():
    url = "https://docs.google.com/spreadsheets/d/1I1ql5NwFafbWXYkVOvv0yvMM9GKnJ5954R4zif2owGI/export?format=csv"
    df = pd.read_csv(url)
    df.replace("null", None, inplace=True)
    df["Avg_Payout"] = (df["Total_Revenue"]/df["Disbursed AMT"]*100).round(2)
    return df

df = load_data()

# -----------------------------
# Sidebar Filters
# -----------------------------
st.sidebar.title("Filters")
dashboard_type = st.sidebar.radio("Select Dashboard", ["All Managers", "Single Manager", "Comparison"])
months = sorted(df["Disb Month"].dropna().unique())
selected_month = st.sidebar.selectbox("Select Month", months)
df = df[df["Disb Month"]==selected_month]

managers = sorted(df["Manager"].dropna().unique())
selected_manager1 = st.sidebar.selectbox("Select Manager 1", managers)
if dashboard_type=="Comparison":
    selected_manager2 = st.sidebar.selectbox("Select Manager 2", managers, index=1)

# -----------------------------
# Helper Functions
# -----------------------------
base_colors = ["#636EFA","#EF553B","#00CC96","#AB63FA","#FFA15A","#19D3F3","#FF6692","#B6E880"]

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

def calc_metrics(f):
    total_disb = f["Disbursed AMT"].sum()
    total_rev = f["Total_Revenue"].sum()
    txn_count = len(f)
    avg_disb = total_disb/txn_count if txn_count else 0
    avg_payout = (total_rev/total_disb*100) if total_disb else 0
    top_bank = f.groupby("Bank")["Disbursed AMT"].sum().idxmax() if not f.empty else "N/A"
    top_campaign = f.groupby("Campaign")["Disbursed AMT"].sum().idxmax() if not f.empty else "N/A"
    top_caller = f.groupby("Caller")["Disbursed AMT"].sum().idxmax() if not f.empty else "N/A"
    return total_disb,total_rev,avg_payout,txn_count,avg_disb,top_bank,top_campaign,top_caller

def plot_bar(f, col, manager_name, key):
    summary = f.groupby(col)["Disbursed AMT"].sum()
    colors = [base_colors[i % len(base_colors)] for i in range(len(summary))]
    fig = go.Figure(go.Bar(
        x=summary.index,
        y=summary.values/100000,
        text=[f"{v/100000:.2f}L" for v in summary.values],
        textposition="auto",
        marker_color=colors,
        name=manager_name
    ))
    fig.update_layout(title=f"{manager_name} - {col} Distribution", yaxis_title="Amount (L)", template="plotly_white", height=400)
    st.plotly_chart(fig, use_container_width=True, key=key)

# -----------------------------
# ALL MANAGERS DASHBOARD
# -----------------------------
if dashboard_type=="All Managers":
    st.header(f"📊 All Managers - {selected_month}")
    
    agg_df = df.groupby(["Vertical","Manager"]).agg(
        Total_Disbursed=("Disbursed AMT","sum"),
        Total_Revenue=("Total_Revenue","sum"),
        Avg_Payout=("Avg_Payout","mean"),
        Transactions=("Manager","count")
    ).reset_index()
    
    # Sort vertical-wise by Total Disbursed
    agg_df.sort_values(["Vertical","Total_Disbursed"], ascending=[True, False], inplace=True)
    
    st.dataframe(agg_df)
    st.download_button("📥 Download CSV", agg_df.to_csv(index=False), file_name="all_managers.csv")

# -----------------------------
# SINGLE MANAGER DASHBOARD
# -----------------------------
elif dashboard_type=="Single Manager":
    st.header(f"📊 {selected_manager1} - {selected_month} Dashboard")
    
    f = df[df["Manager"]==selected_manager1]
    
    if f.empty:
        st.warning("No data available")
    else:
        total_disb,total_rev,avg_payout,txn_count,avg_disb,top_bank,top_campaign,top_caller = calc_metrics(f)

        # KPI Cards
        col1,col2,col3,col4 = st.columns(4)
        col1.metric("Total Disbursed", format_inr(total_disb))
        col2.metric("Total Revenue", format_inr(total_rev))
        col3.metric("Transactions", txn_count)
        col4.metric("Avg Payout %", f"{avg_payout:.2f}%")
        
        # Charts
        plot_bar(f,"Bank",selected_manager1,"bank_single")
        plot_bar(f,"Caller",selected_manager1,"caller_single")
        
        # Campaign Pie
        summary = f.groupby("Campaign")["Disbursed AMT"].sum()
        fig = go.Figure(go.Pie(labels=summary.index, values=summary.values/100000, hole=0.4))
        fig.update_layout(title=f"{selected_manager1} - Campaign Distribution")
        st.plotly_chart(fig, use_container_width=True, key="campaign_single")
        
        # Insights
        st.markdown("### 📝 Insights")
        st.write(f"Top Bank: {top_bank}")
        st.write(f"Top Campaign: {top_campaign}")
        st.write(f"Top Caller: {top_caller}")

# -----------------------------
# COMPARISON DASHBOARD
# -----------------------------
elif dashboard_type=="Comparison":
    st.header(f"📊 Comparison Dashboard - {selected_month}")
    
    if selected_manager1==selected_manager2:
        st.warning("Select different managers")
        st.stop()
    
    f1 = df[df["Manager"]==selected_manager1]
    f2 = df[df["Manager"]==selected_manager2]
    
    d1,r1,p1,t1,avg1,bank1,camp1,caller1 = calc_metrics(f1)
    d2,r2,p2,t2,avg2,bank2,camp2,caller2 = calc_metrics(f2)
    
    # Side by side KPI cards
    col1,col2,col3,col4 = st.columns(4)
    col1.metric(f"{selected_manager1} Disbursed", format_inr(d1))
    col2.metric(f"{selected_manager2} Disbursed", format_inr(d2))
    col3.metric(f"{selected_manager1} Revenue", format_inr(r1))
    col4.metric(f"{selected_manager2} Revenue", format_inr(r2))
    
    col5,col6,col7,col8 = st.columns(4)
    col5.metric(f"{selected_manager1} Avg Payout %", f"{p1:.2f}%")
    col6.metric(f"{selected_manager2} Avg Payout %", f"{p2:.2f}%")
    col7.metric(f"{selected_manager1} Transactions", t1)
    col8.metric(f"{selected_manager2} Transactions", t2)
    
    # Charts
    plot_bar(f1,"Bank",selected_manager1,"bank_comp1")
    plot_bar(f2,"Bank",selected_manager2,"bank_comp2")
    plot_bar(f1,"Caller",selected_manager1,"caller_comp1")
    plot_bar(f2,"Caller",selected_manager2,"caller_comp2")
    
    # Campaign Pie
    fig1 = go.Figure(go.Pie(labels=f1.groupby("Campaign")["Disbursed AMT"].sum().index,
                            values=f1.groupby("Campaign")["Disbursed AMT"].sum().values/100000,
                            hole=0.4))
    fig1.update_layout(title=f"{selected_manager1} Campaign Distribution")
    st.plotly_chart(fig1, key="campaign_comp1")
    
    fig2 = go.Figure(go.Pie(labels=f2.groupby("Campaign")["Disbursed AMT"].sum().index,
                            values=f2.groupby("Campaign")["Disbursed AMT"].sum().values/100000,
                            hole=0.4))
    fig2.update_layout(title=f"{selected_manager2} Campaign Distribution")
    st.plotly_chart(fig2, key="campaign_comp2")
