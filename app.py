import streamlit as st
import pandas as pd
import plotly.graph_objs as go

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(page_title="Manager Dashboard", layout="wide")

# -----------------------------
# Load CSV
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("data.csv")
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
    for val in index_list:
        colors.append("#FFD700" if val==top_value else base_colors[index_list.get_loc(val)%len(base_colors)])
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

def plot_bar(f, col, top_value, manager_name):
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

        # KPI Cards
        kpi_col1,kpi_col2,kpi_col3 = st.columns(3)
        with kpi_col1:
            st.markdown(f"<div style='background:#BBDEFB;padding:20px;border-radius:12px;text-align:center;box-shadow: 2px 2px 5px #aaa'><b>Total Disbursed</b><br>{format_inr(total_disb)}</div>", unsafe_allow_html=True)
        with kpi_col2:
            st.markdown(f"<div style='background:#FFE082;padding:20px;border-radius:12px;text-align:center;box-shadow: 2px 2px 5px #aaa'><b>Total Revenue</b><br>{format_inr(total_rev)}</div>", unsafe_allow_html=True)
        with kpi_col3:
            st.markdown(f"<div style='background:#C8E6C9;padding:20px;border-radius:12px;text-align:center;box-shadow: 2px 2px 5px #aaa'><b>Avg Payout %</b><br>{avg_payout:.2f}%</div>", unsafe_allow_html=True)

        # Tabs
        tab1,tab2,tab3 = st.tabs(["🏦 Bank-wise","📢 Campaign-wise","📞 Caller-wise"])
        with tab1: st.plotly_chart(plot_bar(f,"Bank",top_bank,selected_manager1), use_container_width=True)

        with tab2:
            summary = f.groupby("Campaign")["Disbursed AMT"].sum()
            colors = [base_colors[i%len(base_colors)] for i in range(len(summary))]
            fig = go.Figure(go.Pie(
                labels=summary.index,
                values=summary.values/100000,
                hole=0.4,
                marker=dict(colors=colors)
            ))
            st.plotly_chart(fig, use_container_width=True)

        with tab3: st.plotly_chart(plot_bar(f,"Caller",top_caller,selected_manager1), use_container_width=True)

        # Summary
        st.markdown("### 📝 Summary & Insights")
        st.markdown(f"<ul style='color:#424242'><li>📌 Top Bank: {top_bank}</li><li>📌 Top Campaign: {top_campaign}</li><li>📌 Top Caller: {top_caller}</li></ul>", unsafe_allow_html=True)

        # Raw Data
        st.subheader("📄 Raw Data")
        st.dataframe(f)
        csv = f.to_csv(index=False).encode("utf-8")
        st.download_button(f"Download {selected_manager1}_{selected_month1} Data", data=csv, file_name=f"{selected_manager1}_{selected_month1}.csv", mime="text/csv")

# -----------------------------
# COMPARISON DASHBOARD
# -----------------------------
if dashboard_type=="Comparison":
    st.header(f"📊 Comparison Dashboard")
    f1 = df[(df["Manager"]==selected_manager1)&(df["Disb Month"]==selected_month1)]
    f2 = df[(df["Manager"]==selected_manager2)&(df["Disb Month"]==selected_month2)]

    if f1.empty and f2.empty:
        st.warning("No data available for selected managers/months")
    else:
        d1,r1,p1,txn1,avg1,top_bank1,top_camp1,top_caller1 = calc_metrics(f1)
        d2,r2,p2,txn2,avg2,top_bank2,top_camp2,top_caller2 = calc_metrics(f2)

        # -----------------------------
        # Delta function
        # -----------------------------
        def color_delta(value):
            if isinstance(value,float):
                return f"<span style='color:green'>+{value:.2f}</span>" if value>=0 else f"<span style='color:red'>{value:.2f}</span>"
            return f"<span style='color:green'>+{format_inr(value)}</span>" if value>=0 else f"<span style='color:red'>{format_inr(value)}</span>"

        # -----------------------------
        # KPI Cards
        # -----------------------------
        kpi_col1,kpi_col2,kpi_col3 = st.columns(3)
        # Manager 1 Card
        kpi_col1.markdown(f"""
        <div style='background:#BBDEFB;padding:20px;border-radius:12px;text-align:center;box-shadow:2px 2px 5px #aaa'>
            <b>{selected_manager1} - {selected_month1}</b><br><br>
            Total Disbursed: {format_inr(d1)}<br>Δ vs {selected_manager2}: {color_delta(d1-d2)}<br>
            Total Revenue: {format_inr(r1)}<br>Δ vs {selected_manager2}: {color_delta(r1-r2)}<br>
            Avg Payout: {p1:.2f}%<br>Δ vs {selected_manager2}: <span style='color:{"green" if p1-p2>=0 else "red"}'>{p1-p2:.2f}%</span>
        </div>
        """, unsafe_allow_html=True)
        # Manager 2 Card
        kpi_col2.markdown(f"""
        <div style='background:#FFE082;padding:20px;border-radius:12px;text-align:center;box-shadow:2px 2px 5px #aaa'>
            <b>{selected_manager2} - {selected_month2}</b><br><br>
            Total Disbursed: {format_inr(d2)}<br>Δ vs {selected_manager1}: {color_delta(d2-d1)}<br>
            Total Revenue: {format_inr(r2)}<br>Δ vs {selected_manager1}: {color_delta(r2-r1)}<br>
            Avg Payout: {p2:.2f}%<br>Δ vs {selected_manager1}: <span style='color:{"green" if p2-p1>=0 else "red"}'>{p2-p1:.2f}%</span>
        </div>
        """, unsafe_allow_html=True)
        # Comparison Summary Card
        kpi_col3.markdown(f"""
        <div style='background:#C8E6C9;padding:20px;border-radius:12px;text-align:center;box-shadow:2px 2px 5px #aaa'>
            <b>Comparison Summary</b><br><br>
            Total Disbursed Δ: {color_delta(d1-d2)}<br>
            Revenue Δ: {color_delta(r1-r2)}<br>
            Avg Payout Δ: <span style='color:{"green" if p1-p2>=0 else "red"}'>{p1-p2:.2f}%</span><br><br>
            Top Bank: {top_bank1} vs {top_bank2}<br>
            Top Campaign: {top_camp1} vs {top_camp2}<br>
            Top Caller: {top_caller1} vs {top_caller2}
        </div>
        """, unsafe_allow_html=True)
