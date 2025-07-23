# Timo Digital Bank Case Study

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13%2B-blue?logo=postgresql)](https://www.postgresql.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red?logo=streamlit)](https://streamlit.io/)
[![Dagster](https://img.shields.io/badge/Dagster-Orchestration-purple?logo=dagster)](https://dagster.io/)

---

## 🚀 Quick Start

1. Clone the project and run the setup script:
   ```bash
   git clone https://github.com/ToGiaBaoKDL/TimoBankCaseStudy.git
   cd TimoBankCaseStudy
   chmod +x setup.sh
   ./setup.sh
   ```
2. Access:
   - Dagster UI: [http://localhost:3000](http://localhost:3000)
   - Streamlit dashboard: [http://localhost:8501](http://localhost:8501)
3. Use the Dagster UI to run or schedule pipelines (data generation, quality checks, monitoring, etc.).
4. If needed, edit the `.env` file for your PostgreSQL connection and re-run the setup script.

> Requirements: Python 3.10+, PostgreSQL, and psql CLI must be installed.

---

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
│   ├── schema.sql              # Database schema, triggers, and sample data
│   ├── reporting_queries.sql   # Analytical and operational reporting queries
│   └── README.md               # SQL schema and reporting documentation
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
├── setup.sh                    # One-command setup script
└── README.md                   # Project documentation
```

---

## 3. Database Schema

![Database Schema](https://ik.imagekit.io/baodata2226/imagekit-assets/database_schema.png?updatedAt=1753199318256)

The system uses PostgreSQL with the following main tables:
- **customers**: Customer information (individual/organization), national ID, tax code, status, address, etc.
- **bank_accounts**: Customer bank accounts, account type (savings/checking/ewallet), balance, status
- **devices**: Customer devices, device type, OS, trust status
- **authentication_methods**: Authentication methods (OTP, biometric, digital signature, etc.), security level (A/B/C/D)
- **payment_transactions**: Payment transactions, transfers, e-wallet operations, etc.
- **authentication_logs**: Authentication logs for each transaction, result, failure reason
- **risk_alerts**: Risk alerts (high-value transactions, untrusted devices, weak authentication, etc.)
- **banks, other_banks_customers, other_banks_accounts**: Simulated data for other banks, supporting interbank transactions
- **daily_transaction_summaries**: Daily transaction summaries, used for limit control and anomaly detection

---

## 4. Pipeline & Components

- **Orchestration with Dagster**: All data generation, quality checks, and monitoring are orchestrated via Dagster jobs defined in `dags_or_jobs/bank_dq_dags.py`. Use the Dagster UI to run or schedule these jobs.

![Dagster UI](https://ik.imagekit.io/baodata2226/imagekit-assets/dagster.png?updatedAt=1753199318227)
- **Analytical Dashboard**: The Streamlit dashboard (`visualization/dashboard.py`) connects directly to the database and provides:
  - Customer, transaction, device, and risk alert overviews
  - Time series charts, customer segmentation, transaction types, alert categories
  - Detailed data tables, filterable by date, transaction type, customer segment

---

## 5. Assumptions & Notes
- The schema is designed for the Vietnamese banking context, with realistic constraints and triggers for fraud/risk detection
- Generated data covers diverse and edge-case scenarios (large transactions, weak authentication, untrusted devices, etc.)
- All scripts and jobs use the same PostgreSQL connection string (configured via environment variable)
- Logs are saved in the `logs/` directory for audit and debugging
- The system is extensible: you can add more jobs, alerts, or dashboard features as needed

---

## 6. Additional Documentation

- For a detailed explanation of the business requirements, regulatory context, and technical rationale behind the schema design, please refer to the report:
  - `report/25CDEI_ To Gia Bao.pdf`
- See `sql/README.md` for schema and reporting query documentation.

## 7. Contact
For questions or contributions, please contact the project maintainer. 