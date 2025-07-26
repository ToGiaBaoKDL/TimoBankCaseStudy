import streamlit as st


def load_css():
    """Injects custom CSS for dashboard styling."""
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');

        html, body, [class*="st-"] {
            font-family: 'Roboto', sans-serif;
            color: #2c3e50;
        }

        .main {
            background-color: #f0f2f6;
            padding: 1.5em 3em;
        }

        .stMainBlockContainer {
            max-width:60rem;
        }

        .stApp {
            background-color: #f0f2f6;
        }

        .header {
            color: #1a2a3a;
            font-size: 3em;
            font-weight: 800;
            margin-bottom: 0.05em;
            text-align: center;
            text-shadow: 2px 2px 6px rgba(0,0,0,0.15);
            padding-top: 0.8em;
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
            padding: 0.5em;
            border-radius: 18px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.12);
            margin-bottom: 1em;
            text-align: center;
            transition: all 0.3s ease-in-out;
            border: 1px solid #e0e0e0;
        }
        .metric-card:hover {
            transform: translateY(-8px) scale(1.02);
            box-shadow: 0 12px 30px rgba(0,0,0,0.18);
        }

        .metric-card .card-header {
            color: #34495e;
            font-size: 1.2em;
            margin-bottom: 0.1em;
            font-weight: bold;
            text-align: center;
        }
        .metric-card p {
            font-size: 1.4em;
            font-weight: bold;
            color: #007bff;
            margin: 0;
        }

        .metric-card ul {
            font-size: 1em;
            color: #444;
            line-height: 1.7;
            padding-left: 8px;
            text-align: left;
        }

        .metric-card ul li {
            margin-bottom: 8px;
            transition: all 0.2s ease-in-out;
        }

        .metric-card ul li:hover {
            color: #4e54c8;
            transform: translateX(4px);
        }

        .sidebar .sidebar-content {
            background-color: #ffffff;
            padding: 2.5em;
            border-radius: 15px;
            box-shadow: 0 6px 20px rgba(0,0,0,0.1);
            border: 1px solid #e0e0e0;
        }

        /* Modern Filter Button Styles */
        .filter-button-container {
            margin-top: 2em;
            padding-top: 1.5em;
            border-top: 2px solid #e0e0e0;
            display: flex;
            flex-direction: column;
            gap: 0.8em;
        }

        .apply-filter-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 12px;
            padding: 0.9em 1.5em;
            font-size: 1.1em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
            position: relative;
            overflow: hidden;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .apply-filter-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
            background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
        }

        .apply-filter-btn:active {
            transform: translateY(0px);
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }

        .reset-filter-btn {
            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
            color: white;
            border: none;
            border-radius: 12px;
            padding: 0.8em 1.5em;
            font-size: 1em;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(255, 107, 107, 0.4);
            position: relative;
            overflow: hidden;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .reset-filter-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(255, 107, 107, 0.6);
            background: linear-gradient(135deg, #ee5a24 0%, #ff6b6b 100%);
        }

        .reset-filter-btn:active {
            transform: translateY(0px);
            box-shadow: 0 4px 15px rgba(255, 107, 107, 0.4);
        }

        /* Button ripple effect */
        .apply-filter-btn::before, .reset-filter-btn::before {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.3);
            transition: width 0.6s, height 0.6s, top 0.6s, left 0.6s;
            transform: translate(-50%, -50%);
            z-index: 0;
        }

        .apply-filter-btn:active::before, .reset-filter-btn:active::before {
            width: 300px;
            height: 300px;
            top: 50%;
            left: 50%;
        }

        .apply-filter-btn span, .reset-filter-btn span {
            position: relative;
            z-index: 1;
        }

        /* Filter status indicator */
        .filter-status {
            background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
            color: white;
            padding: 0.5em 1em;
            border-radius: 20px;
            font-size: 0.9em;
            text-align: center;
            margin-bottom: 1em;
            font-weight: 500;
            box-shadow: 0 2px 10px rgba(116, 185, 255, 0.3);
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

        .sidebar-title {
            font-size: 1.6em;
            font-weight: 700;
            margin-bottom: 0.5em;
            color: #4e54c8;
        }
        .sidebar-section {
            margin-bottom: 1em;
            padding-bottom: 0.5em;
            border-bottom: 1px solid #e0e0e0;
        }
        .sidebar-section b {
            font-size: 1.2em;
            color: #34495e;
        }
    </style>
    """, unsafe_allow_html=True)
