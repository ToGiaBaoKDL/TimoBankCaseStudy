## Overview

The `visualization` directory contains the Streamlit dashboard for the Timo Digital Bank Case Study. This dashboard provides interactive analytics and visualizations for all generated and monitored data.

![Key Metric](https://ik.imagekit.io/baodata2226/imagekit-assets/streamlit_2.png?updatedAt=1753199318195)
![Visualization](https://ik.imagekit.io/baodata2226/imagekit-assets/streamlit_3.png?updatedAt=1753199318183)


## File Descriptions

- **main.py**  
  - Main Streamlit app for data visualization and analytics.
  - Connects directly to the PostgreSQL database using SQLAlchemy.
  - Uses pandas and plotly for data processing and visualization.

## Features

- **Key Metrics**:  
  - Total customers, transactions, average transaction value, fraud detection rate
  - Transaction success rate, average daily transactions
  - Total bank accounts, devices, trusted devices, new customers, average accounts per customer
  - Authentication logs, risk alerts, failed authentications, high-security transactions

- **Visualizations**:  
  - Time-series charts for transaction volume
  - Bar charts for customer type distribution
  - Pie/donut charts for risk alert categories
  - Data tables for risky transactions, unverified devices, and more

- **Filtering**:  
  - Date range, customer segment, transaction type filters in the sidebar

- **Modern UI**:  
  - Custom CSS for a professional look
  - Responsive layout and interactive tabs

## Usage

- Start the dashboard with:  
  ```
  streamlit run visualization/main.py
  ```
- Access via [http://localhost:8501](http://localhost:8501)
- Ensure the database is populated and accessible. 