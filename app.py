import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from streamlit_autorefresh import st_autorefresh

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(page_title="Manager Dashboard", layout="wide")

# 🔄 Auto Refresh every 60 sec
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
    txn_count = len(f)
    avg_payout = (total_rev/total_disb)*100 if total_disb else 0
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
        name=manager_name,
        width=0.5
    ))
    fig.update_layout(yaxis_title="Amount (L)", template="plotly_white", height=400)
    return fig

# -----------------------------
# Colored KPI card
# -----------------------------
def colored_kpi(title, value, color="#636EFA", delta=None):
    st.markdown(
        f"""
        <div style="
            background-color:{color};
            padding:15px;
            border-radius:10px;
            text-align:center;
            color:white;
        ">
            <h4>{title}</h4>
            <h2>{value}</h2>
            {'<h4>' + delta + '</h4>' if delta else ''}
        </div>
        """, unsafe_allow_html=True
    )

# -----------------------------
# Sidebar Filters
# -----------------------------
st.sidebar.title("Filters & Dashboards")
dashboard_type = st.sidebar.radio("Select Dashboard", ["All Managers", "Single Manager", "Comparison"])
months = sorted(df["Disb Month"].dropna().unique())
selected_month = st.sidebar.selectbox("Select Month", months)

managers = sorted(df["Manager"].dropna().unique())
selected_manager1 = st.sidebar.selectbox("Manager 1", managers)
if dashboard_type=="Comparison":
    selected_manager2 = st.sidebar.selectbox("Manager 2", managers, index=1)

# -----------------------------
# ALL MANAGERS DASHBOARD
# -----------------------------
if dashboard_type=="All Managers":
    st.header("📊 All Managers Dashboard")
    filtered_df = df[df["Disb Month"]==selected_month]
    filtered_df["Transactions"] = 1
    agg_df = filtered_df.groupby(["Vertical","Manager"]).agg(
        Total_Disbursed=("Disbursed AMT","sum"),
        Total_Revenue=("Total_Revenue","sum"),
        Transactions=("Transactions","sum"),
        Avg_Payout=("Total_Revenue", lambda x: x.sum()/filtered_df.loc[x.index,"Disbursed AMT"].sum()*100 if filtered_df.loc[x.index,"Disbursed AMT"].sum() else 0)
    ).reset_index()
    agg_df = agg_df.sort_values("Vertical")
    st.dataframe(agg_df.style.background_gradient(cmap="Blues"), use_container_width=True)
    st.download_button("Download CSV", agg_df.to_csv(index=False), "all_managers.csv", "text/csv")

# -----------------------------
# SINGLE MANAGER DASHBOARD
# -----------------------------
if dashboard_type=="Single Manager":
    st.header(f"📊 {selected_manager1} - {selected_month} Dashboard")
    f = df[(df["Manager"]==selected_manager1)&(df["Disb Month"]==selected_month)]
    if f.empty:
        st.warning("No data available")
    else:
        total_disb,total_rev,avg_payout,txn_count,avg_disb,top_bank,top_campaign,top_caller = calc_metrics(f)
        col1,col2,col3,col4 = st.columns(4)
        with col1:
            colored_kpi("Total Disbursed", format_inr(total_disb), color="#636EFA")
        with col2:
            colored_kpi("Total Revenue", format_inr(total_rev), color="#EF553B")
        with col3:
            colored_kpi("Avg Payout %", f"{avg_payout:.2f}%", color="#00CC96")
        with col4:
            colored_kpi("Transactions", txn_count, color="#AB63FA")

        st.plotly_chart(plot_bar(f,"Bank",top_bank,selected_manager1,"bank_chart"), width='stretch')
        st.plotly_chart(plot_bar(f,"Caller",top_caller,selected_manager1,"caller_chart"), width='stretch')

        # Campaign Pie
        summary = f.groupby("Campaign")["Disbursed AMT"].sum()
        fig = go.Figure(go.Pie(labels=summary.index, values=summary.values/100000, hole=0.4))
        st.plotly_chart(fig, width='stretch')

        st.markdown("### 📝 Insights")
        st.write(f"Top Bank: {top_bank}")
        st.write(f"Top Campaign: {top_campaign}")
        st.write(f"Top Caller: {top_caller}")
        st.write(f"Transactions: {txn_count}")
        st.write(f"Avg Disbursed: {format_inr(avg_disb)}")

# -----------------------------
# COMPARISON DASHBOARD
# -----------------------------
if dashboard_type=="Comparison":
    st.header("📊 Comparison Dashboard")
    if selected_manager1 == selected_manager2:
        st.warning("Select different managers")
        st.stop()
    f1 = df[(df["Manager"]==selected_manager1)&(df["Disb Month"]==selected_month)]
    f2 = df[(df["Manager"]==selected_manager2)&(df["Disb Month"]==selected_month)]
    d1,r1,p1,txn1,avg1,top_bank1,top_camp1,top_caller1 = calc_metrics(f1)
    d2,r2,p2,txn2,avg2,top_bank2,top_camp2,top_caller2 = calc_metrics(f2)

    # Colorful KPI cards side by side
    col1,col2,col3,col4 = st.columns(4)
    with col1:
        colored_kpi(selected_manager1, format_inr(d1), color="#636EFA")
    with col2:
        colored_kpi(selected_manager2, format_inr(d2), color="#EF553B")
    with col3:
        colored_kpi("Total Revenue", f"{format_inr(r1)} vs {format_inr(r2)}", color="#00CC96")
    with col4:
        colored_kpi("Avg Payout %", f"{p1:.2f}% vs {p2:.2f}%", color="#AB63FA")

    st.plotly_chart(plot_bar(f1,"Bank",top_bank1,selected_manager1,"bank_chart_1"), width='stretch')
    st.plotly_chart(plot_bar(f2,"Bank",top_bank2,selected_manager2,"bank_chart_2"), width='stretch')
    st.plotly_chart(plot_bar(f1,"Caller",top_caller1,selected_manager1,"caller_chart_1"), width='stretch')
    st.plotly_chart(plot_bar(f2,"Caller",top_caller2,selected_manager2,"caller_chart_2"), width='stretch')

    st.markdown("### 📝 Insights")
    st.write(f"{selected_manager1}: Top Bank - {top_bank1}, Top Campaign - {top_camp1}, Top Caller - {top_caller1}, Transactions - {txn1}")
    st.write(f"{selected_manager2}: Top Bank - {top_bank2}, Top Campaign - {top_camp2}, Top Caller - {top_caller2}, Transactions - {txn2}")
