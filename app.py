import streamlit as st
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
from streamlit_autorefresh import st_autorefresh

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(page_title="Pro Manager Dashboard", layout="wide", initial_sidebar_state="expanded")
st_autorefresh(interval=60*1000, key="refresh")

# -----------------------------
# Style Enhancement (CSS)
# -----------------------------
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    [data-testid="stSidebar"] { background-color: #1e293b; color: white; }
    </style>
    """, unsafe_allow_html=True)

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
    last3, rest = s[-3:], s[:-3]
    parts = []
    while len(rest) > 2:
        parts.append(rest[-2:])
        rest = rest[:-2]
    if rest: parts.append(rest)
    parts.reverse()
    return "₹" + (",".join(parts) + "," + last3 if parts else last3)

def calc_metrics(f):
    if f.empty: return [0]*5 + ["N/A"]*3
    total_disb = f["Disbursed AMT"].sum()
    total_rev = f["Total_Revenue"].sum()
    avg_payout = (total_rev/total_disb)*100 if total_disb else 0
    txn_count = len(f)
    avg_disb = total_disb/txn_count if txn_count else 0
    top_bank = f.groupby("Bank")["Disbursed AMT"].sum().idxmax()
    top_campaign = f.groupby("Campaign")["Disbursed AMT"].sum().idxmax()
    top_caller = f.groupby("Caller")["Disbursed AMT"].sum().idxmax()
    return total_disb, total_rev, avg_payout, txn_count, avg_disb, top_bank, top_campaign, top_caller

# -----------------------------
# Sidebar Navigation
# -----------------------------
st.sidebar.title("🚀 Navigation")
dashboard_type = st.sidebar.radio("View", ["All Managers", "Single Manager", "Campaign Performance", "Comparison"])

verticals = ["All"] + sorted(df["Vertical"].dropna().unique().tolist())
months = sorted(df["Disb Month"].dropna().unique().tolist())
managers = sorted(df["Manager"].dropna().unique().tolist())

st.sidebar.divider()

# -----------------------------
# Dashboard Logic
# -----------------------------

if dashboard_type == "All Managers":
    st.title("📊 Enterprise Overview")
    selected_month = st.sidebar.selectbox("Select Month", months, index=len(months)-1)
    
    f = df[df["Disb Month"] == selected_month]
    
    # KPIs at top
    td, tr, ap, tc, _, _, _, _ = calc_metrics(f)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Disbursed", format_inr(td))
    c2.metric("Total Revenue", format_inr(tr))
    c3.metric("Avg Payout", f"{ap:.2f}%")
    c4.metric("Total Deals", tc)

    st.divider()
    
    agg_df = f.groupby(["Vertical","Manager"]).agg(
        Total_Disbursed=("Disbursed AMT","sum"),
        Transactions=("Manager","count")
    ).reset_index().sort_values("Total_Disbursed", ascending=False)
    
    fig = px.bar(agg_df, x="Manager", y="Total_Disbursed", color="Vertical", 
                 title="Manager Performance by Vertical", text_auto='.2s', template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

elif dashboard_type == "Single Manager":
    sel_mgr = st.sidebar.selectbox("Select Manager", managers)
    sel_month = st.sidebar.selectbox("Select Month", months, index=len(months)-1)
    
    f = df[(df["Manager"] == sel_mgr) & (df["Disb Month"] == sel_month)]
    
    st.title(f"📈 {sel_mgr}'s Dashboard")
    
    if f.empty:
        st.warning("Data not available for this month.")
    else:
        td, tr, ap, tc, ad, tb, tcmp, tclr = calc_metrics(f)
        
        # Interactive Tabs
        tab1, tab2, tab3 = st.tabs(["🎯 Key Metrics", "📊 Visual Analytics", "📑 Raw Data"])
        
        with tab1:
            c1, c2, c3 = st.columns(3)
            c1.metric("Disbursed", format_inr(td))
            c2.metric("Revenue", format_inr(tr))
            c3.metric("Avg Ticket Size", format_inr(ad))
            
            st.markdown(f"""
            > **Top Bank:** {tb} | **Top Campaign:** {tcmp} | **Top Caller:** {tclr}
            """)

        with tab2:
            col_l, col_r = st.columns(2)
            with col_l:
                # Bank Chart
                bank_data = f.groupby("Bank")["Disbursed AMT"].sum().reset_index()
                st.plotly_chart(px.pie(bank_data, values='Disbursed AMT', names='Bank', hole=.4, title="Bank Mix"), use_container_width=True)
            with col_r:
                # Caller Chart
                caller_data = f.groupby("Caller")["Disbursed AMT"].sum().reset_index()
                st.plotly_chart(px.bar(caller_data, x='Caller', y='Disbursed AMT', title="Caller Performance"), use_container_width=True)

        with tab3:
            st.dataframe(f, use_container_width=True)

elif dashboard_type == "Campaign Performance":
    st.title("🎯 Campaign Intelligence")
    sel_mgrs = st.sidebar.multiselect("Filter Manager(s)", managers, default=None)
    
    f_camp = df.copy()
    if sel_mgrs:
        f_camp = f_camp[f_camp["Manager"].isin(sel_mgrs)]
    
    all_c = sorted(f_camp["Campaign"].dropna().unique().tolist())
    sel_c = st.sidebar.multiselect("Select Campaigns", all_c, default=all_c[:5])
    
    f_filtered = f_camp[f_camp["Campaign"].isin(sel_c)]
    
    if not f_filtered.empty:
        # Treemap for visual impact
        fig_tree = px.treemap(f_filtered, path=['Campaign', 'Bank'], values='Disbursed AMT',
                              color='Disbursed AMT', color_continuous_scale='RdBu',
                              title="Campaign vs Bank Distribution")
        st.plotly_chart(fig_tree, use_container_width=True)
        
        # Metrics Table
        camp_res = f_filtered.groupby("Campaign").agg(
            Disbursed=("Disbursed AMT","sum"),
            Revenue=("Total_Revenue","sum"),
            Deals=("Manager","count")
        ).reset_index()
        st.table(camp_res.style.background_gradient(cmap='Blues'))
    else:
        st.info("Please select at least one campaign from the sidebar.")

elif dashboard_type == "Comparison":
    st.title("⚖️ Manager vs Manager")
    m1 = st.sidebar.selectbox("Manager A", managers, index=0)
    m2 = st.sidebar.selectbox("Manager B", managers, index=1 if len(managers)>1 else 0)
    
    f1 = df[df["Manager"] == m1]
    f2 = df[df["Manager"] == m2]
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader(m1)
        td1, tr1, _, _, _, _, _, _ = calc_metrics(f1)
        st.metric("Total Disbursed", format_inr(td1))
    with c2:
        st.subheader(m2)
        td2, tr2, _, _, _, _, _, _ = calc_metrics(f2)
        st.metric("Total Disbursed", format_inr(td2), delta=int(td2-td1))

    # Comparative Chart
    comp_df = pd.concat([f1, f2])
    fig_comp = px.box(comp_df, x="Manager", y="Disbursed AMT", color="Manager", title="Ticket Size Distribution Comparison")
    st.plotly_chart(fig_comp, use_container_width=True)

# -----------------------------
# Footer
# -----------------------------
st.sidebar.markdown("---")
st.sidebar.write(f"Refreshed: {pd.Timestamp.now().strftime('%H:%M:%S')}")
