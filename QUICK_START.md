# Quick Start Guide - Timo Digital Bank Case Study

## 🚀 Fast Setup & Verification

### 1. Prerequisites Check
```bash
# Check Python version (should be 3.10+)
python --version

# Check if PostgreSQL is running
psql --version

# Check if psql CLI is available
which psql  # Linux/Mac
where psql  # Windows
```

### 2. One-Command Setup
```bash
# Clone and setup
git clone https://github.com/ToGiaBaoKDL/TimoBankCaseStudy.git
cd TimoBankCaseStudy

# Run automated setup
./setup.sh  # Linux/Mac
# OR
.\setup.sh  # Windows PowerShell
```

### 3. Verify Installation
After running setup.sh, check:

#### Database Connection
```bash
# Test database connection
psql -U postgres -d postgres -c "SELECT version();"
```

#### Dagster UI
- Open: http://localhost:3000
- Should show Dagster UI with available jobs
- Check if jobs are listed: `customer_data_generation_job`, `transaction_generation_job`, `quality_and_monitoring_job`

#### Streamlit Dashboard
- Open: http://localhost:8501
- Should show Timo Digital Bank Dashboard
- Check if dashboard loads without errors

### 4. Test Data Pipeline

#### Generate Sample Data
1. Go to Dagster UI: http://localhost:3000
2. Click on `customer_data_generation_job`
3. Click "Launch Run" with default config
4. Wait for completion (should take 30-60 seconds)
5. Check logs in `logs/customerdatageneration.log`

#### Generate Transactions
1. In Dagster UI, click on `transaction_generation_job`
2. Click "Launch Run" with default config
3. Wait for completion
4. Check logs in `logs/transactiondatageneration.log`

#### Run Quality Checks
1. In Dagster UI, click on `quality_and_monitoring_job`
2. Click "Launch Run"
3. Check logs in `logs/dataqualitychecks.log` and `logs/monitoring_audit.log`

### 5. Verify Dashboard Data
1. Go to Streamlit Dashboard: http://localhost:8501
2. Check if metrics show data (not zeros)
3. Try different filters in sidebar
4. Navigate through different tabs

### 6. Troubleshooting

#### Common Issues

**Database Connection Failed:**
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql  # Linux
brew services list | grep postgresql  # Mac
# On Windows, check Services app

# Test connection manually
psql -U postgres -h localhost -p 5432
```

**Port Already in Use:**
```bash
# Check what's using the ports
lsof -i :3000  # Dagster port
lsof -i :8501  # Streamlit port

# Kill processes if needed
kill -9 <PID>
```

**Missing Dependencies:**
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Check specific package
python -c "import dagster; print('Dagster OK')"
python -c "import streamlit; print('Streamlit OK')"
```

**Permission Issues (Windows):**
```powershell
# Run PowerShell as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 7. Expected Results

After successful setup, you should see:

#### Dagster UI (http://localhost:3000)
- 3 jobs available
- Ability to launch runs
- Job execution logs

#### Streamlit Dashboard (http://localhost:8501)
- Professional banking dashboard
- Interactive filters
- Data visualizations
- Multiple tabs with different views

#### Database
- All tables created
- Sample data populated
- Triggers and constraints active

### 8. Next Steps

1. **Explore the Dashboard**: Try different filters and tabs
2. **Run More Jobs**: Generate more data or run quality checks
3. **Customize**: Modify configuration in `.env` file
4. **Extend**: Add new jobs or dashboard features

### 9. Support

If you encounter issues:
1. Check the `logs/` directory for error messages
2. Verify all prerequisites are installed
3. Ensure PostgreSQL is running and accessible
4. Check the main README.md for detailed documentation 