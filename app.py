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
# Auto-fit Card Function
# -----------------------------
def colored_metric_auto_fit(label, value, color="#2596be"):
    return f"""
    <div style="
        background-color: #d058e8;
        padding: 10px;
        border-radius: 12px;
        border-left: 6px solid {color};
        box-shadow: 2px 4px 10px rgba(0,0,0,0.08);
        text-align: center;
        margin-bottom: 15px;
        height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        overflow: hidden;
    ">
        <div style="width: 100%; display: flex; justify-content: center; align-items: center; flex-direction: column;">
            <span style="
                font-size: 14px; 
                font-weight: 700; 
                text-transform: uppercase; 
                color: #6c757d;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            ">{label}</span>
            <span style="
                font-weight: 800; 
                color: #212529;
                font-size: 2rem; 
                display: inline-block;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            ">{value}</span>
        </div>
    </div>
    """

# Initialize refresh flag
if "refresh" not in st.session_state:
    st.session_state.refresh = False

# Refresh button in sidebar
if st.sidebar.button("🔄 Refresh Dashboard"):
    st.session_state.refresh = True
    st.experimental_rerun()

# -----------------------------
# LOAD MAIN DATA
# -----------------------------
@st.cache_data(ttl=60)
def load_data():
    url = "https://docs.google.com/spreadsheets/d/1I1ql5NwFafbWXYkVOvv0yvMM9GKnJ5954R4zif2owGI/export?format=csv"
    df = pd.read_csv(url)
    df.replace("null", None, inplace=True)
    return df

# -----------------------------
# LOAD CAMPAIGN DATA
# -----------------------------
@st.cache_data(ttl=60)
def load_campaign_data():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vROJC-HN52HXZboNKd2rNzYbTHzXtAsewd_hbht7MnQMvpNmVfE9H4fjQA0S06sFZGwPDCErXIPEhsy/pub?output=csv"
    df2 = pd.read_csv(url)
    df2.columns = df2.columns.str.strip()
    return df2

df = load_data()
campaign_df = load_campaign_data()

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
            background-color: #07f2c3;
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
# SIDEBAR
# -----------------------------
st.sidebar.title("📊 Dashboard")

dashboard_type = st.sidebar.radio("Select Dashboard", [
    "All Managers",
    "Single Manager",
    "Comparison",
    "Campaign Performance",
    "📊 Campaign Funnel Analysis"
])


verticals = ["All"] + sorted(df["Vertical"].dropna().unique())
months = sorted(df["Disb Month"].dropna().unique())
managers = sorted(df["Manager"].dropna().unique())
latest_month_index = len(months)-1


# -----------------------------
# All Managers Dashboard
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
            Total_Revenue=("Total_Revenue","sum"),
            Transactions=("Manager","count"),
        ).reset_index()

        # Remove blank rows
        agg_df.dropna(how='all', inplace=True)

        # Metrics
        total_disbursed = agg_df["Total_Disbursed"].sum()
        total_revenue = agg_df["Total_Revenue"].sum()
        total_txn = agg_df["Transactions"].sum()
        avg_payout = (total_revenue / total_disbursed * 100) if total_disbursed else 0

        # Display 4 main metric cards
        cols = st.columns([1,1,1,1])
        card_data = [
            ("Total Disbursed", format_inr(total_disbursed), "#636EFA"),
            ("Total Revenue", format_inr(total_revenue), "#00CC96"),
            ("Avg Payout %", f"{avg_payout:.2f}%", "#FFA15A"),
            ("Total Transactions", total_txn, "#EF553B")
        ]
        for col, data in zip(cols, card_data):
            label, value, color = data
            col.markdown(colored_metric_auto_fit(label, value, color), unsafe_allow_html=True)

        # -----------------------------
        # Insight Summary Section
        # -----------------------------
        top_bank = filtered_df.groupby("Bank")["Disbursed AMT"].sum().idxmax() if not filtered_df.empty else "N/A"
        top_campaign = filtered_df.groupby("Campaign")["Disbursed AMT"].sum().idxmax() if not filtered_df.empty else "N/A"
        top_caller = filtered_df.groupby("Caller")["Disbursed AMT"].sum().idxmax() if not filtered_df.empty else "N/A"

        st.markdown(f"""
        <div style="
            background-color: #07f2c3;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-around;
            text-align: center;
        ">
            <div><b>Top Bank:</b> {top_bank}</div>
            <div><b>Top Campaign:</b> {top_campaign}</div>
            <div><b>Top Caller:</b> {top_caller}</div>
        </div>
        """, unsafe_allow_html=True)

        # -----------------------------
        # Table below cards (centered & bold numeric)
        # -----------------------------
        agg_df_display = agg_df.copy()
        agg_df_display["Total_Disbursed"] = agg_df_display["Total_Disbursed"].apply(format_inr)
        agg_df_display["Total_Revenue"] = agg_df_display["Total_Revenue"].apply(format_inr)

        styled_df = agg_df_display.style.set_properties(**{
            'text-align': 'center',
            'vertical-align': 'middle'
        }).format({
            'Total_Disbursed': '   {}    ',
            'Total_Revenue': '   {}    ',
            'Transactions': '    {}    '
        }).set_table_styles([{
            'selector': 'th',
            'props': [('text-align', 'center')]
        }])

        st.subheader("📄 Detailed Table")
        st.dataframe(styled_df, use_container_width=True, height=300)
        st.download_button("Download CSV", agg_df_display.to_csv(index=False), "all_managers.csv", "text/csv")

        # -----------------------------
        # Campaign-wise Disbursed Chart (bold data labels)
        # -----------------------------
        campaign_summary = filtered_df.groupby("Campaign")["Disbursed AMT"].sum()
        if not campaign_summary.empty:
            top_campaign_val = campaign_summary.idxmax()
            campaign_colors = get_colors(campaign_summary.index, top_campaign_val)
            fig_campaign = go.Figure(go.Bar(
                x=campaign_summary.index,
                y=campaign_summary.values/100000,
                text=[f"<b>{v/100000:.2f}L</b>" for v in campaign_summary.values],
                textposition="auto",
                marker_color=campaign_colors,
                name="Campaigns"
            ))
            fig_campaign.update_layout(
                yaxis_title="Amount (L)",
                template="plotly_white",
                height=400,
                title="Campaign-wise Disbursed Amount",
                xaxis_tickangle=-30
            )
            st.plotly_chart(fig_campaign, use_container_width=True)

        # -----------------------------
        # Bank-wise Disbursed Chart (bold data labels)
        # -----------------------------
        bank_summary = filtered_df.groupby("Bank")["Disbursed AMT"].sum()
        if not bank_summary.empty:
            top_bank_val = bank_summary.idxmax()
            bank_colors = get_colors(bank_summary.index, top_bank_val)
            fig_bank = go.Figure(go.Bar(
                x=bank_summary.index,
                y=bank_summary.values/100000,
                text=[f"<b>{v/100000:.2f}L</b>" for v in bank_summary.values],
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

    filtered_df = df[df["Manager"] == selected_manager]
    if selected_month:
        filtered_df = filtered_df[filtered_df["Disb Month"] == selected_month]

    campaigns_available = sorted(filtered_df["Campaign"].dropna().unique())
    with st.sidebar.expander("Campaign Filter", expanded=True):
        selected_campaigns = st.multiselect("Select Campaigns", campaigns_available, default=campaigns_available)
    if selected_campaigns:
        filtered_df = filtered_df[filtered_df["Campaign"].isin(selected_campaigns)]

    st.header(f"📈 Overview - {selected_manager}")
    f = filtered_df
    if f.empty:
        st.warning("No data available")
    else:
        # Calculate metrics
        total_disb, total_rev, avg_payout, txn_count, avg_disb, top_bank, top_campaign, top_caller = calc_metrics(f)
        
        # Metric Cards
        cols = st.columns(4)
        card_data = [
            ("Total Disbursed", format_inr(total_disb), "#636EFA"),
            ("Total Revenue", format_inr(total_rev), "#00CC96"),
            ("Avg Payout %", f"{avg_payout:.2f}%", "#FFA15A"),
            ("Transactions", txn_count, "#EF553B")
        ]
        for col, data in zip(cols, card_data):
            label, value, color = data
            col.markdown(colored_metric_auto_fit(label, value, color), unsafe_allow_html=True)

        # Insight Summary
        st.markdown(f"""
        <div style="
            background-color: #07f2c3;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-around;
            text-align: center;
        ">
            <div><b>Top Bank:</b> {top_bank}</div>
            <div><b>Top Campaign:</b> {top_campaign}</div>
            <div><b>Top Caller:</b> {top_caller}</div>
            <div><b>Avg Disbursed:</b> {format_inr(avg_disb)}</div>
        </div>
        """, unsafe_allow_html=True)

        # Charts
        st.plotly_chart(plot_bar(f, "Bank", top_bank, selected_manager, "bank1"), use_container_width=True)
        st.plotly_chart(plot_bar(f, "Caller", top_caller, selected_manager, "caller1"), use_container_width=True)

        # Campaign-wise Disbursed Chart
        summary = f.groupby("Campaign")["Disbursed AMT"].sum()
        fig = go.Figure(go.Bar(
            x=summary.index,
            y=summary.values/100000,
            text=[f"<b>{v/100000:.2f}L</b>" for v in summary.values],
            textposition="auto",
            marker_color=base_colors,
        ))
        fig.update_layout(
            title="Campaign-wise Disbursed Amount",
            yaxis_title="Amount (L)",
            template="plotly_white",
            xaxis_tickangle=-30
        )
        st.plotly_chart(fig, use_container_width=True)

        # Data Table at Bottom
        st.markdown("### 📄 Data")
        df_display = f.dropna(how='all').copy()
        styled_df = df_display.style.set_properties(**{'text-align': 'center', 'vertical-align': 'middle'}).set_table_styles([{'selector': 'th', 'props': [('text-align', 'center')]}])
        st.dataframe(styled_df, use_container_width=True, height=300)
        st.download_button("Download CSV", df_display.to_csv(index=False), f"{selected_manager}.csv", "text/csv")

# -----------------------------
# Comparison Dashboard with Additional Graphs
# -----------------------------
elif dashboard_type == "Comparison":
    with st.sidebar.expander("Manager & Month Selection", expanded=True):
        selected_manager1 = st.selectbox("First Manager", managers)
        selected_month1 = st.selectbox("Month for First Manager", months, index=latest_month_index)

        selected_manager2 = st.selectbox("Second Manager", managers)
        selected_month2 = st.selectbox("Month for Second Manager", months, index=latest_month_index)

    same_manager = selected_manager1 == selected_manager2

    # Base filters
    f1 = df[(df["Manager"] == selected_manager1) & (df["Disb Month"] == selected_month1)]
    f2 = df[(df["Manager"] == selected_manager2) & (df["Disb Month"] == selected_month2)]

    # Campaign filters
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

    # Header
    st.header("⚖️ Manager / Month Comparison" if not same_manager else f"📅 Month Comparison - {selected_manager1}")
    if f1.empty or f2.empty:
        st.warning("No data available for selected filters")
        st.stop()

    # Metrics
    d1, r1, p1, txn1, avg1, top_bank1, top_camp1, top_caller1 = calc_metrics(f1)
    d2, r2, p2, txn2, avg2, top_bank2, top_camp2, top_caller2 = calc_metrics(f2)
    label1 = f"{selected_manager1} ({selected_month1})"
    label2 = f"{selected_manager2} ({selected_month2})"

    # Winner / Better Month
    if same_manager:
        better_month = selected_month1 if d1 > d2 else selected_month2
        st.success(f"📈 Better Month: {better_month} ({format_inr(max(d1, d2))})")
    else:
        winner = selected_manager1 if d1 > d2 else selected_manager2
        st.success(f"🏆 Winner: {winner} with {format_inr(max(d1, d2))}")

    # Metric Cards
    col1, col2 = st.columns(2)
    card_metrics = [("Total Disbursed", "#636EFA"), ("Total Revenue", "#00CC96"),
                    ("Avg Payout %", "#EF553B"), ("Transactions", "#FFA15A")]
    values1 = [format_inr(d1), format_inr(r1), f"{p1:.2f}%", txn1]
    values2 = [format_inr(d2), format_inr(r2), f"{p2:.2f}%", txn2]

    with col1:
        st.subheader(label1)
        for (lbl, color), val in zip(card_metrics, values1):
            st.markdown(colored_metric_auto_fit(lbl, val, color), unsafe_allow_html=True)
    with col2:
        st.subheader(label2)
        for (lbl, color), val in zip(card_metrics, values2):
            st.markdown(colored_metric_auto_fit(lbl, val, color), unsafe_allow_html=True)

    # Comparison Chart
    comp_df = pd.DataFrame({
        "Metric": ["Disbursed", "Revenue", "Transactions"],
        label1: [d1 / 100000, r1 / 100000, txn1],
        label2: [d2 / 100000, r2 / 100000, txn2]
    })
    fig_comp = go.Figure()
    fig_comp.add_trace(go.Bar(name=label1, x=comp_df["Metric"], y=comp_df[label1],
                              text=[f"<b>{v:.2f}L</b>" if i<2 else f"<b>{int(v)}</b>" for i,v in enumerate(comp_df[label1])],
                              textposition='outside', marker_color="#636EFA"))
    fig_comp.add_trace(go.Bar(name=label2, x=comp_df["Metric"], y=comp_df[label2],
                              text=[f"<b>{v:.2f}L</b>" if i<2 else f"<b>{int(v)}</b>" for i,v in enumerate(comp_df[label2])],
                              textposition='outside', marker_color="#EF553B"))
    fig_comp.update_layout(barmode='group', title="Comparison Overview", template="plotly_white", height=450)
    st.plotly_chart(fig_comp, use_container_width=True)

    # Performance Difference
    growth = ((d1 - d2)/d2*100) if d2 !=0 else 0
    st.markdown("### 📈 Performance Difference")
    st.write(f"{label1} vs {label2}: {growth:.2f}% difference")

    # Insights Summary
    st.markdown("### 📝 Insights")
    st.markdown(f"""
    <div style="background-color: #07f2c3; padding: 15px; border-radius: 10px; margin-bottom: 20px;
                display: flex; justify-content: space-around; text-align: center;">
        <div><b>{label1}:</b> Top Bank {top_bank1}, Top Campaign {top_camp1}, Top Caller {top_caller1}</div>
        <div><b>{label2}:</b> Top Bank {top_bank2}, Top Campaign {top_camp2}, Top Caller {top_caller2}</div>
    </div>
    """, unsafe_allow_html=True)

    # Bank-wise, Caller-wise, Campaign-wise Graphs
    for title, col_name, top_val1, top_val2 in [("Bank", "Bank", top_bank1, top_bank2),
                                                ("Caller", "Caller", top_caller1, top_caller2),
                                                ("Campaign", "Campaign", top_camp1, top_camp2)]:
        st.markdown(f"### 📊 {title}-wise Comparison")
        fig = go.Figure()
        summary1 = f1.groupby(col_name)["Disbursed AMT"].sum()
        summary2 = f2.groupby(col_name)["Disbursed AMT"].sum()
        fig.add_trace(go.Bar(x=summary1.index, y=summary1.values/100000, 
                             text=[f"<b>{v/100000:.2f}L</b>" for v in summary1.values], 
                             textposition='auto', name=label1, marker_color="#636EFA"))
        fig.add_trace(go.Bar(x=summary2.index, y=summary2.values/100000, 
                             text=[f"<b>{v/100000:.2f}L</b>" for v in summary2.values], 
                             textposition='auto', name=label2, marker_color="#EF553B"))
        fig.update_layout(template="plotly_white", barmode='group', xaxis_tickangle=-30, height=400)
        st.plotly_chart(fig, use_container_width=True)

    # Data Tables at Bottom
    st.markdown("### 📄 Data - First Selection")
    df1_display = f1.dropna(how='all').copy()
    st.dataframe(df1_display.style.set_properties(**{'text-align': 'center'}), use_container_width=True, height=300)
    st.download_button("Download CSV", df1_display.to_csv(index=False), "manager1.csv", "text/csv")

    st.markdown("### 📄 Data - Second Selection")
    df2_display = f2.dropna(how='all').copy()
    st.dataframe(df2_display.style.set_properties(**{'text-align': 'center'}), use_container_width=True, height=300)
    st.download_button("Download CSV", df2_display.to_csv(index=False), "manager2.csv", "text/csv")
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
# 📊 CAMPAIGN FUNNEL ANALYSIS (NEW) with Dynamic Filters
# -----------------------------
if dashboard_type == "📊 Campaign Funnel Analysis":

    st.header("📊 Campaign Funnel Analysis")

    df2 = campaign_df.copy()

    # Initialize filters
    months = ["All"] + sorted(df2["Month"].dropna().unique())
    selected_month = st.sidebar.selectbox("Select Month", months)

    # Filter month first
    filtered_month = df2.copy()
    if selected_month != "All":
        filtered_month = filtered_month[filtered_month["Month"] == selected_month]

    # Dynamic Dates
    dates = ["All"] + sorted(filtered_month["Date"].dropna().unique())
    selected_date = st.sidebar.selectbox("Select Date", dates)
    filtered_date = filtered_month.copy()
    if selected_date != "All":
        filtered_date = filtered_date[filtered_date["Date"] == selected_date]

    # Dynamic Campaigns
    campaigns = ["All"] + sorted(filtered_date["Campaign Name"].dropna().unique())
    selected_campaign = st.sidebar.selectbox("Select Campaign", campaigns)
    filtered_campaign = filtered_date.copy()
    if selected_campaign != "All":
        filtered_campaign = filtered_campaign[filtered_campaign["Campaign Name"] == selected_campaign]

    # Dynamic Managers
    managers = ["All"] + sorted(filtered_campaign["Manager"].dropna().unique()) if "Manager" in filtered_campaign.columns else ["All"]
    selected_manager = st.sidebar.selectbox("Select Manager", managers)
    filtered = filtered_campaign.copy()
    if selected_manager != "All" and "Manager" in filtered.columns:
        filtered = filtered[filtered["Manager"] == selected_manager]

    # Aggregate metrics
    total_ivr = int(filtered["IVR Data"].sum())
    press1 = int(filtered["Press 1"].sum())
    leads = int(filtered["Total Request"].sum())
    sent = int(filtered["RCS Sent"].sum())
    delivered = int(filtered["RCS Delivered"].sum())
    read = int(filtered["RCS Read"].sum())
    clicks = int(filtered["RCS Unique Clicks"].sum())
    cost =int(filtered["Cost"].sum())
    total_disbursed = int(filtered["Disbursed"].sum())
    arg_ctr = round((clicks / delivered * 100) if delivered else 0, 2)

    # -----------------------------
    # Colorful KPI cards
    # -----------------------------
    kpi_html = f"""
    <style>
        .kpi-card {{
            color: white;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            font-family: sans-serif;
            flex:1;
        }}
        .kpi-title {{
            font-size: 16px;
            font-weight: bold;
        }}
        .kpi-value {{
            font-size: 28px;
            margin-top: 5px;
        }}
        .kpi-container {{
            display:flex;
            gap:10px;
            flex-wrap:wrap;
        }}
    </style>
    <div class="kpi-container">
        <div class="kpi-card" style="background: linear-gradient(135deg, #6a11cb, #2575fc);">
            <div class="kpi-title">Total IVR</div><div class="kpi-value">{total_ivr:,}</div>
        </div>
        <div class="kpi-card" style="background: linear-gradient(135deg, #ff416c, #ff4b2b);">
            <div class="kpi-title">Press 1</div><div class="kpi-value">{press1:,}</div>
        </div>
        <div class="kpi-card" style="background: linear-gradient(135deg, #f7971e, #ffd200);">
            <div class="kpi-title">Total Request</div><div class="kpi-value">{leads:,}</div>
        </div>
        <div class="kpi-card" style="background: linear-gradient(135deg, #11998e, #38ef7d);">
            <div class="kpi-title">RCS Sent</div><div class="kpi-value">{sent:,}</div>
        </div>
        <div class="kpi-card" style="background: linear-gradient(135deg, #fc4a1a, #f7b733);">
            <div class="kpi-title">RCS Read</div><div class="kpi-value">{read:,}</div>
        </div>
        <div class="kpi-card" style="background: linear-gradient(135deg, #00c6ff, #0072ff);">
            <div class="kpi-title">Clicks</div><div class="kpi-value">{clicks:,}</div>
        </div>
        <div class="kpi-card" style="background: linear-gradient(135deg, #8e2de2, #4a00e0);">
            <div class="kpi-title">Total Cost</div><div class="kpi-value">₹{cost:,}</div>
        </div>
        <div class="kpi-card" style="background: linear-gradient(135deg, #f7971e, #ffd200);">
            <div class="kpi-title">ARG CTR %</div><div class="kpi-value">{arg_ctr:.2f}%</div>
        </div>
        <div class="kpi-card" style="background: linear-gradient(135deg, #36d1dc, #5b86e5);">
            <div class="kpi-title">Total Disbursed</div><div class="kpi-value">₹{total_disbursed:,}</div>
        </div>
    </div>
    """
    st.markdown(kpi_html, unsafe_allow_html=True)

    # -----------------------------
    # Funnel chart
    # -----------------------------
   st.subheader("📉 Funnel")

funnel_colors = ["#6a11cb", "#ff416c", "#f7971e", "#11998e", "#fc4a1a", "#00c6ff"]  # colors per stage

fig = go.Figure(go.Funnel(
    y=["IVR","Press1","Total Request","Delivered","Read","Clicks"],
    x=[total_ivr, press1, leads, delivered, read, clicks],
    textinfo="value+percent previous",
    textposition="inside",
    marker={"color": funnel_colors},
    opacity=0.9
))

# Update layout for better clarity
fig.update_layout(
    margin=dict(l=20, r=20, t=30, b=20),
    font=dict(size=14, family="Arial", color="black"),
)

# Make text bold
fig.update_traces(texttemplate="<b>%{value}</b><br><b>%{percentPrevious:.1%}</b>")

st.plotly_chart(fig, use_container_width=True)

    # -----------------------------
    # Conversion metrics
    # -----------------------------
    st.subheader("📊 Conversion")
    press_rate = round((press1 / total_ivr * 100) if total_ivr else 0, 2)
    delivery_rate = round((delivered / sent * 100) if sent else 0, 2)
    read_rate = round((read / delivered * 100) if delivered else 0, 2)
    cpl = round((cost / leads) if leads else 0, 2)

    r1,r2,r3,r4,r5 = st.columns(5)
    r1.metric("Press %", f"{press_rate:.2f}%")
    r2.metric("Delivery %", f"{delivery_rate:.2f}%")
    r3.metric("Read %", f"{read_rate:.2f}%")
    r4.metric("Cost/Lead", f"₹{cpl:,.2f}")
    r5.metric("Total Disbursed", f"₹{total_disbursed:,.2f}")

    # -----------------------------
    # Click Trend
    # -----------------------------
    if "Date" in filtered.columns:
        st.subheader("📈 Click Trend")
        trend = filtered.groupby("Date")["RCS Unique Clicks"].sum().reset_index()
        fig2 = go.Figure(go.Scatter(
            x=trend["Date"],
            y=trend["RCS Unique Clicks"],
            mode="lines+markers"
        ))
        st.plotly_chart(fig2, use_container_width=True)

    # -----------------------------
    # Insights
    # -----------------------------
    st.subheader("🤖 Insights")
    insight_text = ""
    if arg_ctr < 2:
        st.warning("Low CTR")
        insight_text += "CTR is low. "
    if delivery_rate < 70:
        st.warning("Delivery issue")
        insight_text += "Delivery issues detected. "
    if read_rate < 50:
        st.warning("Low read rate")
        insight_text += "Read rate is low. "
    if cpl > 100:
        st.warning("High cost per lead")
        insight_text += "High cost per lead. "
    if insight_text:
        st.info(insight_text)
# Sidebar + Logout
# -----------------------------
st.sidebar.title("")

if st.sidebar.button("🚪 Logout"):
    st.session_state.login = False
    st.rerun()
