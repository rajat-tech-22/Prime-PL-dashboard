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
# Sidebar Dark Theme CSS
# -----------------------------
st.markdown("""
    <style>
    /* Sidebar background */
    [data-testid="stSidebar"] {
        background-color: #111111;
        color: white;
    }
    /* Sidebar title and headers */
    [data-testid="stSidebar"] .css-1d391kg, 
    [data-testid="stSidebar"] .stExpanderHeader {
        color: white;
        font-weight: bold;
        font-size: 18px;
    }
    /* Sidebar expanders */
    [data-testid="stSidebar"] .st-expander {
        background-color: #1a1a1a;
        border-radius: 8px;
        margin-bottom: 8px;
    }
    /* Input texts inside sidebar */
    [data-testid="stSidebar"] .stTextInput input,
    [data-testid="stSidebar"] .stSelectbox select,
    [data-testid="stSidebar"] .stMultiselect select,
    [data-testid="stSidebar"] .stRadio input + label {
        color: white !important;
        background-color: #111111 !important;
    }
    /* Scrollbar */
    [data-testid="stSidebar"] ::-webkit-scrollbar {
        width: 8px;
    }
    [data-testid="stSidebar"] ::-webkit-scrollbar-thumb {
        background-color: rgba(255,255,255,0.2);
        border-radius: 4px;
    }
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
            <h4 style="margin:0">{label}</h4>
            <h2 style="margin:0">{value}</h2>
        </div>
        """, unsafe_allow_html=True)

# -----------------------------
# Sidebar Filters - Interactive Layout
# -----------------------------
st.sidebar.title("📊 Dashboard Filters")
with st.sidebar.expander("Select Dashboard Type", expanded=True):
    dashboard_type = st.radio("Dashboard", ["All Managers", "Single Manager", "Comparison"])

# Precompute unique options
verticals = ["All"] + sorted(df["Vertical"].dropna().unique())
months = sorted(df["Disb Month"].dropna().unique())
managers = sorted(df["Manager"].dropna().unique())
latest_month_index = len(months)-1

# -----------------------------
# All Managers Sidebar
# -----------------------------
if dashboard_type == "All Managers":
    with st.sidebar.expander("Month & Vertical Filters", expanded=True):
        selected_month = st.selectbox("Select Month", months, index=latest_month_index)
        selected_vertical = st.selectbox("Business Vertical", verticals)

    filtered_df = df.copy()
    if selected_vertical != "All":
        filtered_df = filtered_df[filtered_df["Vertical"]==selected_vertical]
    if selected_month:
        filtered_df = filtered_df[filtered_df["Disb Month"]==selected_month]

    campaigns_available = sorted(filtered_df["Campaign"].dropna().unique())
    with st.sidebar.expander("Campaign Filter", expanded=True):
        selected_campaigns = st.multiselect("Select Campaigns", campaigns_available, default=campaigns_available)
    if selected_campaigns:
        filtered_df = filtered_df[filtered_df["Campaign"].isin(selected_campaigns)]

# -----------------------------
# Single Manager Sidebar
# -----------------------------
elif dashboard_type == "Single Manager":
    with st.sidebar.expander("Manager & Month Filters", expanded=True):
        selected_manager = st.selectbox("Select Manager", managers)
        selected_month = st.selectbox("Select Month", months, index=latest_month_index)

    filtered_df = df[df["Manager"]==selected_manager]
    if selected_month:
        filtered_df = filtered_df[filtered_df["Disb Month"]==selected_month]

    campaigns_available = sorted(filtered_df["Campaign"].dropna().unique())
    with st.sidebar.expander("Campaign Filter", expanded=True):
        selected_campaigns = st.multiselect("Select Campaigns", campaigns_available, default=campaigns_available)
    if selected_campaigns:
        filtered_df = filtered_df[filtered_df["Campaign"].isin(selected_campaigns)]

# -----------------------------
# Comparison Sidebar
# -----------------------------
elif dashboard_type == "Comparison":
    with st.sidebar.expander("Manager & Month Selection", expanded=True):
        selected_manager1 = st.selectbox("First Manager", managers)
        selected_month1 = st.selectbox("Month for First Manager", months, index=latest_month_index)
        selected_manager2 = st.selectbox("Second Manager", managers)
        selected_month2 = st.selectbox("Month for Second Manager", months, index=latest_month_index)

    filtered_df1 = df[(df["Manager"]==selected_manager1) & (df["Disb Month"]==selected_month1)]
    filtered_df2 = df[(df["Manager"]==selected_manager2) & (df["Disb Month"]==selected_month2)]

# -----------------------------
# All Managers Dashboard
# -----------------------------
if dashboard_type == "All Managers":
    st.header("📊 Enterprise Overview")

    if filtered_df.empty:
        st.warning("No data available for selected filters")
    else:
        agg_df = filtered_df.groupby(["Vertical","Manager"]).agg(
            Total_Disbursed=("Disbursed AMT","sum"),
            Total_Revenue=("Total_Revenue","sum"),
            Transactions=("Manager","count")
        ).reset_index()
        agg_df["Avg_Payout"] = (agg_df["Total_Revenue"]/agg_df["Total_Disbursed"]*100).round(2)
        agg_df.sort_values(["Vertical","Total_Disbursed"], ascending=[True,False], inplace=True)
        agg_df["Total_Disbursed"] = agg_df["Total_Disbursed"].apply(format_inr)
        agg_df["Total_Revenue"] = agg_df["Total_Revenue"].apply(format_inr)

        st.dataframe(agg_df, use_container_width=True, height=500)
        st.download_button("Download CSV", agg_df.to_csv(index=False), "all_managers.csv", "text/csv")

        bank_summary = filtered_df.groupby("Bank")["Disbursed AMT"].sum()
        if not bank_summary.empty:
            top_bank = bank_summary.idxmax()
            bank_colors = get_colors(bank_summary.index, top_bank)
            fig_bank = go.Figure(go.Bar(
                x=bank_summary.index,
                y=bank_summary.values/100000,
                text=[f"{v/100000:.2f}L" for v in bank_summary.values],
                textposition="auto",
                marker_color=bank_colors,
                name="Banks"
            ))
            fig_bank.update_layout(
                yaxis_title="Amount (L)",
                template="plotly_white",
                height=400,
                title="Bank-wise Disbursed Amount"
            )
            st.plotly_chart(fig_bank, use_container_width=True)

# -----------------------------
# Single Manager Dashboard
# -----------------------------
if dashboard_type == "Single Manager":
    st.header(f"📈 Insights - {selected_manager}")
    f = filtered_df
    if f.empty:
        st.warning("No data available")
    else:
        total_disb,total_rev,avg_payout,txn_count,avg_disb,top_bank,top_campaign,top_caller = calc_metrics(f)
        col1,col2,col3,col4 = st.columns(4)
        with col1: colored_metric("Total Disbursed", format_inr(total_disb), "#636EFA")
        with col2: colored_metric("Total Revenue", format_inr(total_rev), "#00CC96")
        with col3: colored_metric("Avg Payout %", f"{avg_payout:.2f}%", "#EF553B")
        with col4: colored_metric("Transactions", txn_count, "#FFA15A")

        st.plotly_chart(plot_bar(f,"Bank",top_bank,selected_manager,key_val="bank1"), use_container_width=True)
        st.plotly_chart(plot_bar(f,"Caller",top_caller,selected_manager,key_val="caller1"), use_container_width=True)
        summary = f.groupby("Campaign")["Disbursed AMT"].sum()
        fig = go.Figure(go.Pie(labels=summary.index, values=summary.values/100000, hole=0.4))
        fig.update_layout(title="Campaign Distribution")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### 📝 Insights")
        st.write(f"Top Bank: {top_bank}")
        st.write(f"Top Campaign: {top_campaign}")
        st.write(f"Top Caller: {top_caller}")
        st.write(f"Transactions: {txn_count}")
        st.write(f"Avg Disbursed: {format_inr(avg_disb)}")

        st.markdown("### 📄 Data")
        st.dataframe(f, use_container_width=True, height=400)
        st.download_button("Download CSV", f.to_csv(index=False), "single_manager.csv", "text/csv")

# -----------------------------
# Comparison Dashboard
# -----------------------------
if dashboard_type == "Comparison":
    st.header("⚖️ Manager Benchmark")
    if selected_manager1 == selected_manager2:
        st.warning("Select different managers")
        st.stop()

    f1 = filtered_df1
    f2 = filtered_df2

    d1,r1,p1,txn1,avg1,top_bank1,top_camp1,top_caller1 = calc_metrics(f1)
    d2,r2,p2,txn2,avg2,top_bank2,top_camp2,top_caller2 = calc_metrics(f2)

    col1,col2 = st.columns(2)
    with col1:
        st.subheader(selected_manager1)
        colored_metric("Total Disbursed", format_inr(d1), "#636EFA")
        colored_metric("Total Revenue", format_inr(r1), "#00CC96")
        colored_metric("Avg Payout %", f"{p1:.2f}%", "#EF553B")
        colored_metric("Transactions", txn1, "#FFA15A")
    with col2:
        st.subheader(selected_manager2)
        colored_metric("Total Disbursed", format_inr(d2), "#636EFA")
        colored_metric("Total Revenue", format_inr(r2), "#00CC96")
        colored_metric("Avg Payout %", f"{p2:.2f}%", "#EF553B")
        colored_metric("Transactions", txn2, "#FFA15A")

    st.plotly_chart(plot_bar(f1,"Bank",top_bank1,selected_manager1,key_val="bank_cmp1"), use_container_width=True)
    st.plotly_chart(plot_bar(f2,"Bank",top_bank2,selected_manager2,key_val="bank_cmp2"), use_container_width=True)
    st.plotly_chart(plot_bar(f1,"Caller",top_caller1,selected_manager1,key_val="caller_cmp1"), use_container_width=True)
    st.plotly_chart(plot_bar(f2,"Caller",top_caller2,selected_manager2,key_val="caller_cmp2"), use_container_width=True)

    st.markdown("### 📝 Insights")
    st.write(f"{selected_manager1}: Top Bank {top_bank1}, Top Campaign {top_camp1}, Top Caller {top_caller1}, Transactions {txn1}")
    st.write(f"{selected_manager2}: Top Bank {top_bank2}, Top Campaign {top_camp2}, Top Caller {top_caller2}, Transactions {txn2}")

    st.markdown("### 📄 Data - Manager 1")
    st.dataframe(f1, use_container_width=True, height=300)
    st.download_button("Download CSV", f1.to_csv(index=False), "manager1.csv", "text/csv")

    st.markdown("### 📄 Data - Manager 2")
    st.dataframe(f2, use_container_width=True, height=300)
    st.download_button("Download CSV", f2.to_csv(index=False), "manager2.csv", "text/csv")
