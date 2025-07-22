# dags_or_jobs Directory

## Overview

The `dags_or_jobs` directory contains Dagster job definitions for orchestrating the data pipeline of the Timo Digital Bank Case Study. This includes data generation, quality checks, and risk monitoring, all scheduled and managed via Dagster.

## File Descriptions

- **bank_dq_dags.py**  
  - Main Dagster pipeline definition file.
  - Imports all core logic from `src/`.
  - Defines jobs, ops, and schedules for the entire data pipeline.

## Pipeline Components

- **Ops**:
  - `generate_customers_accounts_devices`: Generates customers, accounts, and devices
  - `generate_payment_transactions`: Generates payment transactions and authentication logs
  - `run_data_quality_checks`: Runs all data quality checks
  - `run_risk_monitoring`: Runs all risk monitoring checks

- **Jobs**:
  - `customer_data_generation_job`: Runs customer/account/device generation
  - `transaction_generation_job`: Runs transaction and authentication log generation
  - `quality_and_monitoring_job`: Runs both data quality and risk monitoring checks

- **Schedules**:
  - `customer_data_schedule`: Runs customer data generation every 6 hours
  - `transaction_data_schedule`: Runs transaction generation every 3 hours
  - `quality_monitoring_schedule`: Runs quality and monitoring checks every 12 hours

- **Logging**:  
  Each job logs to a dedicated file in the `logs/` directory.

## Usage

- Start Dagster UI with:  
  ```
  dagster dev -f dags_or_jobs/bank_dq_dags.py
  ```
- Access the Dagster UI at [http://localhost:3000](http://localhost:3000)
- Jobs can be triggered manually or run on schedule. 