import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment variables
load_dotenv()

# Database connection setup using SQLAlchemy
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://togiabao:mysecretpassword@34.228.244.87:5432/timo_digital_bank")


@st.cache_resource
def get_engine():
    return create_engine(DATABASE_URL)


engine = get_engine()


# Fetch data from database using SQLAlchemy
@st.cache_data(ttl=600)
def fetch_data(query, params=None):
    try:
        with engine.connect() as connection:
            df = pd.read_sql(text(query), connection, params=params)
            return df
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()


# Set page configuration
st.set_page_config(
    page_title="Timo Digital Bank Case Study",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🏦"
)

# Custom CSS for modern styling and improved UI
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');

    html, body, [class*="st-"] {
        font-family: 'Roboto', sans-serif;
        color: #2c3e50;
    }

    .main {
        background-color: #f0f2f6;
        padding: 2em 3em;
    }

    .stApp {
        background-color: #f0f2f6;
    }

    .header {
        color: #1a2a3a;
        font-size: 3.5em;
        font-weight: 800;
        margin-bottom: 0.8em;
        text-align: center;
        text-shadow: 2px 2px 6px rgba(0,0,0,0.15);
        padding-top: 1em;
    }

    .subheader {
        color: #34495e;
        font-size: 2.2em;
        font-weight: 700;
        margin-top: 2.5em;
        margin-bottom: 1.2em;
        border-bottom: 4px solid #e0e0e0;
        padding-bottom: 0.6em;
        text-align: left;
    }

    .metric-card {
        background-color: #ffffff;
        padding: 1.6em;
        border-radius: 18px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.12);
        margin-bottom: 2em;
        text-align: center;
        transition: all 0.3s ease-in-out;
        border: 1px solid #e0e0e0;
    }
    .metric-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 12px 30px rgba(0,0,0,0.18);
    }
    .metric-card h3 {
        color: #555;
        font-size: 1.3em;
        margin-bottom: 0.8em;
        font-weight: 600;
    }
    .metric-card p {
        font-size: 2.1em;
        font-weight: bold;
        color: #007bff;
        margin: 0;
    }

    .sidebar .sidebar-content {
        background-color: #ffffff;
        padding: 2.5em;
        border-radius: 15px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.1);
        border: 1px solid #e0e0e0;
    }

    .stButton>button {
        background-color: #007bff;
        color: white;
        border-radius: 12px;
        padding: 0.9em 1.8em;
        font-size: 1.2em;
        font-weight: 600;
        transition: background-color 0.3s ease, transform 0.2s ease, box-shadow 0.3s ease;
        border: none;
        box-shadow: 0 4px 15px rgba(0,123,255,0.3);
    }
    .stButton>button:hover {
        background-color: #0056b3;
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(0,123,255,0.4);
    }

    .stDateInput, .stMultiSelect {
        margin-bottom: 1.5em;
    }

    .stWarning {
        background-color: #fff3cd;
        color: #856404;
        border-radius: 12px;
        padding: 1.5em;
        border: 1px solid #ffeeba;
        font-size: 1.1em;
    }

    .stInfo {
        background-color: #d1ecf1;
        color: #0c5460;
        border-radius: 12px;
        padding: 1.5em;
        border: 1px solid #bee5eb;
        font-size: 1.1em;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 15px;
        margin-bottom: 1.5em;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 15px 15px 0 0;
        background-color: #e9ecef;
        padding: 1em 1.5em;
        transition: all 0.3s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #dee2e6;
    }
    .stTabs [aria-selected="true"] {
        background-color: #007bff;
        color: white;
        font-weight: 700;
        border-bottom: 3px solid #0056b3;
    }
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1.4em;
        font-weight: 600;
        margin: 0;
    }

    .stDataFrame {
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    }

    .stPlotlyChart {
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        background-color: #ffffff;
        padding: 1em;
    }

</style>
""", unsafe_allow_html=True)

# Sidebar for filters
st.sidebar.header("📊 Dashboard Filters")

date_range = st.sidebar.date_input(
    "📅 Select Date Range",
    value=[datetime.now() - timedelta(days=30), datetime.now()],
    min_value=datetime(2023, 1, 1),
    max_value=datetime.now()
)

customer_segment_options = ["individual", "organization"]
customer_segment = st.sidebar.multiselect(
    "👥 Customer Segment",
    options=customer_segment_options,
    default=customer_segment_options
)

transaction_type_options = [
    "transfer_same_bank_same_owner", "transfer_same_bank_diff_owner",
    "transfer_interbank_domestic", "transfer_interbank_international",
    "payment_goods_services", "ewallet_topup", "ewallet_withdrawal",
    "inquiry", "ewallet_transfer"
]
transaction_types = st.sidebar.multiselect(
    "💳 Transaction Type",
    options=transaction_type_options,
    default=transaction_type_options
)

# Main content
st.markdown("<div class=\"header\">Timo Digital Bank Case Study</div>", unsafe_allow_html=True)

# Overview Section
st.markdown("""
<div class="subheader">Overview</div>
<div class="metric-card" style="text-align: left;">
    <p style="font-size: 1.2em; font-weight: normal; color: #555;">
        This dashboard provides comprehensive insights into Timo Digital Bank's operations, focusing on key areas such as transaction patterns, customer behavior, risk management, and device security. 
        Our primary objectives are to:
    </p>
    <ul style="font-size: 1.1em; color: #666; line-height: 1.6;">
        <li>Monitor and analyze transaction volumes and types to understand evolving customer behavior and market trends.</li>
        <li>Identify and flag suspicious transactions and authentication failures proactively to enhance overall security posture.</li>
        <li>Track and manage unverified devices to mitigate potential fraud risks and prevent unauthorized account access.</li>
        <li>Provide actionable insights derived from data analysis to support informed decision-making for fraud prevention, operational efficiency, and strategic growth.</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# Logic for handling date range and transaction types
start_date = None
end_date = None
if date_range and len(date_range) == 2:
    start_date = date_range[0]
    end_date = date_range[1]

if not transaction_types:
    st.warning("Please select at least one transaction type to view metrics and visualizations.")
    st.stop()  # Stop execution if no transaction types are selected

# Prepare parameters for parameterized queries
params = {
    "start_date": start_date,
    "end_date": end_date,
    "transaction_types": tuple(transaction_types) if transaction_types else (""),  # Ensure it's a tuple for IN clause
    "customer_segments": tuple(customer_segment) if customer_segment else ("")
}

# Key Metrics Section
st.markdown("<div class=\"subheader\">Key Metrics</div>", unsafe_allow_html=True)

metric_tabs = st.tabs(["Transaction Metrics", "Customer & Device Metrics", "Security Metrics"])

with metric_tabs[0]:  # Transaction Metrics
    # Total Customers (moved here for consistency, though not strictly a transaction metric)
    total_customers_df = fetch_data("SELECT COUNT(*) FROM customers WHERE status = 'active'")
    total_customers = total_customers_df.iloc[0, 0] if not total_customers_df.empty else 0

    # Total Transactions and Average Transaction Value
    query_transactions = """
        SELECT COUNT(*) AS total_transactions, COALESCE(AVG(amount), 0) AS avg_transaction_value
        FROM payment_transactions
        WHERE transaction_date::DATE BETWEEN :start_date AND :end_date
        AND transaction_type IN :transaction_types
    """
    transaction_metrics_df = fetch_data(query_transactions, params)
    total_transactions = transaction_metrics_df.iloc[0, 0] if not transaction_metrics_df.empty else 0
    avg_transaction_value = transaction_metrics_df.iloc[0, 1] if not transaction_metrics_df.empty else 0

    # Risky Transactions and Fraud Detection Rate
    query_risky = """
        SELECT COUNT(*) 
        FROM payment_transactions 
        WHERE is_suspicious = TRUE 
        AND transaction_date::DATE BETWEEN :start_date AND :end_date
        AND transaction_type IN :transaction_types
    """
    risky_transactions_df = fetch_data(query_risky, params)
    risky_transactions = risky_transactions_df.iloc[0, 0] if not risky_transactions_df.empty else 0

    fraud_detection_rate = (risky_transactions / total_transactions * 100) if total_transactions > 0 else 0

    # New Metric 1: Transaction Success Rate
    query_success_rate = """
        SELECT 
            CAST(COUNT(CASE WHEN status = 'completed' THEN 1 END) AS DECIMAL) / COUNT(*) * 100
        FROM payment_transactions
        WHERE transaction_date::DATE BETWEEN :start_date AND :end_date
        AND transaction_type IN :transaction_types
    """
    success_rate_df = fetch_data(query_success_rate, params)
    transaction_success_rate = success_rate_df.iloc[0, 0] if not success_rate_df.empty else 0

    # New Metric 2: Average Daily Transactions
    query_avg_daily_tx = """
        SELECT COALESCE(AVG(daily_count), 0)
        FROM (
            SELECT COUNT(*) AS daily_count
            FROM payment_transactions
            WHERE transaction_date::DATE BETWEEN :start_date AND :end_date
            AND transaction_type IN :transaction_types
            GROUP BY transaction_date::DATE
        ) AS daily_transactions
    """
    avg_daily_tx_df = fetch_data(query_avg_daily_tx, params)
    avg_daily_transactions = avg_daily_tx_df.iloc[0, 0] if not avg_daily_tx_df.empty else 0

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("<div class=\"metric-card\"><h3>Total Customers</h3><p>" + f"{total_customers:,}" + "</p></div>",
                    unsafe_allow_html=True)
    with col2:
        st.markdown(
            "<div class=\"metric-card\"><h3>Total Transactions</h3><p>" + f"{total_transactions:,}" + "</p></div>",
            unsafe_allow_html=True)
    with col3:
        st.markdown(
            "<div class=\"metric-card\"><h3>Avg. Transaction Value</h3><p>" + f"₫{avg_transaction_value:,.2f}" + "</p></div>",
            unsafe_allow_html=True)
    with col4:
        st.markdown(
            "<div class=\"metric-card\"><h3>Fraud Detection Rate</h3><p>" + f"{fraud_detection_rate:.2f}%" + "</p></div>",
            unsafe_allow_html=True)

    col5, col6 = st.columns(2)
    with col5:
        st.markdown(
            "<div class=\"metric-card\"><h3>Transaction Success Rate</h3><p>" + f"{transaction_success_rate:.2f}%" + "</p></div>",
            unsafe_allow_html=True)
    with col6:
        st.markdown(
            "<div class=\"metric-card\"><h3>Avg. Daily Transactions</h3><p>" + f"{avg_daily_transactions:,.0f}" + "</p></div>",
            unsafe_allow_html=True)

with metric_tabs[1]:  # Customer & Device Metrics
    # Total Bank Accounts
    total_bank_accounts_df = fetch_data("SELECT COUNT(*) FROM bank_accounts")
    total_bank_accounts = total_bank_accounts_df.iloc[0, 0] if not total_bank_accounts_df.empty else 0

    # Total Devices
    total_devices_df = fetch_data("SELECT COUNT(*) FROM devices")
    total_devices = total_devices_df.iloc[0, 0] if not total_devices_df.empty else 0

    # Average Account Balance
    avg_account_balance_df = fetch_data("SELECT COALESCE(AVG(balance), 0) FROM bank_accounts")
    avg_account_balance = avg_account_balance_df.iloc[0, 0] if not avg_account_balance_df.empty else 0

    # Number of Trusted Devices
    trusted_devices_df = fetch_data("SELECT COUNT(*) FROM devices WHERE is_trusted = TRUE")
    trusted_devices = trusted_devices_df.iloc[0, 0] if not trusted_devices_df.empty else 0

    # New Metric 3: New Customers (within date range)
    query_new_customers = """
        SELECT COUNT(*)
        FROM customers
        WHERE registration_date::DATE BETWEEN :start_date AND :end_date
    """
    new_customers_df = fetch_data(query_new_customers, params)
    new_customers = new_customers_df.iloc[0, 0] if not new_customers_df.empty else 0

    # New Metric 4: Average Accounts per Customer
    query_avg_accounts_per_customer = """
        SELECT COALESCE(AVG(account_count), 0)
        FROM (
            SELECT customer_id, COUNT(*) AS account_count
            FROM bank_accounts
            GROUP BY customer_id
        ) AS customer_account_counts
    """
    avg_accounts_per_customer_df = fetch_data(query_avg_accounts_per_customer, params)
    avg_accounts_per_customer = avg_accounts_per_customer_df.iloc[0, 0] if not avg_accounts_per_customer_df.empty else 0

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(
            "<div class=\"metric-card\"><h3>Total Bank Accounts</h3><p>" + f"{total_bank_accounts:,}" + "</p></div>",
            unsafe_allow_html=True)
    with col2:
        st.markdown("<div class=\"metric-card\"><h3>Total Devices</h3><p>" + f"{total_devices:,}" + "</p></div>",
                    unsafe_allow_html=True)
    with col3:
        st.markdown(
            "<div class=\"metric-card\"><h3>Avg. Account Balance</h3><p>" + f"₫{avg_account_balance:,.2f}" + "</p></div>",
            unsafe_allow_html=True)
    with col4:
        st.markdown("<div class=\"metric-card\"><h3>Trusted Devices</h3><p>" + f"{trusted_devices:,}" + "</p></div>",
                    unsafe_allow_html=True)

    col5, col6 = st.columns(2)
    with col5:
        st.markdown("<div class=\"metric-card\"><h3>New Customers</h3><p>" + f"{new_customers:,}" + "</p></div>",
                    unsafe_allow_html=True)
    with col6:
        st.markdown(
            "<div class=\"metric-card\"><h3>Avg. Accounts/Customer</h3><p>" + f"{avg_accounts_per_customer:.2f}" + "</p></div>",
            unsafe_allow_html=True)

with metric_tabs[2]:  # Security Metrics
    # Total Authentication Logs
    total_auth_logs_df = fetch_data("SELECT COUNT(*) FROM authentication_logs")
    total_auth_logs = total_auth_logs_df.iloc[0, 0] if not total_auth_logs_df.empty else 0

    # Total Risk Alerts
    total_risk_alerts_df = fetch_data("SELECT COUNT(*) FROM risk_alerts")
    total_risk_alerts = total_risk_alerts_df.iloc[0, 0] if not total_risk_alerts_df.empty else 0

    # Number of Failed Authentications
    failed_auth_df = fetch_data("SELECT COUNT(*) FROM authentication_logs WHERE auth_result = 'failed'")
    failed_auth = failed_auth_df.iloc[0, 0] if not failed_auth_df.empty else 0

    # High Security Transactions (using security_level C or D)
    high_security_tx_df = fetch_data("SELECT COUNT(*) FROM payment_transactions WHERE security_level IN ('C', 'D')",
                                     params)
    high_security_tx = high_security_tx_df.iloc[0, 0] if not high_security_tx_df.empty else 0

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("<div class=\"metric-card\"><h3>Total Auth Logs</h3><p>" + f"{total_auth_logs:,}" + "</p></div>",
                    unsafe_allow_html=True)
    with col2:
        st.markdown(
            "<div class=\"metric-card\"><h3>Total Risk Alerts</h3><p>" + f"{total_risk_alerts:,}" + "</p></div>",
            unsafe_allow_html=True)
    with col3:
        st.markdown("<div class=\"metric-card\"><h3>Failed Authentications</h3><p>" + f"{failed_auth:,}" + "</p></div>",
                    unsafe_allow_html=True)
    with col4:
        st.markdown(
            "<div class=\"metric-card\"><h3>High Security Txns</h3><p>" + f"{high_security_tx:,}" + "</p></div>",
            unsafe_allow_html=True)

# Visualizations Section
st.markdown("<div class=\"subheader\">Visualizations</div>", unsafe_allow_html=True)

visualization_tabs = st.tabs(["Transaction Analysis", "Customer & Security Analysis", "Device & Authentication Trends"])

with visualization_tabs[0]:  # Transaction Analysis Tab
    st.markdown("### Transaction Volume & Value Trends")
    # Time-series Chart: Transactions Over Time
    query_time_series = """
        SELECT transaction_date::DATE AS date, COUNT(*) AS transaction_count, SUM(amount) AS total_amount
        FROM payment_transactions
        WHERE transaction_date::DATE BETWEEN :start_date AND :end_date
        AND transaction_type IN :transaction_types
        GROUP BY transaction_date::DATE
        ORDER BY date
    """
    df_transactions = fetch_data(query_time_series, params)
    df_transactions['date'] = pd.to_datetime(df_transactions['date'])
    if not df_transactions.empty:
        fig_time_series = px.line(
            df_transactions, x="date", y="transaction_count",
            title="Transactions Over Time",
            labels={"date": "Date", "transaction_count": "Number of Transactions"},
            template="plotly_white",
            line_shape="spline",  # Smooth the line
            color_discrete_sequence=px.colors.qualitative.Plotly  # Use a nice color palette
        )
        fig_time_series.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color="#333",
            title_font_size=24,
            title_font_color="#1a2a3a",
            xaxis_title_font_size=18,
            yaxis_title_font_size=18,
            margin=dict(l=40, r=40, t=80, b=40),
            hovermode="x unified"
        )
        st.plotly_chart(fig_time_series, use_container_width=True)

        fig_amount_time_series = px.line(
            df_transactions, x="date", y="total_amount",
            title="Total Transaction Amount Over Time",
            labels={"date": "Date", "total_amount": "Total Amount (₫)"},
            template="plotly_white",
            line_shape="spline",
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        fig_amount_time_series.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color="#333",
            title_font_size=24,
            title_font_color="#1a2a3a",
            xaxis_title_font_size=18,
            yaxis_title_font_size=18,
            margin=dict(l=40, r=40, t=80, b=40),
            hovermode="x unified"
        )
        st.plotly_chart(fig_amount_time_series, use_container_width=True)
    else:
        st.info("No transaction data available for the selected filters to display time-series charts.")

    # Transaction Volume by Type (Bar Chart)
    st.markdown("### Transaction Volume by Type")
    query_tx_volume_by_type = """
        SELECT transaction_type, COUNT(*) AS transaction_count, SUM(amount) AS total_amount
        FROM payment_transactions
        WHERE transaction_date::DATE BETWEEN :start_date AND :end_date
        AND transaction_type IN :transaction_types
        GROUP BY transaction_type
        ORDER BY total_amount DESC
    """
    df_tx_volume_by_type = fetch_data(query_tx_volume_by_type, params)
    if not df_tx_volume_by_type.empty:
        fig_tx_volume = px.bar(
            df_tx_volume_by_type, x="transaction_type", y="total_amount",
            title="Total Transaction Amount by Type",
            labels={"transaction_type": "Transaction Type", "total_amount": "Total Amount (₫)"},
            template="plotly_white",
            color="transaction_type",
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        fig_tx_volume.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color="#333",
            title_font_size=24,
            title_font_color="#1a2a3a",
            xaxis_title_font_size=18,
            yaxis_title_font_size=18,
            margin=dict(l=40, r=40, t=80, b=40)
        )
        st.plotly_chart(fig_tx_volume, use_container_width=True)
    else:
        st.info("No transaction volume data by type available for the selected filters.")

    # Transaction Status Distribution (Pie Chart)
    st.markdown("### Transaction Status Distribution")
    query_tx_status_dist = """
        SELECT status, COUNT(*) AS status_count
        FROM payment_transactions
        WHERE transaction_date::DATE BETWEEN :start_date AND :end_date
        AND transaction_type IN :transaction_types
        GROUP BY status
    """
    df_tx_status_dist = fetch_data(query_tx_status_dist, params)
    if not df_tx_status_dist.empty:
        fig_tx_status = px.pie(
            df_tx_status_dist, names="status", values="status_count",
            title="Transaction Status Distribution",
            template="plotly_white",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.D3
        )
        fig_tx_status.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color="#333",
            title_font_size=24,
            title_font_color="#1a2a3a",
            margin=dict(l=40, r=40, t=80, b=40)
        )
        st.plotly_chart(fig_tx_status, use_container_width=True)
    else:
        st.info("No transaction status data available for the selected filters.")

    # Top Customers by Transaction Amount (Bar Chart)
    st.markdown("### Top 10 Customers by Transaction Amount")
    query_top_customers = """
        SELECT c.full_name, SUM(pt.amount) AS total_amount
        FROM payment_transactions pt
        JOIN customers c ON pt.customer_id = c.customer_id
        WHERE pt.transaction_date::DATE BETWEEN :start_date AND :end_date
        AND pt.transaction_type IN :transaction_types
        GROUP BY c.full_name
        ORDER BY total_amount DESC
        LIMIT 10
    """
    df_top_customers = fetch_data(query_top_customers, params)
    if not df_top_customers.empty:
        fig_top_customers = px.bar(
            df_top_customers, x="full_name", y="total_amount",
            title="Top 10 Customers by Total Transaction Amount",
            labels={"full_name": "Customer Name", "total_amount": "Total Amount (₫)"},
            template="plotly_white",
            color="full_name",
            color_discrete_sequence=px.colors.qualitative.G10
        )
        fig_top_customers.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color="#333",
            title_font_size=24,
            title_font_color="#1a2a3a",
            xaxis_title_font_size=18,
            yaxis_title_font_size=18,
            margin=dict(l=40, r=40, t=80, b=40)
        )
        st.plotly_chart(fig_top_customers, use_container_width=True)
    else:
        st.info("No top customer data available for the selected filters.")

with visualization_tabs[1]:  # Customer & Security Analysis Tab
    st.markdown("### Customer Demographics & Risk Overview")
    # Bar Chart: Customer Types
    query_customer_types = """
        SELECT customer_type, COUNT(*) AS customer_count
        FROM customers
        WHERE customer_type IN :customer_segments
        GROUP BY customer_type
    """
    df_customer_types = fetch_data(query_customer_types, params)
    if not df_customer_types.empty:
        fig_bar = px.bar(
            df_customer_types, x="customer_type", y="customer_count",
            title="Customer Type Distribution",
            labels={"customer_type": "Customer Type", "customer_count": "Number of Customers"},
            color="customer_type",
            template="plotly_white",
            color_discrete_sequence=px.colors.qualitative.Pastel  # Use a nice color palette
        )
        fig_bar.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color="#333",
            title_font_size=24,
            title_font_color="#1a2a3a",
            xaxis_title_font_size=18,
            yaxis_title_font_size=18,
            margin=dict(l=40, r=40, t=80, b=40)
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("No customer data available for the selected customer segments to display customer type distribution.")

    # Pie Chart: Risk Alert Categories
    st.markdown("### Risk Alert Categories")
    query_risk_alerts = """
        SELECT ra.alert_type, COUNT(*) AS alert_count
        FROM risk_alerts ra
        JOIN payment_transactions pt ON ra.transaction_id = pt.transaction_id
        WHERE pt.transaction_date::DATE BETWEEN :start_date AND :end_date
        AND pt.transaction_type IN :transaction_types
        GROUP BY ra.alert_type
    """
    df_risk_alerts = fetch_data(query_risk_alerts, params)
    if not df_risk_alerts.empty:
        fig_pie = px.pie(
            df_risk_alerts, names="alert_type", values="alert_count",
            title="Risk Alert Categories",
            template="plotly_white",
            hole=0.3,  # Make it a donut chart
            color_discrete_sequence=px.colors.qualitative.Set3  # Use a nice color palette
        )
        fig_pie.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color="#333",
            title_font_size=24,
            title_font_color="#1a2a3a",
            margin=dict(l=40, r=40, t=80, b=40)
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("No risk alert data available for the selected filters to display risk alert categories.")

    # Risky Transaction Count Section
    st.markdown("### Risky Transactions by Type")
    query_risky_transactions = """
        SELECT pt.transaction_type, COUNT(*) AS risky_count
        FROM payment_transactions pt
        WHERE pt.is_suspicious = TRUE
        AND pt.transaction_date::DATE BETWEEN :start_date AND :end_date
        AND pt.transaction_type IN :transaction_types
        GROUP BY pt.transaction_type
        ORDER BY risky_count DESC
    """
    df_risky_transactions = fetch_data(query_risky_transactions, params)
    if not df_risky_transactions.empty:
        fig_risky = px.bar(
            df_risky_transactions, x="transaction_type", y="risky_count",
            title="Risky Transactions by Type",
            labels={"transaction_type": "Transaction Type", "risky_count": "Count"},
            template="plotly_white",
            color="transaction_type",
            color_discrete_sequence=px.colors.qualitative.Prism
        )
        fig_risky.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color="#333",
            title_font_size=24,
            title_font_color="#1a2a3a",
            xaxis_title_font_size=18,
            yaxis_title_font_size=18,
            margin=dict(l=40, r=40, t=80, b=40)
        )
        st.plotly_chart(fig_risky, use_container_width=True)
    else:
        st.info("No risky transactions found for the selected filters.")

    # New Chart: Transaction Security Level Distribution (Pie Chart)
    st.markdown("### Transaction Security Level Distribution")
    query_security_level_dist = """
        SELECT security_level, COUNT(*) AS count
        FROM payment_transactions
        WHERE transaction_date::DATE BETWEEN :start_date AND :end_date
        AND transaction_type IN :transaction_types
        GROUP BY security_level
        ORDER BY security_level
    """
    df_security_level_dist = fetch_data(query_security_level_dist, params)
    if not df_security_level_dist.empty:
        fig_security_level = px.pie(
            df_security_level_dist, names="security_level", values="count",
            title="Transaction Security Level Distribution",
            template="plotly_white",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_security_level.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color="#333",
            title_font_size=24,
            title_font_color="#1a2a3a",
            margin=dict(l=40, r=40, t=80, b=40)
        )
        st.plotly_chart(fig_security_level, use_container_width=True)
    else:
        st.info("No security level data available for the selected filters.")

with visualization_tabs[2]:  # Device & Authentication Trends Tab
    st.markdown("### Device & Authentication Insights")
    # Authentication Method Usage (Bar Chart)
    query_auth_method_usage = """
        SELECT am.method_name, COUNT(al.log_id) AS usage_count
        FROM authentication_logs al
        JOIN authentication_methods am ON al.auth_method_id = am.auth_id
        JOIN payment_transactions pt ON al.transaction_id = pt.transaction_id
        WHERE pt.transaction_date::DATE BETWEEN :start_date AND :end_date
        AND pt.transaction_type IN :transaction_types
        GROUP BY am.method_name
        ORDER BY usage_count DESC
    """
    df_auth_method_usage = fetch_data(query_auth_method_usage, params)
    if not df_auth_method_usage.empty:
        fig_auth_method = px.bar(
            df_auth_method_usage, x="method_name", y="usage_count",
            title="Authentication Method Usage",
            labels={"method_name": "Authentication Method", "usage_count": "Usage Count"},
            template="plotly_white",
            color="method_name",
            color_discrete_sequence=px.colors.qualitative.Vivid
        )
        fig_auth_method.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color="#333",
            title_font_size=24,
            title_font_color="#1a2a3a",
            xaxis_title_font_size=18,
            yaxis_title_font_size=18,
            margin=dict(l=40, r=40, t=80, b=40)
        )
        st.plotly_chart(fig_auth_method, use_container_width=True)
    else:
        st.info("No authentication method usage data available for the selected filters.")

    # Top Failed Checks Section
    st.markdown("### Top Failed Authentication Checks")
    query_failed_checks = """
        SELECT al.failure_reason, COUNT(*) AS failure_count
        FROM authentication_logs al
        JOIN payment_transactions pt ON al.transaction_id = pt.transaction_id
        WHERE al.auth_result = 'failed'
        AND pt.transaction_date::DATE BETWEEN :start_date AND :end_date
        AND pt.transaction_type IN :transaction_types
        GROUP BY al.failure_reason
        ORDER BY failure_count DESC
        LIMIT 5
    """
    df_failed_checks = fetch_data(query_failed_checks, params)
    if not df_failed_checks.empty:
        fig_failed = px.bar(
            df_failed_checks, x="failure_reason", y="failure_count",
            title="Top Failed Authentication Checks",
            labels={"failure_reason": "Failure Reason", "failure_count": "Count"},
            template="plotly_white",
            color="failure_reason",
            color_discrete_sequence=px.colors.qualitative.Dark2
        )
        fig_failed.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color="#333",
            title_font_size=24,
            title_font_color="#1a2a3a",
            xaxis_title_font_size=18,
            yaxis_title_font_size=18,
            margin=dict(l=40, r=40, t=80, b=40)
        )
        st.plotly_chart(fig_failed, use_container_width=True)
    else:
        st.info("No failed authentication checks found for the selected filters.")

    # Unverified Devices by Customer Section
    st.markdown("### Unverified Devices by Customer")
    query_unverified_devices = """
        SELECT c.full_name, c.customer_type, COUNT(d.device_id) AS unverified_count
        FROM customers c
        JOIN devices d ON c.customer_id = d.customer_id
        WHERE d.is_trusted = FALSE
        AND c.customer_type IN :customer_segments
        GROUP BY c.full_name, c.customer_type
        ORDER BY unverified_count DESC
        LIMIT 10
    """
    df_unverified_devices = fetch_data(query_unverified_devices, params)
    if not df_unverified_devices.empty:
        st.dataframe(df_unverified_devices, use_container_width=True)
    else:
        st.info("No unverified devices found for the selected filters.")

    # New Chart: Device Type Distribution (Pie Chart)
    st.markdown("### Device Type Distribution")
    query_device_type_dist = """
        SELECT device_type, COUNT(*) AS count
        FROM devices
        GROUP BY device_type
    """
    df_device_type_dist = fetch_data(query_device_type_dist, params)
    if not df_device_type_dist.empty:
        fig_device_type = px.pie(
            df_device_type_dist, names="device_type", values="count",
            title="Device Type Distribution",
            template="plotly_white",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        fig_device_type.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color="#333",
            title_font_size=24,
            title_font_color="#1a2a3a",
            margin=dict(l=40, r=40, t=80, b=40)
        )
        st.plotly_chart(fig_device_type, use_container_width=True)
    else:
        st.info("No device type data available.")

# Data Table Preview Section (kept outside tabs for easy access)
st.markdown("<div class=\"subheader\">Data Table Preview (Recent Risky Transactions)</div>", unsafe_allow_html=True)
query_data_preview = """
    SELECT 
        pt.transaction_id, 
        pt.transaction_type, 
        pt.amount, 
        pt.transaction_date, 
        pt.status, 
        c.full_name, 
        c.customer_type
    FROM payment_transactions pt
    JOIN customers c ON pt.customer_id = c.customer_id
    WHERE pt.is_suspicious = TRUE
    AND pt.transaction_date::DATE BETWEEN :start_date AND :end_date
    AND pt.transaction_type IN :transaction_types
    ORDER BY pt.transaction_date DESC
    LIMIT 10
"""
df_data_preview = fetch_data(query_data_preview, params)
if not df_data_preview.empty:
    st.dataframe(df_data_preview, use_container_width=True)
else:
    st.info("No recent risky transactions found for the selected filters.")
