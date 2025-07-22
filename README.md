# Timo Digital Bank Case Study

## 1. Project Overview

Timo Digital Bank Case Study is a comprehensive simulation of a modern digital banking environment, designed to:
- Generate synthetic data for customers, accounts, devices, transactions (including interbank and e-wallet operations)
- Define and automatically check data quality standards
- Monitor risks, detect fraud, and trigger security alerts
- Visualize data and provide analytical dashboards
- Automate the data pipeline using Dagster (orchestration, scheduling)

This project is suitable for banking analytics, fraud detection system testing, and demonstrating modern data management capabilities.

---

## 2. Project Structure

```
TimoBankCaseStudy/
├── dags_or_jobs/
│   └── bank_dq_dags.py         # Dagster jobs, ops, and schedules
├── sql/
│   └── schema.sql              # Database schema, triggers, and sample data
├── src/
│   ├── data_quality_standards.py   # Data quality check scripts
│   ├── generate_data_timo.py       # Generate synthetic data for Timo
│   ├── generate_data_other_banks.py# Generate data for other banks
│   ├── models.py                  # ORM model definitions
│   └── monitoring_audit.py        # Risk monitoring scripts
├── visualization/
│   └── dashboard.py            # Streamlit dashboard
├── logs/                       # Log files for audit and monitoring
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation
```

---

## 3. Database Schema

![Database Schema](https://ik.imagekit.io/baodata2226/imagekit-assets/database_schema.png?updatedAt=1753199318256)


The system uses PostgreSQL with the following main tables:

### 3.1. Main Tables
- **customers**: Customer information (individual/organization), national ID, tax code, status, address, etc.
- **bank_accounts**: Customer bank accounts, account type (savings/checking/ewallet), balance, status
- **devices**: Customer devices, device type, OS, trust status
- **authentication_methods**: Authentication methods (OTP, biometric, digital signature, etc.), security level (A/B/C/D)
- **payment_transactions**: Payment transactions, transfers, e-wallet operations, etc.
- **authentication_logs**: Authentication logs for each transaction, result, failure reason
- **risk_alerts**: Risk alerts (high-value transactions, untrusted devices, weak authentication, etc.)
- **banks, other_banks_customers, other_banks_accounts**: Simulated data for other banks, supporting interbank transactions
- **daily_transaction_summaries**: Daily transaction summaries, used for limit control and anomaly detection

### 3.2. Relationships and Constraints
- **Foreign Keys**: bank_accounts, devices, payment_transactions, etc. are tightly linked to customers
- **CHECK Constraints**: Ensure valid formats for national ID, phone number, account type, status, etc.
- **Triggers & Functions**:
  - **classify_transaction**: Automatically classifies transaction security level according to SBV regulations (2345/QĐ-NHNN)
  - **update_daily_summary**: Automatically updates daily transaction summaries and generates risk alerts (high-value, weak authentication, etc.)
- **Indexes**: Optimize queries for foreign keys, transaction date, status, etc.

### 3.3. Table Purposes
- **customers**: Central customer data, distinguishes individuals/organizations, supports authentication scenarios
- **bank_accounts**: Each customer can have multiple accounts, supporting various transaction types
- **devices**: Simulates multi-device usage, tests device security scenarios
- **payment_transactions**: Records all transactions, supports analytics and fraud detection
- **risk_alerts**: Automatically generated alerts for anomalies, supports alert system testing

---

## 4. Pipeline & Components (Details)

### 4.1. Data Generation Scripts
- `src/generate_data_timo.py`: Generates customers, accounts, devices, transactions, and authentication logs for Timo
- `src/generate_data_other_banks.py`: Generates customers and accounts for other banks (for interbank scenarios)
- Generated data strictly follows schema constraints and covers diverse scenarios (large transactions, untrusted devices, etc.)

### 4.2. Data Quality & Risk Monitoring
- `src/data_quality_standards.py`: Checks for nulls, duplicates, format, foreign keys, etc.
- `src/monitoring_audit.py`: Checks for high-value transactions without strong authentication, transactions from untrusted devices, daily limit breaches, etc.
- Detailed logs are saved in the `logs/` directory

### 4.3. Orchestration with Dagster
- `dags_or_jobs/bank_dq_dags.py`: Defines jobs for:
  - Generating customers/accounts/devices
  - Generating transactions and authentication logs
  - Running data quality checks
  - Running risk monitoring
- Defines automatic schedules (every 6h, 3h, 12h)
- Jobs can be run manually or scheduled via Dagster UI

### 4.4. Analytical Dashboard
- `visualization/dashboard.py`: Streamlit dashboard, connects directly to the database, displays:
  - Customer, transaction, device, and risk alert overviews
  - Time series charts, customer segmentation, transaction types, alert categories
  - Detailed data tables, filterable by date, transaction type, customer segment

---

## 5. Setup & Usage (Details)

### 5.1. Environment Setup
- Requirements: Python 3.10+, PostgreSQL
- Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```
- Create a `.env` file or export the environment variable:
  ```
  DATABASE_URL=postgresql://<user>:<password>@<host>:<port>/timo_digital_bank
  ```

### 5.2. Database Initialization
- Create the database and schema:
  ```bash
  psql -U <user> -d <database> -f sql/schema.sql
  ```
- Ensure all tables, triggers, and sample data (banks, authentication methods) are created

### 5.3. Data Generation & Quality Checks (Manual)
- Generate Timo data:
  ```bash
  python src/generate_data_timo.py
  ```
- Generate other banks data:
  ```bash
  python src/generate_data_other_banks.py
  ```
- Run data quality checks:
  ```bash
  python src/data_quality_standards.py
  ```
- Run risk monitoring:
  ```bash
  python src/monitoring_audit.py
  ```

### 5.4. Orchestration with Dagster

![Dagster UI](https://ik.imagekit.io/baodata2226/imagekit-assets/dagster.png?updatedAt=1753199318227)

- Start Dagster UI:
  ```bash
  dagster dev -f dags_or_jobs/bank_dq_dags.py
  ```
- Access the UI at [http://localhost:3000](http://localhost:3000)
- Jobs can be run or scheduled directly from the UI

### 5.5. Analytical Dashboard
- Start the dashboard:
  ```bash
  streamlit run visualization/dashboard.py
  ```
- Access the dashboard at [http://localhost:8501](http://localhost:8501)
- The dashboard automatically connects to the database and displays the latest data

---

## 6. Assumptions & Notes
- The schema is designed for the Vietnamese banking context, with realistic constraints and triggers for fraud/risk detection
- Generated data covers diverse and edge-case scenarios (large transactions, weak authentication, untrusted devices, etc.)
- All scripts and jobs use the same PostgreSQL connection string (configured via environment variable)
- Logs are saved in the `logs/` directory for audit and debugging
- The system is extensible: you can add more jobs, alerts, or dashboard features as needed

---

## 7. Contact
For questions or contributions, please contact the project maintainer. 