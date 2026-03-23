import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from streamlit_autorefresh import st_autorefresh
from io import BytesIO

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(page_title="Manager Dashboard", layout="wide")
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
    fig.update_layout(title=f"{manager_name} - {col} wise Disbursed Amount", yaxis_title="Amount (L)", template="plotly_white", height=400)
    return fig

def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

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
# SINGLE DASHBOARD
# -----------------------------
if dashboard_type=="Single Manager":
    st.header(f"📊 {selected_manager1} - {selected_month1} Dashboard")
    f = df[(df["Manager"]==selected_manager1)&(df["Disb Month"]==selected_month1)]

    if f.empty:
        st.warning("No data available")
    else:
        total_disb,total_rev,avg_payout,txn_count,avg_disb,top_bank,top_campaign,top_caller = calc_metrics(f)

        # Colorful KPI Cards
        col1,col2,col3 = st.columns(3)
        col1.markdown(f'<div style="background-color:#FFD700;padding:15px;border-radius:10px;text-align:center;"><h4>Total Disbursed</h4><p>{format_inr(total_disb)}</p></div>', unsafe_allow_html=True)
        col2.markdown(f'<div style="background-color:#00CC96;padding:15px;border-radius:10px;text-align:center;"><h4>Total Revenue</h4><p>{format_inr(total_rev)}</p></div>', unsafe_allow_html=True)
        col3.markdown(f'<div style="background-color:#FF6692;padding:15px;border-radius:10px;text-align:center;"><h4>Avg Payout %</h4><p>{avg_payout:.2f}%</p></div>', unsafe_allow_html=True)

        # Charts
        st.plotly_chart(plot_bar(f,"Bank",top_bank,selected_manager1,key="single_bank"), use_container_width=True)
        st.plotly_chart(plot_bar(f,"Caller",top_caller,selected_manager1,key="single_caller"), use_container_width=True)

        # Campaign Pie
        summary = f.groupby("Campaign")["Disbursed AMT"].sum()
        fig = go.Figure(go.Pie(
            labels=summary.index,
            values=summary.values/100000,
            hole=0.4
        ))
        fig.update_layout(title=f"{selected_manager1} - Campaign-wise Distribution")
        st.plotly_chart(fig, use_container_width=True)

        # Summary Insights
        st.markdown("### 📝 Insights")
        st.write(f"Top Bank: {top_bank}")
        st.write(f"Top Campaign: {top_campaign}")
        st.write(f"Top Caller: {top_caller}")
        st.write(f"Transactions: {txn_count}")
        st.write(f"Avg Disbursed: {format_inr(avg_disb)}")

        # Show Data and Download
        st.markdown("### 📋 Data Table")
        st.dataframe(f)
        csv = convert_df_to_csv(f)
        st.download_button("Download CSV", csv, file_name=f"{selected_manager1}_{selected_month1}.csv", mime='text/csv')

# -----------------------------
# COMPARISON DASHBOARD
# -----------------------------
if dashboard_type == "Comparison":
    st.header("📊 Comparison Dashboard")

    if selected_manager1 == selected_manager2:
        st.warning("Select different managers")
        st.stop()

    f1 = df[(df["Manager"]==selected_manager1)&(df["Disb Month"]==selected_month1)]
    f2 = df[(df["Manager"]==selected_manager2)&(df["Disb Month"]==selected_month2)]

    d1, r1, p1, txn1, avg1, top_bank1, top_camp1, top_caller1 = calc_metrics(f1)
    d2, r2, p2, txn2, avg2, top_bank2, top_camp2, top_caller2 = calc_metrics(f2)

    # Colorful KPI Cards
    col1,col2,col3 = st.columns(3)
    col1.markdown(f'<div style="background-color:#FFD700;padding:15px;border-radius:10px;text-align:center;"><h4>{selected_manager1}</h4><p>Total Disbursed: {format_inr(d1)}</p><p>Total Revenue: {format_inr(r1)}</p><p>Avg Payout: {p1:.2f}%</p></div>', unsafe_allow_html=True)
    col2.markdown(f'<div style="background-color:#00CC96;padding:15px;border-radius:10px;text-align:center;"><h4>{selected_manager2}</h4><p>Total Disbursed: {format_inr(d2)}</p><p>Total Revenue: {format_inr(r2)}</p><p>Avg Payout: {p2:.2f}%</p></div>', unsafe_allow_html=True)
    delta_disb = d1 - d2
    delta_color = "green" if delta_disb > 0 else "red"
    col3.markdown(f'<div style="background-color:#FFA15A;padding:15px;border-radius:10px;text-align:center;"><h4>Delta Disbursed</h4><p style="color:{delta_color};font-size:24px;">{"▲" if delta_disb>0 else "▼"} {format_inr(abs(delta_disb))}</p></div>', unsafe_allow_html=True)

    # Charts with manager names
    st.subheader("Bank-wise Disbursed Amount")
    st.plotly_chart(plot_bar(f1, "Bank", top_bank1, selected_manager1, key="bank_chart_cmp1"), use_container_width=True)
    st.plotly_chart(plot_bar(f2, "Bank", top_bank2, selected_manager2, key="bank_chart_cmp2"), use_container_width=True)

    st.subheader("Caller-wise Disbursed Amount")
    st.plotly_chart(plot_bar(f1, "Caller", top_caller1, selected_manager1, key="caller_chart_cmp1"), use_container_width=True)
    st.plotly_chart(plot_bar(f2, "Caller", top_caller2, selected_manager2, key="caller_chart_cmp2"), use_container_width=True)

    # Campaign Summary
    st.subheader("Campaign-wise Summary")
    summary1 = f1.groupby("Campaign")["Disbursed AMT"].sum()
    summary2 = f2.groupby("Campaign")["Disbursed AMT"].sum()
    fig_cmp = go.Figure()
    fig_cmp.add_trace(go.Bar(
        x=summary1.index, y=summary1.values/100000,
        name=selected_manager1, marker_color="#FFD700"
    ))
    fig_cmp.add_trace(go.Bar(
        x=summary2.index, y=summary2.values/100000,
        name=selected_manager2, marker_color="#00CC96"
    ))
    fig_cmp.update_layout(title="Campaign-wise Disbursed Amount", yaxis_title="Amount (L)", template="plotly_white", barmode="group", height=400)
    st.plotly_chart(fig_cmp, use_container_width=True)

    # Comparison Insights
    st.markdown("### 📝 Insights")
    st.write(f"{selected_manager1}: Top Bank: {top_bank1}, Top Campaign: {top_camp1}, Top Caller: {top_caller1}, Transactions: {txn1}, Avg Disbursed: {format_inr(avg1)}")
    st.write(f"{selected_manager2}: Top Bank: {top_bank2}, Top Campaign: {top_camp2}, Top Caller: {top_caller2}, Transactions: {txn2}, Avg Disbursed: {format_inr(avg2)}")

    # Show Data and Download
    st.markdown("### 📋 Data Table - Manager 1")
    st.dataframe(f1)
    csv1 = convert_df_to_csv(f1)
    st.download_button(f"Download CSV - {selected_manager1}", csv1, file_name=f"{selected_manager1}_{selected_month1}.csv", mime='text/csv')

    st.markdown("### 📋 Data Table - Manager 2")
    st.dataframe(f2)
    csv2 = convert_df_to_csv(f2)
    st.download_button(f"Download CSV - {selected_manager2}", csv2, file_name=f"{selected_manager2}_{selected_month2}.csv", mime='text/csv')
