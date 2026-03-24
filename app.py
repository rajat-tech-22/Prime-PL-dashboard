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
    df["Disbursed AMT"] = pd.to_numeric(df["Disbursed AMT"], errors='coerce').fillna(0)
    df["Total_Revenue"] = pd.to_numeric(df["Total_Revenue"], errors='coerce').fillna(0)
    return df

df = load_data()

# -----------------------------
# Helper Functions
# -----------------------------
def format_inr(number):
    if number is None or number == 0: return "₹0"
    s = str(int(number))
    if len(s) <= 3: return "₹" + s
    last3, rest = s[-3:], s[:-3]
    parts = []
    while len(rest) > 2:
        parts.append(rest[-2:]); rest = rest[:-2]
    if rest: parts.append(rest)
    parts.reverse()
    return "₹" + ",".join(parts) + "," + last3

base_colors = ["#636EFA","#EF553B","#00CC96","#AB63FA","#FFA15A","#19D3F3","#FF6692","#B6E880"]

def get_colors(index_list, top_value):
    return ["#FFD700" if val == top_value else base_colors[i % len(base_colors)] for i, val in enumerate(index_list)]

def calc_metrics(f):
    if f.empty: return 0,0,0,0,0,"N/A","N/A","N/A"
    td, tr = f["Disbursed AMT"].sum(), f["Total_Revenue"].sum()
    ap = (tr/td)*100 if td else 0
    tc = len(f)
    ad = td/tc if tc else 0
    tb = f.groupby("Bank")["Disbursed AMT"].sum().idxmax()
    tcmp = f.groupby("Campaign")["Disbursed AMT"].sum().idxmax()
    tclr = f.groupby("Caller")["Disbursed AMT"].sum().idxmax()
    return td, tr, ap, tc, ad, tb, tcmp, tclr

def plot_bar(f, col, top_value, manager_name):
    summary = f.groupby(col)["Disbursed AMT"].sum()
    colors = get_colors(summary.index, top_value)
    fig = go.Figure(go.Bar(x=summary.index, y=summary.values/100000, 
                           text=[f"{v/100000:.2f}L" for v in summary.values],
                           textposition="auto", marker_color=colors))
    fig.update_layout(yaxis_title="Amount (L)", template="plotly_white", height=400, title=f"{manager_name} - {col} Summary")
    return fig

def colored_metric(label, value, color="#000000"):
    st.markdown(f"""<div style="background-color:{color}; padding:20px; border-radius:10px; text-align:center; color:white; margin-bottom:10px;">
        <h4 style="margin:0">{label}</h4><h2 style="margin:0">{value}</h2></div>""", unsafe_allow_html=True)

# -----------------------------
# Sidebar Filters
# -----------------------------
st.sidebar.title("Filters")
dashboard_type = st.sidebar.radio("Select Dashboard", ["All Managers", "Single Manager", "Campaign Performance", "Comparison"])
months = sorted(df["Disb Month"].dropna().unique())
managers = sorted(df["Manager"].dropna().unique())
latest_month_index = len(months)-1 if months else 0

# -----------------------------
# 1. All Managers Dashboard
# -----------------------------
if dashboard_type == "All Managers":
    st.header("📊 Enterprise Overview")
    selected_month = st.sidebar.selectbox("Select Month", months, index=latest_month_index)
    f = df[df["Disb Month"]==selected_month]
    
    td, tr, ap, tc, _, tb, tcmp, _ = calc_metrics(f)
    c1, c2, c3, c4 = st.columns(4)
    with c1: colored_metric("Total Disbursed", format_inr(td), "#636EFA")
    with c2: colored_metric("Total Revenue", format_inr(tr), "#00CC96")
    with c3: colored_metric("Average Payout", f"{ap:.2f}%", "#EF553B")
    with c4: colored_metric("Total Leads", tc, "#FFA15A")

    agg_df = f.groupby(["Vertical","Manager"]).agg(Total_Disbursed=("Disbursed AMT","sum"), Transactions=("Manager","count")).reset_index()
    agg_df.sort_values("Total_Disbursed", ascending=False, inplace=True)
    st.dataframe(agg_df, use_container_width=True)

    st.markdown("### 📝 Key Insights")
    st.write(f"* **Top Performer:** Is month ka sabse zyada disbursement `{agg_df.iloc[0]['Manager'] if not agg_df.empty else 'N/A'}` ne kiya hai.")
    st.write(f"* **Top Bank:** `{tb}` sabse zyada business de raha hai.")
    st.write(f"* **Dominant Campaign:** Sabse successful campaign `{tcmp}` raha hai.")

# -----------------------------
# 2. Single Manager Dashboard
# -----------------------------
elif dashboard_type == "Single Manager":
    sel_mgr = st.sidebar.selectbox("Select Manager", managers)
    sel_month = st.sidebar.selectbox("Select Month", months, index=latest_month_index)
    f = df[(df["Manager"]==sel_mgr) & (df["Disb Month"]==sel_month)]
    
    st.header(f"📈 Insights - {sel_mgr}")
    if f.empty: st.warning("No data available")
    else:
        td, tr, ap, tc, ad, tb, tcmp, tclr = calc_metrics(f)
        c1, c2, c3, c4 = st.columns(4)
        with c1: colored_metric("Disbursed", format_inr(td), "#636EFA")
        with c2: colored_metric("Revenue", format_inr(tr), "#00CC96")
        with c3: colored_metric("Payout %", f"{ap:.2f}%", "#EF553B")
        with c4: colored_metric("Avg Deal", format_inr(ad), "#FFA15A")

        st.plotly_chart(plot_bar(f, "Bank", tb, sel_mgr), use_container_width=True)

        st.markdown("### 📝 Manager Insights")
        st.write(f"* **Top Bank:** `{sel_mgr}` ka sabse zyada business `{tb}` se aa raha hai.")
        st.write(f"* **Top Caller:** Inki team mein `{tclr}` sabse zyada deals close kar raha hai.")
        st.write(f"* **Volume:** Total `{tc}` deals close hui hain jiski average value `{format_inr(ad)}` hai.")

# -----------------------------
# 3. Campaign Performance
# -----------------------------
elif dashboard_type == "Campaign Performance":
    st.header("🎯 Campaign Performance")
    sel_mgr = st.sidebar.selectbox("Filter Manager", ["All"] + managers)
    temp_df = df.copy() if sel_mgr == "All" else df[df["Manager"] == sel_mgr]
    all_camps = sorted(temp_df["Campaign"].dropna().unique())
    sel_camps = st.sidebar.multiselect("Select Campaigns", all_camps, default=all_camps[:3])
    
    f_camp = temp_df[temp_df["Campaign"].isin(sel_camps)]
    if f_camp.empty: st.info("Please select campaigns")
    else:
        td, tr, ap, tc, _, tb, tcmp, _ = calc_metrics(f_camp)
        c1, c2, c3 = st.columns(3)
        with c1: colored_metric("Total Disbursed", format_inr(td), "#636EFA")
        with c2: colored_metric("Revenue", format_inr(tr), "#00CC96")
        with c3: colored_metric("Leads count", tc, "#AB63FA")
        
        st.plotly_chart(plot_bar(f_camp, "Campaign", tcmp, "Comparison"), use_container_width=True)

        st.markdown("### 📝 Campaign Insights")
        st.write(f"* **Winner:** Selected campaigns mein `{tcmp}` ne sabse best perform kiya hai.")
        st.write(f"* **Bank Support:** In campaigns ko `{tb}` bank se sabse zyada support mil raha hai.")
        st.write(f"* **Profitability:** Overall payout `{ap:.2f}%` generate ho raha hai.")

# -----------------------------
# 4. Comparison Dashboard
# -----------------------------
elif dashboard_type == "Comparison":
    st.header("⚖️ Manager Benchmark")
    m1 = st.sidebar.selectbox("Manager 1", managers, index=0)
    m2 = st.sidebar.selectbox("Manager 2", managers, index=1 if len(managers)>1 else 0)
    f1, f2 = df[df["Manager"]==m1], df[df["Manager"]==m2]
    
    col1, col2 = st.columns(2)
    td1, _, ap1, _, _, _, _, _ = calc_metrics(f1)
    td2, _, ap2, _, _, _, _, _ = calc_metrics(f2)

    with col1:
        st.subheader(m1); colored_metric("Disbursed", format_inr(td1), "#636EFA")
        st.plotly_chart(plot_bar(f1, "Bank", "N/A", m1), use_container_width=True)
    with col2:
        st.subheader(m2); colored_metric("Disbursed", format_inr(td2), "#EF553B")
        st.plotly_chart(plot_bar(f2, "Bank", "N/A", m2), use_container_width=True)

    st.markdown("### 📝 Benchmark Insights")
    winner = m1 if td1 > td2 else m2
    diff = abs(td1 - td2)
    st.write(f"* **Volume Leader:** `{winner}` aage hai (Gap: {format_inr(diff)}).")
    st.write(f"* **Efficiency:** `{m1 if ap1 > ap2 else m2}` ka payout percentage zyada behtar hai.")
