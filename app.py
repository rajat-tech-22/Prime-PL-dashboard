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
    # Ensure numeric columns are actually numeric
    df["Disbursed AMT"] = pd.to_numeric(df["Disbursed AMT"], errors='coerce').fillna(0)
    df["Total_Revenue"] = pd.to_numeric(df["Total_Revenue"], errors='coerce').fillna(0)
    return df

df = load_data()

# -----------------------------
# Helper Functions
# -----------------------------
def format_inr(number):
    if number is None or number == 0:
        return "₹0"
    s = str(int(number))
    if len(s) <= 3:
        return "₹" + s
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

def plot_bar(f, col, top_value, manager_name, key_val):
    summary = f.groupby(col)["Disbursed AMT"].sum()
    colors = get_colors(summary.index, top_value)
    fig = go.Figure(go.Bar(
        x=summary.index,
        y=summary.values/100000,
        text=[f"{v/100000:.2f}L" for v in summary.values],
        textposition="auto",
        marker_color=colors,
        name=manager_name
    ))
    fig.update_layout(
        yaxis_title="Amount (L)",
        template="plotly_white",
        height=400,
        title=f"{manager_name} - {col} Summary"
    )
    return fig

def colored_metric(label, value, color="#000000"):
    st.markdown(f"""
        <div style="background-color:{color}; padding:20px; border-radius:10px; text-align:center; color:white; margin-bottom:10px;">
            <p style="margin:0; font-size:14px; font-weight:bold;">{label}</p>
            <h2 style="margin:0; font-size:24px;">{value}</h2>
        </div>
        """, unsafe_allow_html=True)

# -----------------------------
# Sidebar Filters Logic
# -----------------------------
st.sidebar.title("Navigation & Filters")
dashboard_type = st.sidebar.radio("Select Dashboard", 
    ["All Managers", "Single Manager", "Comparison", "Campaign Performance"])

verticals = ["All"] + sorted(df["Vertical"].dropna().unique().tolist())
months = sorted(df["Disb Month"].dropna().unique().tolist())
managers = sorted(df["Manager"].dropna().unique().tolist())
latest_month_index = len(months)-1 if months else 0

# --- Dashboard Logic Starts ---

if dashboard_type == "All Managers":
    selected_month = st.sidebar.selectbox("Select Month", months, index=latest_month_index)
    selected_vertical = st.sidebar.selectbox("Business Vertical", verticals)
    
    filtered_df = df.copy()
    if selected_vertical != "All":
        filtered_df = filtered_df[filtered_df["Vertical"]==selected_vertical]
    if months:
        filtered_df = filtered_df[filtered_df["Disb Month"]==selected_month]
    
    st.header("📊 Enterprise Overview")
    agg_df = filtered_df.groupby(["Vertical","Manager"]).agg(
        Total_Disbursed=("Disbursed AMT","sum"),
        Total_Revenue=("Total_Revenue","sum"),
        Transactions=("Manager","count")
    ).reset_index()
    agg_df["Avg_Payout"] = (agg_df["Total_Revenue"]/agg_df["Total_Disbursed"]*100).round(2)
    agg_df.sort_values(["Vertical","Total_Disbursed"], ascending=[True,False], inplace=True)
    
    # Format table for display
    display_agg = agg_df.copy()
    display_agg["Total_Disbursed"] = display_agg["Total_Disbursed"].apply(format_inr)
    display_agg["Total_Revenue"] = display_agg["Total_Revenue"].apply(format_inr)
    st.dataframe(display_agg, use_container_width=True, height=400)
    st.download_button("Download CSV", agg_df.to_csv(index=False), "all_managers.csv", "text/csv")

elif dashboard_type == "Single Manager":
    selected_manager = st.sidebar.selectbox("Select Manager", managers)
    selected_month = st.sidebar.selectbox("Select Month", months, index=latest_month_index)
    
    filtered_df = df[df["Manager"]==selected_manager]
    if months:
        filtered_df = filtered_df[filtered_df["Disb Month"]==selected_month]
    
    st.header(f"📈 Insights - {selected_manager}")
    if filtered_df.empty:
        st.warning("No data available for selected criteria")
    else:
        td, tr, ap, tc, ad, tb, tcmp, tclr = calc_metrics(filtered_df)
        c1, c2, c3, c4 = st.columns(4)
        with c1: colored_metric("Total Disbursed", format_inr(td), "#636EFA")
        with c2: colored_metric("Total Revenue", format_inr(tr), "#00CC96")
        with c3: colored_metric("Avg Payout %", f"{ap:.2f}%", "#EF553B")
        with c4: colored_metric("Transactions", tc, "#FFA15A")
        
        st.plotly_chart(plot_bar(filtered_df, "Bank", tb, selected_manager, "sm_bank"), use_container_width=True)
        st.plotly_chart(plot_bar(filtered_df, "Caller", tclr, selected_manager, "sm_caller"), use_container_width=True)

elif dashboard_type == "Comparison":
    m1 = st.sidebar.selectbox("Manager 1", managers, index=0)
    m2 = st.sidebar.selectbox("Manager 2", managers, index=1 if len(managers)>1 else 0)
    month_cmp = st.sidebar.selectbox("Select Month", months, index=latest_month_index)

    st.header("⚖️ Manager Benchmark")
    f1 = df[(df["Manager"]==m1) & (df["Disb Month"]==month_cmp)]
    f2 = df[(df["Manager"]==m2) & (df["Disb Month"]==month_cmp)]

    col_a, col_b = st.columns(2)
    for col, manager_name, data in zip([col_a, col_b], [m1, m2], [f1, f2]):
        with col:
            st.subheader(manager_name)
            if not data.empty:
                td, tr, ap, tc, _, _, _, _ = calc_metrics(data)
                colored_metric("Disbursed", format_inr(td), "#636EFA")
                colored_metric("Payout %", f"{ap:.2f}%", "#EF553B")
                st.plotly_chart(plot_bar(data, "Bank", "N/A", manager_name, f"cmp_{manager_name}"), use_container_width=False)
            else:
                st.write("No data for this month")

elif dashboard_type == "Campaign Performance":
    st.header("🎯 Campaign Performance Dashboard")
    
    # Filters
    sel_mgr = st.sidebar.selectbox("Filter by Manager", ["All Managers"] + managers)
    
    # Filter campaigns based on manager selection
    temp_df = df.copy()
    if sel_mgr != "All Managers":
        temp_df = temp_df[temp_df["Manager"] == sel_mgr]
    
    all_camps = sorted(temp_df["Campaign"].dropna().unique().tolist())
    sel_camps = st.sidebar.multiselect("Select Campaigns", all_camps, default=all_camps[:3] if all_camps else [])
    
    # Apply Final Filters
    f_camp = temp_df.copy()
    if sel_camps:
        f_camp = f_camp[f_camp["Campaign"].isin(sel_camps)]
    
    if f_camp.empty:
        st.warning("No data found. Please check your filters.")
    else:
        # Aggregated Metrics
        camp_stats = f_camp.groupby("Campaign").agg(
            Total_Disbursed=("Disbursed AMT", "sum"),
            Total_Revenue=("Total_Revenue", "sum"),
            Leads=("Manager", "count")
        ).reset_index()
        camp_stats["Payout_Pct"] = (camp_stats["Total_Revenue"] / camp_stats["Total_Disbursed"] * 100).round(2)
        
        # Display KPIs
        kpi1, kpi2, kpi3 = st.columns(3)
        with kpi1: colored_metric("Campaigns Selected", len(sel_camps), "#AB63FA")
        with kpi2: colored_metric("Total Disbursed", format_inr(f_camp["Disbursed AMT"].sum()), "#636EFA")
        with kpi3: colored_metric("Avg Payout", f"{(f_camp['Total_Revenue'].sum()/f_camp['Disbursed AMT'].sum()*100):.2f}%", "#00CC96")
        
        # Performance Chart
        fig_c = go.Figure()
        fig_c.add_trace(go.Bar(
            x=camp_stats["Campaign"], 
            y=camp_stats["Total_Disbursed"]/100000,
            text=[f"{v/100000:.2f}L" for v in camp_stats["Total_Disbursed"]],
            marker_color="#FFA15A",
            name="Disbursed (L)"
        ))
        fig_c.update_layout(title="Disbursement by Campaign", yaxis_title="Amount in Lakhs", template="plotly_white")
        st.plotly_chart(fig_c, use_container_width=True)
        
        # Table
        st.subheader("Campaign Wise Breakdown")
        tbl_df = camp_stats.copy()
        tbl_df["Total_Disbursed"] = tbl_df["Total_Disbursed"].apply(format_inr)
        tbl_df["Total_Revenue"] = tbl_df["Total_Revenue"].apply(format_inr)
        st.dataframe(tbl_df.sort_values("Leads", ascending=False), use_container_width=True)

# -----------------------------
# Global Footer Info
# -----------------------------
st.sidebar.markdown("---")
st.sidebar.info(f"Last data sync: {pd.Timestamp.now().strftime('%H:%M:%S')}")
