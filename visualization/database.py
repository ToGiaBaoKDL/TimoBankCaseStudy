import streamlit as st
from sqlalchemy import create_engine, text
import pandas as pd
import config


# --- Database Connection Setup ---
@st.cache_resource
def get_engine():
    """Establishes and caches the database engine."""
    try:
        engine = create_engine(config.CONNECTION_STRING)
        return engine
    except Exception as e:
        st.error(f"Failed to connect to the database. Please check your .env file and database server. Error: {e}")
        st.stop()  # Stop the app if connection fails


engine = get_engine()


@st.cache_data(ttl=600)  # Cache data for 10 minutes
def fetch_data(query: str, params: dict = None) -> pd.DataFrame:
    """
    Fetches data from the database using a given SQL query and parameters.
    Caches the results.
    """
    if params is None:
        params = {}
    try:
        with engine.connect() as connection:
            # Handle empty tuple cases for SQL `ANY` clause if no filter is selected
            # This logic must align with how params are prepared in main.py
            if "customer_segments" in params and not params["customer_segments"]:
                # If no specific segments are selected, use default/all segments
                params["customer_segments"] = config.DEFAULT_CUSTOMER_SEGMENTS_TUPLE
            if "transaction_types" in params and not params["transaction_types"]:
                params["transaction_types"] = config.ALL_TRANSACTION_TYPES_TUPLE
            if "transaction_statuses" in params and not params["transaction_statuses"]:
                params["transaction_statuses"] = config.ALL_TRANSACTION_STATUSES_TUPLE
            if "auth_results" in params and not params["auth_results"]:
                params["auth_results"] = config.ALL_AUTH_RESULTS_TUPLE
            if "security_levels" in params and not params["security_levels"]:
                params["security_levels"] = config.ALL_SECURITY_LEVELS_TUPLE
            if "alert_statuses" in params and not params["alert_statuses"]:
                params["alert_statuses"] = config.ALL_ALERT_STATUSES_TUPLE

            df = pd.read_sql(text(query), connection, params=params)
            if df.empty:
                st.warning(f"No data returned for the current selection. Consider adjusting filters.")
            return df
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()
