import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Manager Dashboard", layout="wide")
st_autorefresh(interval=60*1000, key="refresh")

@st.cache_data(ttl=60)
def load_data():
    url = "https://docs.google.com/spreadsheets/d/1I1ql5NwFafbWXYkVOvv0yvMM9GKnJ5954R4zif2owGI/export?format=csv"
    df = pd.read_csv(url)
    df.replace("null", None, inplace=True)
    return df

df = load_data()

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
    return ["#FFD700" if val == top_value else base_colors[i % len(base_colors)] for i, val in enumerate(index_list)]

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
        marker_color=colors
    ))
    fig.update_layout(title=f"{manager_name} - {col} Summary", height=400)
    return fig

def colored_metric(label, value, color):
    st.markdown(f"""
    <div style="background:{color};padding:15px;border-radius:10px;text-align:center;color:white">
    <h4>{label}</h4><h2>{value}</h2></div>
    """, unsafe_allow_html=True)

# Sidebar
st.sidebar.title("Filters")
dashboard_type = st.sidebar.radio("Select Dashboard", ["All Managers","Single Manager","Comparison"])

months = sorted(df["Disb Month"].dropna().unique())
managers = sorted(df["Manager"].dropna().unique())

if dashboard_type=="All Managers":
    selected_month = st.sidebar.selectbox("Select Month", months)

elif dashboard_type=="Single Manager":
    selected_manager = st.sidebar.selectbox("Select Manager", managers)
    selected_month = st.sidebar.selectbox("Select Month", months)

else:
    m1 = st.sidebar.selectbox("Manager 1", managers)
    m1_month = st.sidebar.selectbox("Month 1", months)
    m2 = st.sidebar.selectbox("Manager 2", managers)
    m2_month = st.sidebar.selectbox("Month 2", months)

# ---------------- ALL ----------------
if dashboard_type=="All Managers":
    st.header("📊 Enterprise Overview")
    f = df[df["Disb Month"]==selected_month]

    agg = f.groupby("Manager")["Disbursed AMT"].sum()

    fig = go.Figure(go.Bar(x=agg.index, y=agg.values/100000))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 📝 Key Insights")
    st.markdown(f"""
- 📅 Selected Month: **{selected_month}**
- 👥 Total Managers: **{len(agg)}**
- 💰 Total Disbursed: **{format_inr(agg.sum())}**
- 🏆 Top Manager: **{agg.idxmax()}**
""")

# ---------------- SINGLE ----------------
elif dashboard_type=="Single Manager":
    st.header("📈 Manager Insights")
    f = df[(df["Manager"]==selected_manager)&(df["Disb Month"]==selected_month)]

    if f.empty:
        st.warning("No data")
    else:
        d,r,p,txn,avg,bank,camp,caller = calc_metrics(f)

        c1,c2,c3,c4 = st.columns(4)
        with c1: colored_metric("Disbursed",format_inr(d),"#636EFA")
        with c2: colored_metric("Revenue",format_inr(r),"#00CC96")
        with c3: colored_metric("Payout %",f"{p:.2f}%","#EF553B")
        with c4: colored_metric("Txn",txn,"#FFA15A")

        st.plotly_chart(plot_bar(f,"Bank",bank,selected_manager), use_container_width=True)

        st.markdown("### 📝 Key Insights")
        st.markdown(f"""
- 🏦 Top Bank: **{bank}**
- 📣 Top Campaign: **{camp}**
- 📞 Top Caller: **{caller}**
- 🔢 Transactions: **{txn}**
- 💰 Avg Disbursed: **{format_inr(avg)}**
""")

# ---------------- COMPARISON ----------------
else:
    st.header("⚖️ Manager Comparison")

    f1 = df[(df["Manager"]==m1)&(df["Disb Month"]==m1_month)]
    f2 = df[(df["Manager"]==m2)&(df["Disb Month"]==m2_month)]

    d1,r1,p1,txn1,avg1,b1,c1_,cl1 = calc_metrics(f1)
    d2,r2,p2,txn2,avg2,b2,c2_,cl2 = calc_metrics(f2)

    st.markdown("### 📝 Key Insights")

    st.markdown(f"""
#### 🔹 {m1}
- 💰 {format_inr(d1)}
- 🏦 {b1}
- 📞 {cl1}

#### 🔹 {m2}
- 💰 {format_inr(d2)}
- 🏦 {b2}
- 📞 {cl2}
""")
