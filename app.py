import streamlit as st
import pandas as pd
import plotly.graph_objs as go

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(page_title="Manager Dashboard", layout="wide")

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
# Dark Mode Toggle
# -----------------------------
dark_mode = st.sidebar.toggle("🌙 Dark Mode")

if dark_mode:
    bg = "#0E1117"
    text = "white"
else:
    bg = "white"
    text = "black"

st.markdown(f"""
<style>
body {{
    background-color: {bg};
    color: {text};
}}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Helper Functions
# -----------------------------
def format_inr(number):
    if number is None or number == 0:
        return "₹0"
    return f"₹{int(number):,}"

colors = ["#636EFA","#EF553B","#00CC96","#AB63FA","#FFA15A","#19D3F3","#FF6692","#B6E880"]

def calc_metrics(f):
    d = f["Disbursed AMT"].sum()
    r = f["Total_Revenue"].sum()
    p = (r/d)*100 if d else 0
    top_bank = f.groupby("Bank")["Disbursed AMT"].sum().idxmax() if not f.empty else "N/A"
    top_campaign = f.groupby("Campaign")["Disbursed AMT"].sum().idxmax() if not f.empty else "N/A"
    top_caller = f.groupby("Caller")["Disbursed AMT"].sum().idxmax() if not f.empty else "N/A"
    return d,r,p,top_bank,top_campaign,top_caller

def donut(data, title):
    fig = go.Figure(go.Pie(
        labels=data.index,
        values=data.values/100000,
        hole=0.5,
        marker=dict(colors=[colors[i%len(colors)] for i in range(len(data))])
    ))
    fig.update_layout(title=title, template="plotly_white")
    return fig

def bar(f, col):
    g = f.groupby(col)["Disbursed AMT"].sum()
    fig = go.Figure(go.Bar(
        x=g.index,
        y=g.values/100000,
        text=[f"{v/100000:.2f}L" for v in g.values],
        textposition="auto",
        marker_color=[colors[i%len(colors)] for i in range(len(g))]
    ))
    fig.update_layout(template="plotly_white")
    return fig

# -----------------------------
# Sidebar Filters
# -----------------------------
st.sidebar.title("⚙️ Settings")

dashboard_type = st.sidebar.radio("Dashboard Type", ["Single", "Comparison"])

managers = sorted(df["Manager"].dropna().unique())
months = sorted(df["Disb Month"].dropna().unique())

m1 = st.sidebar.selectbox("Manager 1", managers)
mo1 = st.sidebar.selectbox("Month 1", months)

if dashboard_type == "Comparison":
    m2 = st.sidebar.selectbox("Manager 2", managers, index=1)
    mo2 = st.sidebar.selectbox("Month 2", months, index=1)

# -----------------------------
# SINGLE DASHBOARD
# -----------------------------
if dashboard_type == "Single":

    st.title(f"📊 {m1} - {mo1}")

    f = df[(df["Manager"]==m1)&(df["Disb Month"]==mo1)]

    if f.empty:
        st.warning("No Data Available")
    else:
        d,r,p,top_bank,top_campaign,top_caller = calc_metrics(f)

        # KPI
        c1,c2,c3 = st.columns(3)
        c1.metric("Total Disbursed", format_inr(d))
        c2.metric("Total Revenue", format_inr(r))
        c3.metric("Avg Payout %", f"{p:.2f}%")

        # Charts
        tab1,tab2,tab3 = st.tabs(["Bank","Campaign","Caller"])
        with tab1: st.plotly_chart(bar(f,"Bank"), use_container_width=True)
        with tab2: st.plotly_chart(donut(f.groupby("Campaign")["Disbursed AMT"].sum(),"Campaign"), use_container_width=True)
        with tab3: st.plotly_chart(bar(f,"Caller"), use_container_width=True)

        # Trend
        st.subheader("📈 Trend")
        trend = df.groupby("Disb Month")["Disbursed AMT"].sum().reset_index()
        fig = go.Figure(go.Scatter(x=trend["Disb Month"], y=trend["Disbursed AMT"]/100000, mode="lines+markers"))
        st.plotly_chart(fig, use_container_width=True)

        # AI Insight
        st.subheader("🧠 AI Insight")
        best = df.groupby("Manager")["Disbursed AMT"].sum().idxmax()
        st.success(f"🏆 Best Manager: {best}")

        # Summary
        st.markdown(f"""
        ### 📝 Summary
        - Top Bank: **{top_bank}**
        - Top Campaign: **{top_campaign}**
        - Top Caller: **{top_caller}**
        """)

        st.dataframe(f)

# -----------------------------
# COMPARISON DASHBOARD
# -----------------------------
else:

    st.title("📊 Comparison")

    f1 = df[(df["Manager"]==m1)&(df["Disb Month"]==mo1)]
    f2 = df[(df["Manager"]==m2)&(df["Disb Month"]==mo2)]

    if f1.empty or f2.empty:
        st.warning("Data Missing")
    else:
        d1,r1,p1,top_bank1,top_camp1,top_call1 = calc_metrics(f1)
        d2,r2,p2,top_bank2,top_camp2,top_call2 = calc_metrics(f2)

        # KPI
        c1,c2,c3 = st.columns(3)
        c1.metric(f"{m1} Disb", format_inr(d1))
        c2.metric(f"{m2} Disb", format_inr(d2))
        c3.metric("Payout %", f"{p1:.2f}% vs {p2:.2f}%")

        # Charts
        tab1,tab2,tab3 = st.tabs(["Bank","Campaign","Caller"])

        with tab1:
            st.plotly_chart(bar(f1,"Bank"), use_container_width=True)
            st.plotly_chart(bar(f2,"Bank"), use_container_width=True)

        with tab2:
            st.plotly_chart(donut(f1.groupby("Campaign")["Disbursed AMT"].sum(),m1), use_container_width=True)
            st.plotly_chart(donut(f2.groupby("Campaign")["Disbursed AMT"].sum(),m2), use_container_width=True)

        with tab3:
            st.plotly_chart(bar(f1,"Caller"), use_container_width=True)
            st.plotly_chart(bar(f2,"Caller"), use_container_width=True)

        # Summary
        st.markdown(f"""
        ### 📝 Summary
        - {m1}: Top Bank **{top_bank1}**, Campaign **{top_camp1}**, Caller **{top_call1}**
        - {m2}: Top Bank **{top_bank2}**, Campaign **{top_camp2}**, Caller **{top_call2}**
        """)