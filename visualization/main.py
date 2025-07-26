# main.py
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import config
import database
from visualization.queries import SQLQueries
import ui_components
import styles

# --- Streamlit Page Configuration ---
st.set_page_config(
    page_title="Timo Digital Bank Dashboard", layout="wide",
    initial_sidebar_state="expanded", page_icon="🏦"
)

# --- Apply Custom CSS ---
styles.load_css()


# --- Session State Initialization ---
def initialize_session_state():
    """Initializes Streamlit session state variables for filters."""
    if 'applied_filters' not in st.session_state:
        st.session_state.applied_filters = {
            'date_range': [datetime.now() - timedelta(days=30), datetime.now()],
            'customer_segments': config.DEFAULT_CUSTOMER_SEGMENTS,
            'transaction_types': config.ALL_TRANSACTION_TYPES,
            'transaction_statuses': config.ALL_TRANSACTION_STATUSES,
            'auth_results': config.ALL_AUTH_RESULTS,
            'alert_statuses': config.ALL_ALERT_STATUSES,
            'security_levels': config.ALL_SECURITY_LEVELS  # Add new filter here
        }


initialize_session_state()

# --- Sidebar for Filters ---
with st.sidebar:
    st.markdown('<div class="sidebar-title">📊 Dashboard Filters</div>', unsafe_allow_html=True)
    with st.form(key="filter_form"):
        st.markdown('<div class="sidebar-section"><b>📅 Date Range</b></div>', unsafe_allow_html=True)
        date_range = st.date_input("Select Range", value=st.session_state.applied_filters['date_range'],
                                   min_value=datetime(2023, 1, 1), max_value=datetime.now())
        st.markdown('<div class="sidebar-section"><b>👥 Customer Segment</b></div>', unsafe_allow_html=True)
        customer_segments = st.multiselect("Choose segments", options=config.DEFAULT_CUSTOMER_SEGMENTS,
                                           default=st.session_state.applied_filters['customer_segments'])
        st.markdown('<div class="sidebar-section"><b>💳 Transaction Types</b></div>', unsafe_allow_html=True)
        transaction_types = st.multiselect("Choose types", options=config.ALL_TRANSACTION_TYPES,
                                           default=st.session_state.applied_filters['transaction_types'])
        st.markdown('<div class="sidebar-section"><b>📊 Transaction Statuses</b></div>', unsafe_allow_html=True)
        transaction_statuses = st.multiselect("Choose statuses", options=config.ALL_TRANSACTION_STATUSES,
                                              default=st.session_state.applied_filters['transaction_statuses'])
        st.markdown('<div class="sidebar-section"><b>🔐 Auth Results</b></div>', unsafe_allow_html=True)
        auth_results = st.multiselect("Choose results", options=config.ALL_AUTH_RESULTS,
                                      default=st.session_state.applied_filters['auth_results'])
        st.markdown('<div class="sidebar-section"><b>🚨 Alert Statuses</b></div>', unsafe_allow_html=True)
        alert_statuses = st.multiselect("Choose statuses", options=config.ALL_ALERT_STATUSES,
                                        default=st.session_state.applied_filters['alert_statuses'])
        # New Filter: Security Level
        st.markdown('<div class="sidebar-section"><b>🛡️ Security Level</b></div>', unsafe_allow_html=True)  #
        security_levels = st.multiselect("Choose security levels", options=config.ALL_SECURITY_LEVELS,  #
                                         default=st.session_state.applied_filters['security_levels'])  #

        col1, col2 = st.columns(2)
        with col1:
            apply_button = st.form_submit_button("🔍 Apply", use_container_width=True)
        with col2:
            reset_button = st.form_submit_button("🔄 Reset", use_container_width=True)

        if apply_button:
            st.session_state.applied_filters = {
                'date_range': list(date_range) if isinstance(date_range, tuple) and len(date_range) == 2 else [
                    datetime.now() - timedelta(days=30), datetime.now()],
                'customer_segments': customer_segments, 'transaction_types': transaction_types,
                'transaction_statuses': transaction_statuses, 'auth_results': auth_results,
                'alert_statuses': alert_statuses,
                'security_levels': security_levels,  # Update session state with new filter
            }
            st.rerun()
        if reset_button:
            st.session_state.applied_filters = {
                'date_range': [datetime.now() - timedelta(days=30), datetime.now()],
                'customer_segments': config.DEFAULT_CUSTOMER_SEGMENTS,
                'transaction_types': config.ALL_TRANSACTION_TYPES,
                'transaction_statuses': config.ALL_TRANSACTION_STATUSES, 'auth_results': config.ALL_AUTH_RESULTS,
                'alert_statuses': config.ALL_ALERT_STATUSES,
                'security_levels': config.ALL_SECURITY_LEVELS  # Reset new filter
            }
            st.rerun()

# --- Main Dashboard Content ---
ui_components.display_app_header()

params = {
    "start_date": st.session_state.applied_filters['date_range'][0],
    "end_date": st.session_state.applied_filters['date_range'][1],
    "customer_segments": tuple(st.session_state.applied_filters['customer_segments']) or (None,),
    "transaction_types": tuple(st.session_state.applied_filters['transaction_types']) or (None,),
    "transaction_statuses": tuple(st.session_state.applied_filters['transaction_statuses']) or (None,),
    "auth_results": tuple(st.session_state.applied_filters['auth_results']) or (None,),
    "alert_statuses": tuple(st.session_state.applied_filters['alert_statuses']) or (None,),
    "security_levels": tuple(st.session_state.applied_filters['security_levels']) or (None,)
    # Pass new filter to params
}


# --- Fragment Definitions ---
@st.fragment
def render_kpis_fragment(current_params):
    st.markdown("<div class=\"subheader\">Key Performance Indicators</div>", unsafe_allow_html=True)
    kpi_row1 = st.columns(3)
    kpi_row2 = st.columns(3)
    with kpi_row1[0]:
        total_transactions_df = database.fetch_data(SQLQueries.TOTAL_TRANSACTIONS, current_params)
        total_transactions = total_transactions_df.iloc[0, 0] if not total_transactions_df.empty else 0
        ui_components.metric_card("Total Transactions", f"{total_transactions:,}")
    with kpi_row1[1]:
        total_amount_df = database.fetch_data(SQLQueries.TOTAL_TRANSACTION_AMOUNT, current_params)
        total_amount = total_amount_df.iloc[0, 0] if not total_amount_df.empty else 0
        ui_components.metric_card("Total Transaction Amount", f"{total_amount:,.0f} VND")
    with kpi_row1[2]:
        active_customers_df = database.fetch_data(SQLQueries.ACTIVE_CUSTOMERS_PERIOD, current_params)
        active_customers = active_customers_df.iloc[0, 0] if not active_customers_df.empty else 0
        ui_components.metric_card("Active Customers (Period)", f"{active_customers:,}")
    with kpi_row2[0]:
        suspicious_amount_df = database.fetch_data(SQLQueries.SUSPICIOUS_TRANSACTION_AMOUNT, current_params)
        suspicious_amount = suspicious_amount_df.iloc[0, 0] if not suspicious_amount_df.empty else 0
        ui_components.metric_card("Suspicious Txn Amount", f"{suspicious_amount:,.0f} VND")
    with kpi_row2[1]:
        auth_success_rate_df = database.fetch_data(SQLQueries.AUTHENTICATION_SUCCESS_RATE, current_params)
        auth_success_rate = auth_success_rate_df.iloc[0, 0] if not auth_success_rate_df.empty else 0
        ui_components.metric_card("Auth Success Rate", f"{auth_success_rate:.2f}%")
    with kpi_row2[2]:
        total_open_alerts_df = database.fetch_data(SQLQueries.TOTAL_OPEN_RISK_ALERTS)
        total_open_alerts = total_open_alerts_df.iloc[0, 0] if not total_open_alerts_df.empty else 0
        ui_components.metric_card("Open Risk Alerts", f"{total_open_alerts:,}")


@st.fragment
def render_overview_tab_content_fragment(current_params):
    st.markdown("<div class=\"subheader\">Daily Transaction Trends</div>", unsafe_allow_html=True)
    daily_trend_df = database.fetch_data(SQLQueries.DAILY_TRANSACTION_TREND, current_params)
    if not daily_trend_df.empty:
        daily_trend_df["transaction_day"] = pd.to_datetime(daily_trend_df["transaction_day"])
        ui_components.plot_line_chart(daily_trend_df, x="transaction_day", y="daily_transaction_amount",
                                      title="Daily Transaction Amount", x_label="Date", y_label="Total Amount (VND)")
        ui_components.plot_line_chart(daily_trend_df, x="transaction_day", y="daily_transaction_count",
                                      title="Daily Transaction Count", x_label="Date", y_label="Number of Transactions")


@st.fragment
def render_transactions_tab_content_fragment(current_params):
    st.markdown("<div class=\"subheader\">Transaction Analysis</div>", unsafe_allow_html=True)

    # Charts are now consecutive, not side-by-side
    volume_by_type_df = database.fetch_data(SQLQueries.TRANSACTION_VOLUME_BY_TYPE, current_params)
    ui_components.plot_pie_chart(volume_by_type_df, values="count", names="transaction_type",
                                 title="Transaction Volume by Type")

    status_dist_df = database.fetch_data(SQLQueries.TRANSACTION_STATUS_DISTRIBUTION, current_params)
    ui_components.plot_bar_chart(status_dist_df, x="status", y="count", title="Transaction Status Distribution",
                                 x_label="Status", y_label="Count", color_column="status",
                                 color_map={"completed": "#28a745", "failed": "#dc3545", "pending": "#ffc107",
                                            "cancelled": "#6c757d"})

    # Funnel chart for transaction stages
    funnel_df = database.fetch_data(SQLQueries.TRANSACTION_FUNNEL, current_params)
    if not funnel_df.empty:
        funnel_df = funnel_df.sort_values('stage').reset_index(drop=True)
        ui_components.plot_funnel_chart(funnel_df, x="value", y="stage", title="Transaction Completion Funnel")

    # Funnel chart for security levels
    st.markdown("<h4>Transaction Flow by Security Level</h4>", unsafe_allow_html=True)
    security_level_counts_df = database.fetch_data(SQLQueries.TRANSACTION_COUNT_BY_SECURITY_LEVEL, current_params)  #
    ui_components.plot_funnel_chart(security_level_counts_df, x='transaction_count', y='security_level',  #
                                    title='Transaction Count by Security Level')  #

    heatmap_df = database.fetch_data(SQLQueries.TRANSACTION_HEATMAP, current_params)
    if not heatmap_df.empty:
        day_map = {1: 'Mon', 2: 'Tue', 3: 'Wed', 4: 'Thu', 5: 'Fri', 6: 'Sat', 7: 'Sun'}
        heatmap_df['day_of_week_name'] = heatmap_df['day_of_week'].map(day_map)
        heatmap_pivot = pd.pivot_table(heatmap_df, values='transaction_count', index='day_of_week_name',
                                       columns='hour_of_day', fill_value=0).reindex(day_map.values())
        ui_components.plot_heatmap(heatmap_pivot, title="Transactions by Day and Hour", x_label="Hour of Day",
                                   y_label="Day of Week")


@st.fragment
def render_security_risk_tab_content_fragment(current_params):
    st.markdown("<div class=\"subheader\">Security and Risk Analysis</div>", unsafe_allow_html=True)

    # Charts are now consecutive, not side-by-side
    auth_result_df = database.fetch_data(SQLQueries.AUTH_RESULT_BREAKDOWN, current_params)
    ui_components.plot_pie_chart(auth_result_df, values="count", names="auth_result", title="Auth Result Distribution",
                                 color_column="auth_result",
                                 color_map={"success": "#28a745", "failed": "#dc3545", "expired": "#ffc107",
                                            "cancelled": "#6c757d"})

    risk_alert_types_df = database.fetch_data(SQLQueries.RISK_ALERT_TYPES_DISTRIBUTION, current_params)
    ui_components.plot_pie_chart(risk_alert_types_df, values="count", names="alert_type", title="Risk Alert Types")

    st.markdown("<h4>Authentication Method Analysis</h4>", unsafe_allow_html=True)
    auth_method_df = database.fetch_data(SQLQueries.AUTH_METHOD_ANALYSIS, current_params)
    if not auth_method_df.empty:
        auth_method_df['success_rate_text'] = auth_method_df['success_rate'].astype(str) + '%'
        ui_components.plot_bar_chart(auth_method_df, x="method_name", y="total_attempts",
                                     title="Authentication Method Usage & Success Rate", x_label="Method",
                                     y_label="Total Attempts", color_column="security_level",
                                     text_column='success_rate_text')


@st.fragment  #
def render_customer_behavior_tab_content_fragment(current_params):  #
    st.markdown("<div class=\"subheader\">Customer Behavior Analysis</div>", unsafe_allow_html=True)  #
    st.info("This section provides insights into customer transaction patterns and engagement.")  #

    col1, col2 = st.columns(2)  #

    with col1:  #
        st.markdown("<h4>Average Transaction Value by Customer Type</h4>", unsafe_allow_html=True)  #
        avg_txn_value_df = database.fetch_data(SQLQueries.AVG_TRANSACTION_VALUE_BY_CUSTOMER_TYPE, current_params)  #
        ui_components.plot_bar_chart(avg_txn_value_df, x='customer_type', y='avg_amount',  #
                                     title='Average Transaction Value by Customer Type',  #
                                     x_label='Customer Type', y_label='Average Amount')  #

    with col2:  #
        st.markdown("<h4>Transaction Count by Customer Type</h4>", unsafe_allow_html=True)  #
        txn_count_df = database.fetch_data(SQLQueries.TRANSACTION_COUNT_BY_CUSTOMER_TYPE, current_params)  #
        ui_components.plot_bar_chart(txn_count_df, x='customer_type', y='transaction_count',  #
                                     title='Transaction Count by Customer Type',  #
                                     x_label='Customer Type', y_label='Number of Transactions')  #

    st.markdown("<h4>Top 10 Most Active Customers (by Transaction Count)</h4>", unsafe_allow_html=True)  #
    top_customers_df = database.fetch_data(SQLQueries.TOP_ACTIVE_CUSTOMERS, current_params)  #
    st.dataframe(top_customers_df, use_container_width=True)  #

    st.markdown("<h4>Transaction Frequency by Hour of Day (Heatmap)</h4>", unsafe_allow_html=True)  #
    txn_hour_df = database.fetch_data(SQLQueries.TRANSACTION_FREQUENCY_BY_HOUR, current_params)  #
    if not txn_hour_df.empty:  #
        # Pivot table for heatmap #
        txn_hour_pivot = txn_hour_df.pivot_table(index='day_of_week', columns='hour_of_day',
                                                 values='transaction_count').fillna(0)  #
        # Ensure all hours 0-23 and days Mon-Sun are present for consistent heatmap #
        all_hours = range(24)  #
        # Reorder days of the week for consistent plotting #
        day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]  #
        txn_hour_pivot = txn_hour_pivot.reindex(index=day_order, columns=all_hours).fillna(0)  #
        ui_components.plot_heatmap(txn_hour_pivot,  #
                                   title='Transaction Frequency by Day of Week and Hour',  #
                                   x_label='Hour of Day', y_label='Day of Week')  #


@st.fragment
def render_data_exploration_tab_content(current_params):
    st.markdown("<div class=\"subheader\">Data Exploration Reports</div>", unsafe_allow_html=True)
    st.info(
        "This section provides detailed, table-based reports for in-depth analysis. Reports are filtered based on the sidebar selections.")

    st.markdown("<h4>High-Value Transaction Report</h4>", unsafe_allow_html=True)
    high_value_df = database.fetch_data(SQLQueries.HIGH_VALUE_TRANSACTION_REPORT, current_params)
    st.dataframe(high_value_df, use_container_width=True)

    st.markdown("<h4>Authentication Failure Report</h4>", unsafe_allow_html=True)
    auth_failure_df = database.fetch_data(SQLQueries.AUTHENTICATION_FAILURE_REPORT, current_params)
    st.dataframe(auth_failure_df, use_container_width=True)


# --- App Layout & Tab Rendering ---
render_kpis_fragment(params)
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["📊 Overview", "💳 Transactions", "🔒 Security & Risk", " EXPLORE", "👤 Customer Behavior"])  # Add new tab

with tab1:
    render_overview_tab_content_fragment(params)
with tab2:
    render_transactions_tab_content_fragment(params)
with tab3:
    render_security_risk_tab_content_fragment(params)
with tab4:
    render_data_exploration_tab_content(params)
with tab5:  # Render new tab content
    render_customer_behavior_tab_content_fragment(params)
