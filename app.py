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
# SINGLE MANAGER DASHBOARD
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
            st.markdown(f"<div style='background:#BBDEFB;padding:20px;border-radius:12px;text-align:center'><b>Total Disbursed</b><br>{format_inr(total_disb)}</div>", unsafe_allow_html=True)
        with kpi_col2:
            st.markdown(f"<div style='background:#FFE082;padding:20px;border-radius:12px;text-align:center'><b>Total Revenue</b><br>{format_inr(total_rev)}</div>", unsafe_allow_html=True)
        with kpi_col3:
            st.markdown(f"<div style='background:#C8E6C9;padding:20px;border-radius:12px;text-align:center'><b>Avg Payout %</b><br>{avg_payout:.2f}%</div>", unsafe_allow_html=True)

        # -----------------------------
        # Charts
        # -----------------------------
        st.markdown("### 📊 Charts")

        # Bank-wise
        fig_bank = plot_bar(f,"Bank",top_bank,selected_manager1)
        st.plotly_chart(fig_bank, use_container_width=True)

        # Caller-wise
        fig_caller = plot_bar(f,"Caller",top_caller,selected_manager1)
        st.plotly_chart(fig_caller, use_container_width=True)

        # Campaign Pie
        summary = f.groupby("Campaign")["Disbursed AMT"].sum()
        colors = [base_colors[i%len(base_colors)] for i in range(len(summary))]
        fig_campaign = go.Figure(go.Pie(
            labels=summary.index,
            values=summary.values/100000,
            hole=0.4,
            marker=dict(colors=colors)
        ))
        st.plotly_chart(fig_campaign, use_container_width=True)

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

        # KPI CARDS
        col1,col2,col3 = st.columns(3)
        def kpi_card(manager, total_disb, total_rev, avg_payout, month):
            st.markdown(f"""
                <div style='background:#BBDEFB;padding:15px;border-radius:12px;text-align:center;box-shadow:2px 2px 5px #aaa'>
                    <b>{manager} - {month} KPIs</b><br>
                    Total Disbursed: {format_inr(total_disb)}<br>
                    Total Revenue: {format_inr(total_rev)}<br>
                    Avg Payout: <span style='color:{"green" if avg_payout>=0 else "red"}'>{avg_payout:.2f}%</span>
                </div>
            """, unsafe_allow_html=True)

        with col1: kpi_card(selected_manager1, d1, r1, p1, selected_month1)
        with col2: kpi_card(selected_manager2, d2, r2, p2, selected_month2)
        with col3:
            diff_disb = d1-d2
            diff_rev = r1-r2
            diff_payout = p1-p2
            st.markdown(f"""
                <div style='background:#FFE082;padding:15px;border-radius:12px;text-align:center;box-shadow:2px 2px 5px #aaa'>
                    <b>Difference (M1 - M2)</b><br>
                    Disbursed: <span style='color:{"green" if diff_disb>=0 else "red"}'>{format_inr(diff_disb)}</span><br>
                    Revenue: <span style='color:{"green" if diff_rev>=0 else "red"}'>{format_inr(diff_rev)}</span><br>
                    Payout: <span style='color:{"green" if diff_payout>=0 else "red"}'>{diff_payout:.2f}%</span>
                </div>
            """, unsafe_allow_html=True)

        # -----------------------------
        # Comparison Charts
        # -----------------------------
        st.markdown("### 📊 Comparison Charts")

        # Bank-wise
        keys = sorted(set(f1["Bank"]).union(set(f2["Bank"])))
        fig_bank = go.Figure()
        for k in keys:
            fig_bank.add_bar(
                x=[k],
                y=[f1.groupby("Bank")["Disbursed AMT"].sum().get(k,0)/100000],
                name=selected_manager1, marker_color="#636EFA", width=0.4)
            fig_bank.add_bar(
                x=[k],
                y=[f2.groupby("Bank")["Disbursed AMT"].sum().get(k,0)/100000],
                name=selected_manager2, marker_color="#EF553B", width=0.4)
        fig_bank.update_layout(barmode='group', yaxis_title="Amount (L)", template="plotly_white", height=400)
        st.plotly_chart(fig_bank, use_container_width=True)

        # Caller-wise
        keys = sorted(set(f1["Caller"]).union(set(f2["Caller"])))
        fig_caller = go.Figure()
        for k in keys:
            fig_caller.add_bar(
                x=[k],
                y=[f1.groupby("Caller")["Disbursed AMT"].sum().get(k,0)/100000],
                name=selected_manager1, marker_color="#636EFA", width=0.4)
            fig_caller.add_bar(
                x=[k],
                y=[f2.groupby("Caller")["Disbursed AMT"].sum().get(k,0)/100000],
                name=selected_manager2, marker_color="#EF553B", width=0.4)
        fig_caller.update_layout(barmode='group', yaxis_title="Amount (L)", template="plotly_white", height=400)
        st.plotly_chart(fig_caller, use_container_width=True)

        # Campaign Pie Charts side-by-side
        summary1 = f1.groupby("Campaign")["Disbursed AMT"].sum()
        summary2 = f2.groupby("Campaign")["Disbursed AMT"].sum()
        colors1 = [base_colors[i%len(base_colors)] for i in range(len(summary1))]
        colors2 = [base_colors[i%len(base_colors)] for i in range(len(summary2))]

        fig_campaign = go.Figure()
        fig_campaign.add_trace(go.Pie(
            labels=summary1.index, values=summary1.values/100000, hole=0.4,
            marker=dict(colors=colors1), name=selected_manager1, domain=dict(x=[0,0.48])
        ))
        fig_campaign.add_trace(go.Pie(
            labels=summary2.index, values=summary2.values/100000, hole=0.4,
            marker=dict(colors=colors2), name=selected_manager2, domain=dict(x=[0.52,1])
        ))
        fig_campaign.update_layout(template="plotly_white", height=400,
            annotations=[dict(text=selected_manager1, x=0.22, y=0.5, font_size=14, showarrow=False),
                         dict(text=selected_manager2, x=0.78, y=0.5, font_size=14, showarrow=False)]
        )
        st.plotly_chart(fig_campaign, use_container_width=True)
