## Overview

The `sql` directory contains the full database schema and initialization logic for the Timo Digital Bank Case Study. This schema is designed for a realistic digital banking environment, with strong constraints, triggers, and sample data.

## File Descriptions

- **schema.sql**  
  - Creates the `timo_digital_bank` database and all required tables.
  - Defines all business entities: customers, accounts, devices, authentication methods, transactions, logs, risk alerts, and interbank entities.
  - Enforces strict constraints (unique, check, foreign key) for data integrity.
  - Implements advanced triggers and functions for:
    - Automatic transaction classification (per SBV 2345/QĐ-NHNN)
    - Daily transaction summary and risk alerting
    - Enforcement of authentication and risk policies
  - Populates sample data for banks and authentication methods.

## Schema Highlights

- **Tables**:
  - `customers`: Individual/organization, CCCD, tax code, phone, status, etc.
  - `bank_accounts`: Linked to customers, with account type, balance, status.
  - `devices`: Linked to customers, with device type, OS, trust status.
  - `authentication_methods`: All supported authentication types, with security level.
  - `payment_transactions`: All transactions, with type, amount, status, device, etc.
  - `authentication_logs`: Per-transaction authentication attempts and results.
  - `risk_alerts`: All risk alerts, with type, message, status.
  - `banks`, `other_banks_customers`, `other_banks_accounts`: For interbank simulation.
  - `daily_transaction_summaries`: Aggregated daily stats for each account.

- **Constraints**:
  - Uniqueness and format checks for IDs, phone, account numbers.
  - Foreign keys for all relationships.
  - Business logic enforced via CHECK constraints.

- **Triggers & Functions**:
  - `classify_transaction`: Classifies transaction security level based on type, amount, and customer type.
  - `update_daily_summary`: Updates daily summaries, checks for risk patterns, and inserts alerts.
  - Triggers for both transaction classification and summary update.

- **Sample Data**:
  - Inserts for major Vietnamese and international banks.
  - Inserts for all authentication methods (SMS OTP, biometric, digital signature, etc.).

## Usage

- To initialize the database, run:
  ```
  psql -U <user> -d <database> -f sql/schema.sql
  ```
- Ensure the database user has privileges to create tables, triggers, and functions.
- The schema is designed to be robust for both simulation and analytics. 

## Additional Documentation

- For a detailed explanation of the business requirements, regulatory context, and technical rationale behind the schema design, please refer to the report:
  - `report/25CDEI_ To Gia Bao.pdf`
- This document provides background on Vietnamese banking regulations, data quality standards, and risk monitoring logic implemented in the schema and triggers. 

## Reporting Queries

The `reporting_queries.sql` file contains a comprehensive suite of analytical and operational SQL queries designed for reporting, monitoring, and business intelligence on the Timo Digital Bank schema. These queries can be run directly in your SQL client or integrated into dashboards and analytics tools.

### Query Overview

1. **Customer Overview Report**
   - Summarizes customer details, their accounts, and registered devices. Useful for customer profiling and segmentation.

2. **Transaction Summary Report**
   - Aggregates transactions by customer and date, breaking down by security level and status. Supports trend analysis and compliance checks.

3. **Risk Alerts Analysis**
   - Provides detailed analysis of risk alerts, including type, status, and related transaction/authentication details. Useful for risk and fraud monitoring.

4. **Authentication Failure Report**
   - Lists authentication failures, reasons, and associated transaction/device details. Helps identify security issues and user friction points.

5. **High-Value Transaction Report**
   - Identifies transactions exceeding regulatory or business thresholds, categorized by customer type and transaction type. Supports anti-money laundering (AML) and risk review.

6. **Daily Transaction Limit Monitoring**
   - Monitors daily transaction totals against regulatory/customer limits, highlighting breaches and strong authentication usage.

7. **Device Usage Report**
   - Summarizes device usage patterns, trust status, and transaction activity. Useful for device risk assessment and customer behavior analysis.

8. **Interbank Transaction Analysis**
   - Analyzes transactions involving other banks, including domestic and international flows. Supports interbank settlement and compliance.

9. **Authentication Method Usage Report**
   - Shows usage and success rates for each authentication method, helping evaluate security effectiveness and user experience.

10. **Account Activity Report**
    - Summarizes account balances, transaction volumes, and recent activity. Useful for account monitoring and operational reporting.

### Usage
- To run a specific report, copy the relevant query from `reporting_queries.sql` and execute it in your SQL client connected to the Timo Digital Bank database.
- These queries are designed to work with the schema as defined in `schema.sql` and assume recent data generated by the project scripts.
- You can adapt or extend these queries for custom reporting, dashboarding, or integration with BI tools. 
