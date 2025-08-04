#!/bin/bash

echo "==== Timo Digital Bank Case Study: Auto Setup ===="

# 0. Create virtual environment if not exists
if [ ! -d ".venv" ]; then
  echo "[0/4] Creating virtual environment (.venv)..."
  python -m venv .venv
fi

# Activate virtual environment
echo "    Activating virtual environment..."
source .venv/Scripts/activate

# 1. Install Python dependencies
echo "[1/4] Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# 2. Create .env file if missing
if [ ! -f .env ]; then
  echo "[2/4] Creating .env file..."
  cat <<EOT > .env
DB_NAME=timo_digital_bank
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
EOT
  echo "  => Please edit .env to set your actual DB_PASSWORD if needed!"
else
  echo "[2/4] .env file already exists."
fi

# 3. Initialize database and schema
echo "[3/4] Initializing database and schema..."
source .env

# Export password so psql doesn't prompt
export PGPASSWORD=$DB_PASSWORD

# Create DB if not exists
psql -U "$DB_USER" -tc "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME'" | grep -q 1 || \
psql -U "$DB_USER" -c "CREATE DATABASE $DB_NAME;"

# Run schema
psql -U "$DB_USER" -d "$DB_NAME" -f sql/schema.sql

# 4. Start Dagster UI and Streamlit dashboard (in background)
echo "[4/4] Starting Dagster UI and Streamlit dashboard..."
dagster dev -f dags_or_jobs/bank_dq_dags.py > logs/dagster.log 2>&1 &
streamlit run visualization/main.py > logs/streamlit.log 2>&1 &

echo "==== DONE! ===="
echo "• Dagster UI:    http://localhost:3000"
echo "• Streamlit UI:  http://localhost:8501"
echo "=> Open Dagster UI to run pipelines (generate data, quality check, monitoring, etc.)"
