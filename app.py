import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from streamlit_autorefresh import st_autorefresh

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(page_title="Manager Dashboard", layout="wide")

# Auto-refresh
st_autorefresh(interval=60 * 1000, key="refresh")

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

def plot_bar(f, col, top_value, manager_name, key):
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
    fig.update_layout(title=f"{manager_name} - {col} wise Disbursement",
                      yaxis_title="Amount (L)", template="plotly_white", height=400)
    return fig

# -----------------------------
# Sidebar Filters
# -----------------------------
st.sidebar.title("Dashboard")
dashboard_type = st.sidebar.radio("Select One", ["Single Manager", "Comparison"])

managers = sorted(df["Manager"].dropna().unique())
months = sorted(df["Disb Month"].dropna().unique())

selected_manager1 = st.sidebar.selectbox("Select Manager 1", managers)
selected_month1 = st.sidebar.selectbox("Select Month 1", months)

if dashboard_type=="Comparison":
    selected_manager2 = st.sidebar.selectbox("Select Manager 2", managers, index=1)
    selected_month2 = st.sidebar.selectbox("Select Month 2", months, index=1)

# -----------------------------
# Single Manager Dashboard
# -----------------------------
if dashboard_type=="Single Manager":
    st.header(f"📊 {selected_manager1} - {selected_month1} Dashboard")

    f = df[(df["Manager"]==selected_manager1)&(df["Disb Month"]==selected_month1)]
    if f.empty:
        st.warning("No data available")
    else:
        total_disb,total_rev,avg_payout,txn_count,avg_disb,top_bank,top_campaign,top_caller = calc_metrics(f)

        # ----------------------------- KPI Cards (Power BI style) -----------------------------
        st.markdown("### KPI Overview")
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("💰 Total Disbursed", format_inr(total_disb))
        col2.metric("📈 Total Revenue", format_inr(total_rev))
        col3.metric("📊 Avg Payout %", f"{avg_payout:.2f}%")
        col4.metric("📝 Transactions", txn_count)
        col5.metric("🏦 Avg Disbursed", format_inr(avg_disb))

        # ----------------------------- Charts -----------------------------
        st.plotly_chart(plot_bar(f,"Bank",top_bank,selected_manager1,"bank1"), use_container_width=True, key="bank1_chart")
        st.plotly_chart(plot_bar(f,"Caller",top_caller,selected_manager1,"caller1"), use_container_width=True, key="caller1_chart")

        summary = f.groupby("Campaign")["Disbursed AMT"].sum()
        fig = go.Figure(go.Pie(labels=summary.index, values=summary.values/100000, hole=0.4))
        fig.update_layout(title=f"{selected_manager1} - Campaign Distribution")
        st.plotly_chart(fig, use_container_width=True, key="pie_chart")

        # Summary insights
        st.markdown("### 📝 Summary Insights")
        st.write(f"Top Bank: {top_bank}")
        st.write(f"Top Campaign: {top_campaign}")
        st.write(f"Top Caller: {top_caller}")

# -----------------------------
# Comparison Dashboard
# -----------------------------
if dashboard_type=="Comparison":
    st.header("📊 Comparison Dashboard")

    if selected_manager1 == selected_manager2:
        st.warning("Select different managers")
        st.stop()

    f1 = df[(df["Manager"]==selected_manager1)&(df["Disb Month"]==selected_month1)]
    f2 = df[(df["Manager"]==selected_manager2)&(df["Disb Month"]==selected_month2)]

    d1,r1,p1,txn1,avg1,top_bank1,top_camp1,top_caller1 = calc_metrics(f1)
    d2,r2,p2,txn2,avg2,top_bank2,top_camp2,top_caller2 = calc_metrics(f2)

    winner = selected_manager1 if d1 > d2 else selected_manager2
    st.success(f"🏆 Top Performer: {winner}")

    # ----------------------------- KPI Cards Comparison -----------------------------
    st.markdown("### KPI Comparison")
    kpis = {
        "Total Disbursed": (d1,d2),
        "Total Revenue": (r1,r2),
        "Avg Payout %": (p1,p2),
        "Transactions": (txn1,txn2),
        "Avg Disbursed": (avg1,avg2)
    }

    for name, (val1,val2) in kpis.items():
        col1, col2 = st.columns(2)
        if val1>val2:
            col1.metric(f"{selected_manager1} {name}", format_inr(val1) if "Disbursed" in name or "Revenue" in name else round(val1,2), delta="↑", delta_color="normal")
            col2.metric(f"{selected_manager2} {name}", format_inr(val2) if "Disbursed" in name or "Revenue" in name else round(val2,2))
        elif val2>val1:
            col1.metric(f"{selected_manager1} {name}", format_inr(val1) if "Disbursed" in name or "Revenue" in name else round(val1,2))
            col2.metric(f"{selected_manager2} {name}", format_inr(val2) if "Disbursed" in name or "Revenue" in name else round(val2,2), delta="↑", delta_color="normal")
        else:
            col1.metric(f"{selected_manager1} {name}", format_inr(val1) if "Disbursed" in name or "Revenue" in name else round(val1,2))
            col2.metric(f"{selected_manager2} {name}", format_inr(val2) if "Disbursed" in name or "Revenue" in name else round(val2,2))

    # Charts
    st.markdown("### Bank-wise Disbursement Comparison")
    st.plotly_chart(plot_bar(f1,"Bank",top_bank1,selected_manager1,"bank1"), use_container_width=True, key="bank1_chart")
    st.plotly_chart(plot_bar(f2,"Bank",top_bank2,selected_manager2,"bank2"), use_container_width=True, key="bank2_chart")

    st.markdown("### Caller-wise Disbursement Comparison")
    st.plotly_chart(plot_bar(f1,"Caller",top_caller1,selected_manager1,"caller1"), use_container_width=True, key="caller1_chart")
    st.plotly_chart(plot_bar(f2,"Caller",top_caller2,selected_manager2,"caller2"), use_container_width=True, key="caller2_chart")

    st.markdown("### Campaign-wise Distribution Comparison")
    summary1 = f1.groupby("Campaign")["Disbursed AMT"].sum()
    summary2 = f2.groupby("Campaign")["Disbursed AMT"].sum()
    fig1 = go.Figure(go.Pie(labels=summary1.index, values=summary1.values/100000, hole=0.4))
    fig1.update_layout(title=f"{selected_manager1} Campaign Distribution")
    fig2 = go.Figure(go.Pie(labels=summary2.index, values=summary2.values/100000, hole=0.4))
    fig2.update_layout(title=f"{selected_manager2} Campaign Distribution")
    st.plotly_chart(fig1, use_container_width=True, key="pie1_chart")
    st.plotly_chart(fig2, use_container_width=True, key="pie2_chart")
