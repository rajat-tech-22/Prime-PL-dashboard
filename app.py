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
# 🔐 SIMPLE LOGIN SYSTEM (FIXED)
# -----------------------------
USERNAME = "PrimePL"
PASSWORD = "@1234"

if "login" not in st.session_state:
    st.session_state.login = False

if not st.session_state.login:
    st.title("🔐 Login")

    u = st.text_input("Username", value="PrimePL")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        if u == USERNAME and p == PASSWORD:
            st.session_state.login = True
            st.success("Login Successful ✅")
            st.rerun()
        else:
            st.error("Invalid Credentials ❌")

    st.stop()

# -----------------------------
# Sidebar & Global UI CSS
# -----------------------------
st.markdown("""
    <style>
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #2596be;
        color: White;
    }
    [data-testid="stSidebar"] .st-expander {
        background-color: #f0f2f6;
        border-radius: 8px;
        margin-bottom: 10px;
    }
    
    /* Main Background */
    .main {
        background-color: #f8f9fa;
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

# --- UPDATED MODERN CARD UI ---
def colored_metric(label, value, color="#2596be"):
    st.markdown(f"""
        <div style="
            background-color: #b561ed;
            padding: 20px;
            border-radius: 12px;
            border-left: 6px solid {color};
            box-shadow: 2px 4px 10px rgba(0,0,0,0.08);
            text-align: left;
            margin-bottom: 15px;
        ">
            <p style="color: #6c757d; font-size: 13px; margin: 0; font-weight: 700; text-transform: uppercase; letter-spacing: 0.8px;">{label}</p>
            <h2 style="color: #212529; margin: 5px 0 0 0; font-size: 24px; font-weight: 800;">{value}</h2>
        </div>
        """, unsafe_allow_html=True)

# -----------------------------
# Sidebar Filters
# -----------------------------
st.sidebar.title("📊 Filters")
with st.sidebar.expander("Select Dashboard Type", expanded=True):
    dashboard_type = st.radio("Dashboard", ["All Managers", "Single Manager", "Comparison", "Campaign Performance"])

verticals = ["All"] + sorted(df["Vertical"].dropna().unique())
months = sorted(df["Disb Month"].dropna().unique())
managers = sorted(df["Manager"].dropna().unique())
latest_month_index = len(months)-1

# -----------------------------
# All Managers Dashboard - 3 Summary Cards
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

    st.header("📊 Overview - Summary Cards")
    if filtered_df.empty:
        st.warning("No data available for selected filters")
    else:
        # Aggregate per manager
        agg_df = filtered_df.groupby(['Vertical',"Manager"]).agg(
            Total_Disbursed=("Disbursed AMT","sum"),
            Transactions=("Manager","count"),
        ).reset_index()
        

        # Card 1: Total Disbursed Amount (All managers)
        total_disbursed = agg_df["Total_Disbursed"].sum()
        # Card 2: Total Transaction Count (All managers)
        total_txn = agg_df["Transactions"].sum()
        # Card 3: Top Manager by Disbursed Amount
        top_manager_row = agg_df.loc[agg_df["Total_Disbursed"].idxmax()]
        top_manager_name = top_manager_row["Manager"]
        top_manager_amt = top_manager_row["Total_Disbursed"]

        # Display 3 cards in one row
        col1, col2, col3 = st.columns(3)
        with col1:
            colored_metric("Total Disbursed Amount", format_inr(total_disbursed), "#636EFA")
        with col2:
            colored_metric("Total Transactions", total_txn, "#EF553B")
        with col3:
            colored_metric(f"Top Manager: {top_manager_name}", format_inr(top_manager_amt), "#00CC96")
     
        # -----------------------------
        # Full table
        # -----------------------------
        agg_df_display = agg_df.copy()
        agg_df_display["Total_Disbursed"] = agg_df_display["Total_Disbursed"].apply(format_inr)
        st.subheader("📄 Detailed Table")
        st.dataframe(agg_df_display, use_container_width=True, height=500)
        st.download_button("Download CSV", agg_df_display.to_csv(index=False), "all_managers.csv", "text/csv")

        # -----------------------------
        # Bank-wise bar chart
        # -----------------------------
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
                title="Bank-wise Disbursed Amount",
                xaxis_tickangle=-30
            )
            st.plotly_chart(fig_bank, use_container_width=True)



# -----------------------------
# Single Manager Dashboard
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
# Comparison Dashboard (FINAL FIXED)
# -----------------------------
elif dashboard_type == "Comparison":
    with st.sidebar.expander("Manager & Month Selection", expanded=True):
        selected_manager1 = st.selectbox("First Manager", managers)
        selected_month1 = st.selectbox("Month for First Manager", months, index=latest_month_index)

        selected_manager2 = st.selectbox("Second Manager", managers)
        selected_month2 = st.selectbox("Month for Second Manager", months, index=latest_month_index)

    # Base filters
    f1 = df[(df["Manager"]==selected_manager1) & (df["Disb Month"]==selected_month1)]
    f2 = df[(df["Manager"]==selected_manager2) & (df["Disb Month"]==selected_month2)]

    # -----------------------------
    # 🔥 Separate Campaign Filters
    # -----------------------------
    with st.sidebar.expander(f"{selected_manager1} Campaign Filter", expanded=True):
        camp1_list = sorted(f1["Campaign"].dropna().unique())
        selected_camp1 = st.multiselect("Campaigns - Manager 1", camp1_list, default=camp1_list)

    with st.sidebar.expander(f"{selected_manager2} Campaign Filter", expanded=True):
        camp2_list = sorted(f2["Campaign"].dropna().unique())
        selected_camp2 = st.multiselect("Campaigns - Manager 2", camp2_list, default=camp2_list)

    if selected_camp1:
        f1 = f1[f1["Campaign"].isin(selected_camp1)]
    if selected_camp2:
        f2 = f2[f2["Campaign"].isin(selected_camp2)]

    st.header("⚖️ Manager Benchmark")

    # Validation
    if selected_manager1 == selected_manager2:
        st.warning("Select different managers")
        st.stop()

    if f1.empty or f2.empty:
        st.warning("No data available for selected filters")
        st.stop()

    # Metrics
    d1,r1,p1,txn1,avg1,top_bank1,top_camp1,top_caller1 = calc_metrics(f1)
    d2,r2,p2,txn2,avg2,top_bank2,top_camp2,top_caller2 = calc_metrics(f2)

    # -----------------------------
    # 🏆 Winner
    # -----------------------------
    if d1 > d2:
        winner = selected_manager1
        win_amt = d1
    else:
        winner = selected_manager2
        win_amt = d2

    st.success(f"🏆 Winner: {winner} with {format_inr(win_amt)}")

    # -----------------------------
    # Metric Cards
    # -----------------------------
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

    # -----------------------------
    # 📊 Comparison Chart (WITH DATA LABELS)
    # -----------------------------
    comp_df = pd.DataFrame({
        "Metric": ["Disbursed", "Revenue", "Transactions"],
        selected_manager1: [d1/100000, r1/100000, txn1],
        selected_manager2: [d2/100000, r2/100000, txn2]
    })

    fig_comp = go.Figure()

    fig_comp.add_trace(go.Bar(
        name=selected_manager1,
        x=comp_df["Metric"],
        y=comp_df[selected_manager1],
        text=[
            f"{v:.2f}L" if i < 2 else f"{int(v)}"
            for i, v in enumerate(comp_df[selected_manager1])
        ],
        textposition='outside',
        marker_color="#636EFA"
    ))

    fig_comp.add_trace(go.Bar(
        name=selected_manager2,
        x=comp_df["Metric"],
        y=comp_df[selected_manager2],
        text=[
            f"{v:.2f}L" if i < 2 else f"{int(v)}"
            for i, v in enumerate(comp_df[selected_manager2])
        ],
        textposition='outside',
        marker_color="#EF553B"
    ))

    fig_comp.update_layout(
        barmode='group',
        title="Manager Comparison Overview",
        template="plotly_white",
        height=450,
        uniformtext_minsize=10,
        uniformtext_mode='hide'
    )

    fig_comp.update_traces(
        textfont_size=12,
        cliponaxis=False
    )

    st.plotly_chart(fig_comp, use_container_width=True)

    # -----------------------------
    # 📊 Bank + Caller Charts
    # -----------------------------
    st.plotly_chart(plot_bar(f1,"Bank",top_bank1,selected_manager1,"bank_cmp1"), use_container_width=True)
    st.plotly_chart(plot_bar(f2,"Bank",top_bank2,selected_manager2,"bank_cmp2"), use_container_width=True)

    st.plotly_chart(plot_bar(f1,"Caller",top_caller1,selected_manager1,"caller_cmp1"), use_container_width=True)
    st.plotly_chart(plot_bar(f2,"Caller",top_caller2,selected_manager2,"caller_cmp2"), use_container_width=True)

    # -----------------------------
    # 📈 Growth Difference
    # -----------------------------
    growth = ((d1 - d2) / d2 * 100) if d2 != 0 else 0

    st.markdown("### 📈 Performance Difference")
    st.write(f"{selected_manager1} vs {selected_manager2}: {growth:.2f}% difference in disbursed amount")

    # -----------------------------
    # Insights
    # -----------------------------
    st.markdown("### 📝 Insights")
    st.write(f"{selected_manager1}: Top Bank {top_bank1}, Top Campaign {top_camp1}, Top Caller {top_caller1}, Transactions {txn1}")
    st.write(f"{selected_manager2}: Top Bank {top_bank2}, Top Campaign {top_camp2}, Top Caller {top_caller2}, Transactions {txn2}")

    # -----------------------------
    # Data Tables
    # -----------------------------
    st.markdown("### 📄 Data - Manager 1")
    st.dataframe(f1, use_container_width=True, height=300)
    st.download_button("Download CSV", f1.to_csv(index=False), "manager1.csv", "text/csv")

    st.markdown("### 📄 Data - Manager 2")
    st.dataframe(f2, use_container_width=True, height=300)
    st.download_button("Download CSV", f2.to_csv(index=False), "manager2.csv", "text/csv")

# -----------------------------
# Campaign Performance Dashboard (ULTIMATE)
# -----------------------------
elif dashboard_type == "Campaign Performance":
    with st.sidebar.expander("Month & Campaign Filter", expanded=True):
        camp_months = sorted(df["Disb Month"].dropna().unique())

        selected_camp_month = st.selectbox(
            "Select Month",
            camp_months,
            index=len(camp_months)-1
        )

        temp_df = df[df["Disb Month"] == selected_camp_month]
        camp_list = sorted(temp_df["Campaign"].dropna().unique())

        col1, col2 = st.columns(2)
        with col1:
            select_all = st.button("Select All")
        with col2:
            clear_all = st.button("Clear All")

        if "camp_selection" not in st.session_state:
            st.session_state.camp_selection = camp_list

        if select_all:
            st.session_state.camp_selection = camp_list
        if clear_all:
            st.session_state.camp_selection = []

        selected_camps = st.multiselect(
            "Select Campaigns",
            camp_list,
            default=st.session_state.camp_selection
        )

    # Apply filters
    camp_df = df[df["Disb Month"] == selected_camp_month]
    if selected_camps:
        camp_df = camp_df[camp_df["Campaign"].isin(selected_camps)]

    st.header("📊 Campaign Performance Dashboard")

    if camp_df.empty:
        st.warning("No data available for selected filters")
        st.stop()

    # -----------------------------
    # 🏆 Top Campaign
    # -----------------------------
    camp_perf = camp_df.groupby("Campaign")["Disbursed AMT"].sum()
    top_campaign = camp_perf.idxmax()
    top_value = camp_perf.max()

    st.success(f"🏆 Top Campaign: {top_campaign} ({format_inr(top_value)})")

    # -----------------------------
    # 📄 Manager Table
    # -----------------------------
    camp_summary = camp_df.groupby("Manager").agg(
        Total_Disbursed=("Disbursed AMT","sum"),
        Total_Revenue=("Total_Revenue","sum"),
        Transactions=("Manager","count")
    ).reset_index()

    camp_summary["Avg_Payout"] = (
        camp_summary["Total_Revenue"] / camp_summary["Total_Disbursed"] * 100
    ).round(2)

    camp_summary["Total_Disbursed"] = camp_summary["Total_Disbursed"].apply(format_inr)
    camp_summary["Total_Revenue"] = camp_summary["Total_Revenue"].apply(format_inr)

    st.subheader("📄 Manager Performance Table")
    st.dataframe(camp_summary, use_container_width=True, height=350)

    st.download_button(
        "Download CSV",
        camp_summary.to_csv(index=False),
        "campaign_performance.csv",
        "text/csv"
    )

    # -----------------------------
    # 📊 Campaign-wise Chart
    # -----------------------------
    colors = get_colors(camp_perf.index, top_campaign)

    fig_camp = go.Figure(go.Bar(
        x=camp_perf.index,
        y=camp_perf.values/100000,
        text=[f"{v/100000:.2f}L" for v in camp_perf.values],
        textposition="outside",
        marker_color=colors
    ))

    fig_camp.update_layout(
        title="Campaign-wise Performance",
        template="plotly_white",
        height=450
    )

    fig_camp.update_traces(cliponaxis=False)
    st.plotly_chart(fig_camp, use_container_width=True)

    # -----------------------------
    # 🏆 Best Manager per Campaign
    # -----------------------------
    st.markdown("### 🏆 Best Manager per Campaign")

    best_mgr = camp_df.groupby(["Campaign","Manager"])["Disbursed AMT"].sum().reset_index()
    best_mgr = best_mgr.loc[
        best_mgr.groupby("Campaign")["Disbursed AMT"].idxmax()
    ]

    best_mgr["Disbursed AMT"] = best_mgr["Disbursed AMT"].apply(format_inr)

    st.dataframe(best_mgr, use_container_width=True, height=300)

    # -----------------------------
    # 🚨 Underperforming Campaigns
    # -----------------------------
    st.markdown("### 🚨 Underperforming Campaigns")

    avg_perf = camp_perf.mean()
    underperforming = camp_perf[camp_perf < avg_perf]

    if underperforming.empty:
        st.success("✅ No underperforming campaigns")
    else:
        under_df = underperforming.reset_index()
        under_df.columns = ["Campaign","Disbursed AMT"]
        under_df["Disbursed AMT"] = under_df["Disbursed AMT"].apply(format_inr)

        st.warning(f"{len(under_df)} campaigns below average")
        st.dataframe(under_df, use_container_width=True)

    # -----------------------------
    # 📊 Bank-wise Chart
    # -----------------------------
    bank_summary = camp_df.groupby("Bank")["Disbursed AMT"].sum()

    if not bank_summary.empty:
        top_bank = bank_summary.idxmax()
        bank_colors = get_colors(bank_summary.index, top_bank)

        fig_bank = go.Figure(go.Bar(
            x=bank_summary.index,
            y=bank_summary.values/100000,
            text=[f"{v/100000:.2f}L" for v in bank_summary.values],
            textposition="outside",
            marker_color=bank_colors
        ))

        fig_bank.update_layout(
            yaxis_title="Amount (L)",
            template="plotly_white",
            height=400,
            title="Bank-wise Disbursed Amount"
        )

        fig_bank.update_traces(cliponaxis=False)
        st.plotly_chart(fig_bank, use_container_width=True)

    # -----------------------------
    # 📈 Growth Analysis
    # -----------------------------
    current_month_index = camp_months.index(selected_camp_month)

    if current_month_index > 0:
        prev_month = camp_months[current_month_index - 1]

        prev_df = df[df["Disb Month"] == prev_month]

        curr_total = camp_df["Disbursed AMT"].sum()
        prev_total = prev_df["Disbursed AMT"].sum()

        growth = ((curr_total - prev_total) / prev_total * 100) if prev_total != 0 else 0

        st.markdown("### 📈 Growth Analysis")
        st.write(f"{selected_camp_month} vs {prev_month}: {growth:.2f}% change")

    # -----------------------------
    # 🤖 AI Insights
    # -----------------------------
    st.markdown("### 🤖 AI Insights")

    total_disb = camp_df["Disbursed AMT"].sum()
    total_rev = camp_df["Total_Revenue"].sum()
    avg_payout = (total_rev / total_disb * 100) if total_disb else 0

    low_campaign = camp_perf.idxmin()
    low_value = camp_perf.min()

    top_manager = camp_df.groupby("Manager")["Disbursed AMT"].sum().idxmax()

    insight_text = f"""
📊 Total Disbursed: {format_inr(total_disb)}  
💰 Total Revenue: {format_inr(total_rev)}  
📈 Avg Payout: {avg_payout:.2f}%  

🏆 Top Campaign: {top_campaign} ({format_inr(top_value)})  
📉 Lowest Campaign: {low_campaign} ({format_inr(low_value)})  

👑 Best Manager Overall: {top_manager}  
⚠️ {len(underperforming)} campaigns need attention  
"""

    st.info(insight_text)
# -----------------------------
# Sidebar + Logout
# -----------------------------
st.sidebar.title("")

if st.sidebar.button("🚪 Logout"):
    st.session_state.login = False
    st.rerun()
