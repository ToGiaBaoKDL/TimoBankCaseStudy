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
