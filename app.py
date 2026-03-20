import streamlit as st
import pandas as pd
import plotly.graph_objs as go

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(page_title="Manager Dashboard", layout="wide")

# -----------------------------
# Authentication
# -----------------------------
USER_CREDENTIALS = {"admin":"admin123", "manager1":"pass123"}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

def login():
    st.title("🔒 Login Required")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success(f"Welcome, {username}!")
            st.experimental_rerun()
        else:
            st.error("❌ Invalid username or password")

def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.experimental_rerun()

if not st.session_state.logged_in:
    login()
    st.stop()
else:
    st.sidebar.button("Logout", on_click=logout)

# -----------------------------
# Load Data
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
        width=0.4
    ))
    fig.update_layout(yaxis_title="Amount (L)", template="plotly_white", height=400)
    return fig

# -----------------------------
# Sidebar Filters
# -----------------------------
st.sidebar.title(f"Dashboard - User: {st.session_state.username}")
dashboard_type = st.sidebar.radio("Dashboard Type", ["Single Manager","Comparison"])
managers = sorted(df["Manager"].dropna().unique())
months = sorted(df["Disb Month"].dropna().unique())
m1 = st.sidebar.selectbox("Manager 1", managers)
mo1 = st.sidebar.selectbox("Month 1", months)
if dashboard_type=="Comparison":
    m2 = st.sidebar.selectbox("Manager 2", managers, index=1)
    mo2 = st.sidebar.selectbox("Month 2", months, index=1)

# -----------------------------
# SINGLE DASHBOARD
# -----------------------------
if dashboard_type=="Single Manager":
    st.header(f"📊 {m1} - {mo1} Dashboard")
    f = df[(df["Manager"]==m1)&(df["Disb Month"]==mo1)]
    if f.empty:
        st.warning("No data available")
    else:
        total_disb,total_rev,avg_payout,txn_count,avg_disb,top_bank,top_campaign,top_caller = calc_metrics(f)

        # KPI
        c1,c2,c3 = st.columns(3)
        c1.markdown(f"<div style='background:#BBDEFB;padding:20px;border-radius:12px;text-align:center;box-shadow:2px 2px 5px #aaa'><b>Total Disbursed</b><br>{format_inr(total_disb)}</div>", unsafe_allow_html=True)
        c2.markdown(f"<div style='background:#FFE082;padding:20px;border-radius:12px;text-align:center;box-shadow:2px 2px 5px #aaa'><b>Total Revenue</b><br>{format_inr(total_rev)}</div>", unsafe_allow_html=True)
        c3.markdown(f"<div style='background:#C8E6C9;padding:20px;border-radius:12px;text-align:center;box-shadow:2px 2px 5px #aaa'><b>Avg Payout %</b><br>{avg_payout:.2f}%</div>", unsafe_allow_html=True)

        # Trend
        st.subheader("📈 Monthly Disbursed Trend")
        trend = df.groupby("Disb Month")["Disbursed AMT"].sum().reset_index()
        fig_trend = go.Figure(go.Scatter(x=trend["Disb Month"], y=trend["Disbursed AMT"]/100000, mode="lines+markers"))
        st.plotly_chart(fig_trend, use_container_width=True)

        # Tabs
        tab1,tab2,tab3 = st.tabs(["🏦 Bank-wise","📢 Campaign-wise","📞 Caller-wise"])
        with tab1: st.plotly_chart(plot_bar(f,"Bank",top_bank,m1), use_container_width=True)
        with tab2:
            summary = f.groupby("Campaign")["Disbursed AMT"].sum()
            colors = [base_colors[i%len(base_colors)] for i in range(len(summary))]
            fig = go.Figure(go.Pie(labels=summary.index, values=summary.values/100000, hole=0.4, marker=dict(colors=colors)))
            st.plotly_chart(fig, use_container_width=True)
        with tab3: st.plotly_chart(plot_bar(f,"Caller",top_caller,m1), use_container_width=True)

        # Summary & Download
        st.markdown(f"**Top Bank:** {top_bank}, **Top Campaign:** {top_campaign}, **Top Caller:** {top_caller}")
        st.subheader("📄 Raw Data")
        st.dataframe(f)
        csv = f.to_csv(index=False).encode("utf-8")
        st.download_button(f"Download {m1}_{mo1} Data", data=csv, file_name=f"{m1}_{mo1}.csv", mime="text/csv")

# -----------------------------
# COMPARISON DASHBOARD
# -----------------------------
if dashboard_type=="Comparison":
    st.header("📊 Manager Comparison Dashboard")
    f1 = df[(df["Manager"]==m1)&(df["Disb Month"]==mo1)]
    f2 = df[(df["Manager"]==m2)&(df["Disb Month"]==mo2)]
    if f1.empty and f2.empty:
        st.warning("No data for selected managers/months")
    else:
        d1,r1,p1,txn1,avg1,top_bank1,top_camp1,top_caller1 = calc_metrics(f1)
        d2,r2,p2,txn2,avg2,top_bank2,top_camp2,top_caller2 = calc_metrics(f2)

        # KPI Cards
        col1,col2,col3 = st.columns(3)
        col1.markdown(f"<div style='background:#BBDEFB;padding:20px;border-radius:12px;text-align:center;box-shadow:2px 2px 5px #aaa'><b>{m1} Total Disbursed</b><br>{format_inr(d1)}</div>", unsafe_allow_html=True)
        col2.markdown(f"<div style='background:#FFE082;padding:20px;border-radius:12px;text-align:center;box-shadow:2px 2px 5px #aaa'><b>{m2} Total Disbursed</b><br>{format_inr(d2)}</div>", unsafe_allow_html=True)
        col3.markdown(f"<div style='background:#C8E6C9;padding:20px;border-radius:12px;text-align:center;box-shadow:2px 2px 5px #aaa'><b>Avg Payout %</b><br>{p1:.2f}% vs {p2:.2f}%</div>", unsafe_allow_html=True)

        # Trend comparison
        st.subheader("📈 Monthly Trend Comparison")
        trend = df.groupby("Disb Month")["Disbursed AMT"].sum().reset_index()
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(x=trend["Disb Month"], y=trend["Disbursed AMT"]/100000, mode="lines+markers", name="Total Disbursed"))
        st.plotly_chart(fig_trend, use_container_width=True)

        # Tabs
        tab1,tab2,tab3 = st.tabs(["🏦 Bank-wise","📢 Campaign-wise","📞 Caller-wise"])
        # Bank
        with tab1:
            keys = sorted(set(f1["Bank"]).union(set(f2["Bank"])))
            fig = go.Figure()
            for k in keys:
                fig.add_bar(x=[k], y=[f1.groupby("Bank")["Disbursed AMT"].sum().get(k,0)/100000], name=m1, marker_color="#636EFA", width=0.4)
                fig.add_bar(x=[k], y=[f2.groupby("Bank")["Disbursed AMT"].sum().get(k,0)/100000], name=m2, marker_color="#EF553B", width=0.4)
            fig.update_layout(barmode='group', yaxis_title="Amount (L)", template="plotly_white", height=400)
            st.plotly_chart(fig, use_container_width=True)

        # Campaign
        with tab2:
            fig = go.Figure()
            summary1 = f1.groupby("Campaign")["Disbursed AMT"].sum()
            colors1 = [base_colors[i%len(base_colors)] for i in range(len(summary1))]
            fig.add_trace(go.Pie(labels=summary1.index, values=summary1.values/100000, hole=0.4, marker=dict(colors=colors1), name=m1, domain=dict(x=[0,0.48])))
            summary2 = f2.groupby("Campaign")["Disbursed AMT"].sum()
            colors2 = [base_colors[i%len(base_colors)] for i in range(len(summary2))]
            fig.add_trace(go.Pie(labels=summary2.index, values=summary2.values/100000, hole=0.4, marker=dict(colors=colors2), name=m2, domain=dict(x=[0.52,1])))
            fig.update_layout(template="plotly_white", height=400,
                              annotations=[dict(text=m1, x=0.22, y=0.5, font_size=14, showarrow=False),
                                           dict(text=m2, x=0.78, y=0.5, font_size=14, showarrow=False)])
            st.plotly_chart(fig, use_container_width=True)

        # Caller
        with tab3:
            keys = sorted(set(f1["Caller"]).union(set(f2["Caller"])))
            fig = go.Figure()
            for k in keys:
                fig.add_bar(x=[k], y=[f1.groupby("Caller")["Disbursed AMT"].sum().get(k,0)/100000], name=m1, marker_color="#636EFA", width=0.4)
                fig.add_bar(x=[k], y=[f2.groupby("Caller")["Disbursed AMT"].sum().get(k,0)/100000], name=m2, marker_color="#EF553B", width=0.4)
            fig.update_layout(barmode='group', yaxis_title="Amount (L)", template="plotly_white", height=400)
            st.plotly_chart(fig, use_container_width=True)

        # Summary
        st.markdown(f"### 📝 Summary")
        st.markdown(f"<ul style='color:#424242'><li>📌 {m1} - Disbursed: {format_inr(d1)}, Revenue: {format_inr(r1)}, Payout: {p1:.2f}%, Top Bank: {top_bank1}, Top Campaign: {top_camp1}, Top Caller: {top_caller1}</li><li>📌 {m2} - Disbursed: {format_inr(d2)}, Revenue: {format_inr(r2)}, Payout: {p2:.2f}%, Top Bank: {top_bank2}, Top Campaign: {top_camp2}, Top Caller: {top_caller2}</li></ul>", unsafe_allow_html=True)
