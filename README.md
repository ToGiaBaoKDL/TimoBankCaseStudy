# Timo Digital Bank Case Study

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13%2B-blue?logo=postgresql)](https://www.postgresql.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red?logo=streamlit)](https://streamlit.io/)
[![Dagster](https://img.shields.io/badge/Dagster-Orchestration-purple?logo=dagster)](https://dagster.io/)

---

## 🔗 Live Demo

Explore the interactive dashboard here:  
👉 [https://tgb-timobankcasestudy.streamlit.app/](https://tgb-timobankcasestudy.streamlit.app/)

> ⚠️ *Note: The demo may take a few seconds to load as it connects to the remote PostgreSQL server.*

![Streamlit](https://ik.imagekit.io/baodata2226/imagekit-assets/streamlit_4.png?updatedAt=1753213886502)

---

## 🚀 Quick Start

> 📖 **For a step-by-step verification guide, see [QUICK_START.md](QUICK_START.md)**

### Prerequisites
- Python 3.10+
- PostgreSQL 13+
- psql CLI tool

### Installation & Setup

1. **Clone the project:**
   ```bash
   git clone https://github.com/ToGiaBaoKDL/TimoBankCaseStudy.git
   cd TimoBankCaseStudy
   ```

2. **Run the automated setup script:**
   ```bash
   # On Windows (PowerShell)
   .\setup.sh
   
   # On Linux/Mac
   chmod +x setup.sh
   ./setup.sh
   ```

3. **Manual setup (if needed):**
   ```bash
   # Install dependencies
   pip install -r requirements.txt
   
   # Create .env file with your database credentials
   # Edit .env file with your PostgreSQL connection details
   
   # Initialize database
   psql -U postgres -c "CREATE DATABASE postgres;" 2>/dev/null
   psql -U postgres -d postgres -f sql/schema.sql
   ```

### Running the Application

#### Option 1: Using the Setup Script (Recommended)
The setup script automatically starts both services:
```bash
./setup.sh
```

#### Option 2: Manual Startup
1. **Start Dagster UI:**
   ```bash
   dagster dev -f dags_or_jobs/bank_dq_dags.py
   ```

2. **Start Streamlit Dashboard (in a new terminal):**
   ```bash
   streamlit run visualization/main.py
   ```

### Access Points
- **Dagster UI**: [http://localhost:3000](http://localhost:3000)
- **Streamlit Dashboard**: [http://localhost:8501](http://localhost:8501)

### Using the Application
1. **Dagster UI**: Use to run or schedule pipelines (data generation, quality checks, monitoring)
2. **Streamlit Dashboard**: Interactive analytics and data visualization
3. **Database**: Direct access via psql or any PostgreSQL client

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
│   ├── bank_dq_dags.py         # Dagster jobs, ops, and schedules
│   └── README.md               # Dagster documentation
├── sql/
│   ├── schema.sql              # Database schema, triggers, and sample data
│   ├── reporting_queries.sql   # Analytical and operational reporting queries
│   └── README.md               # SQL schema and reporting documentation
├── src/
│   ├── data_quality_standards.py   # Data quality check scripts
│   ├── generate_data_timo.py       # Generate synthetic data for Timo
│   ├── generate_data_other_banks.py# Generate data for other banks
│   ├── models.py                  # ORM model definitions
│   ├── monitoring_audit.py        # Risk monitoring scripts
│   └── README.md                  # Source code documentation
├── visualization/
│   ├── main.py                    # Main Streamlit application
│   ├── config.py                  # Configuration settings
│   ├── database.py                # Database connection utilities
│   ├── queries.py                 # SQL queries for dashboard
│   ├── ui_components.py           # Reusable UI components
│   ├── styles.py                  # Custom CSS styling
│   ├── timo_logo.png              # Application logo
│   └── README.md                  # Dashboard documentation
├── notebook/
│   └── eda.ipynb                  # Exploratory Data Analysis notebook
├── logs/                          # Log files for audit and monitoring
├── report/
│   └── 25CDEI_ To Gia Bao.pdf     # Detailed project report
├── requirements.txt               # Python dependencies
├── setup.sh                       # One-command setup script
└── README.md                      # Project documentation
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

### Orchestration with Dagster
All data generation, quality checks, and monitoring are orchestrated via Dagster jobs defined in `dags_or_jobs/bank_dq_dags.py`. Use the Dagster UI to run or schedule these jobs.

**Available Jobs:**
- `customer_data_generation_job`: Generate customers, accounts, and devices
- `transaction_generation_job`: Generate payment transactions and authentication logs
- `quality_and_monitoring_job`: Run data quality checks and risk monitoring

![Dagster UI](https://ik.imagekit.io/baodata2226/imagekit-assets/dagster.png?updatedAt=1753199318227)

### Analytical Dashboard
The Streamlit dashboard (`visualization/main.py`) connects directly to the database and provides:

**Key Features:**
- **Overview Metrics**: Customer counts, transaction volumes, success rates, fraud detection
- **Interactive Visualizations**: Time series charts, customer segmentation, transaction analysis
- **Security & Risk Monitoring**: Alert tracking, authentication analysis, device trust status
- **Data Exploration**: Detailed tables with filtering by date, transaction type, customer segment
- **Modern UI**: Professional styling with responsive layout and interactive components

**Dashboard Tabs:**
1. **Overview**: Key performance indicators and summary statistics
2. **Transactions**: Transaction analysis and trends
3. **Security & Risk**: Risk alerts and security monitoring
4. **Customer Behavior**: Customer segmentation and behavior analysis
5. **Data Exploration**: Detailed data tables with advanced filtering

---

## 5. Configuration

### Environment Variables
Create a `.env` file in the project root:
```env
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

### Database Connection
The application uses SQLAlchemy with PostgreSQL. Ensure your database is running and accessible with the credentials specified in the `.env` file.

---

## 6. Troubleshooting

### Common Issues

1. **Database Connection Error:**
   - Verify PostgreSQL is running
   - Check `.env` file credentials
   - Ensure database exists: `psql -U postgres -c "CREATE DATABASE postgres;"`

2. **Port Already in Use:**
   - Dagster UI: Change port in Dagster configuration
   - Streamlit: Use `streamlit run visualization/main.py --server.port 8502`

3. **Missing Dependencies:**
   - Run `pip install -r requirements.txt`
   - Ensure Python 3.10+ is installed

4. **Permission Issues (Windows):**
   - Run PowerShell as Administrator
   - Use `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

### Logs
Check the `logs/` directory for detailed error logs:
- `customerdatageneration.log`
- `transactiondatageneration.log`
- `dataqualitychecks.log`
- `monitoring_audit.log`

---

## 7. Assumptions & Notes
- The schema is designed for the Vietnamese banking context, with realistic constraints and triggers for fraud/risk detection
- Generated data covers diverse and edge-case scenarios (large transactions, weak authentication, untrusted devices, etc.)
- All scripts and jobs use the same PostgreSQL connection string (configured via environment variable)
- Logs are saved in the `logs/` directory for audit and debugging
- The system is extensible: you can add more jobs, alerts, or dashboard features as needed

---

## 8. Additional Documentation

- **Detailed Report**: `report/25CDEI_ To Gia Bao.pdf` - Business requirements, regulatory context, and technical rationale
- **SQL Documentation**: `sql/README.md` - Schema and reporting query documentation
- **Dashboard Documentation**: `visualization/README.md` - Dashboard features and usage
- **Source Code Documentation**: `src/README.md` - Source code structure and functions