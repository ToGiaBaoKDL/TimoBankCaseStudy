#!/bin/bash

echo "==== Timo Digital Bank Case Study: Auto Setup ===="

# 0. Create virtual environment if not exists
if [ ! -d ".venv" ]; then
  echo "[0/5] Creating virtual environment (.venv)..."
  python -m venv .venv
fi

# Activate virtual environment
echo "    Activating virtual environment..."
source .venv/Scripts/activate

# 1. Install Python dependencies
echo "[1/5] Installing Python dependencies..."
pip install -r requirements.txt

# 2. Prompt for DB configuration and write to .env
if [ ! -f .env ]; then
  echo "[2/5] Please enter your database configuration:"

  read -p "  ➤ Database name [default: timo_digital_bank]: " DB_NAME
  DB_NAME=${DB_NAME:-timo_digital_bank}

  read -p "  ➤ DB user [default: postgres]: " DB_USER
  DB_USER=${DB_USER:-postgres}

  read -s -p "  ➤ DB password: " DB_PASSWORD
  echo ""

  read -p "  ➤ DB host [default: localhost]: " DB_HOST
  DB_HOST=${DB_HOST:-localhost}

  read -p "  ➤ DB port [default: 5432]: " DB_PORT
  DB_PORT=${DB_PORT:-5432}

  cat <<EOT > .env
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD
DB_HOST=$DB_HOST
DB_PORT=$DB_PORT
EOT

  echo "  => .env file created."
else
  echo "[2/5] .env file already exists. Skipping DB config input."
fi

# 3. Initialize database and schema
echo "[3/5] Initializing database and schema..."
source .env

# Export password so psql doesn't prompt
export PGPASSWORD=$DB_PASSWORD

# Create DB if not exists
psql -U "$DB_USER" -h "$DB_HOST" -p "$DB_PORT" -tc "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME'" | grep -q 1 || \
psql -U "$DB_USER" -h "$DB_HOST" -p "$DB_PORT" -c "CREATE DATABASE $DB_NAME;"

# Run schema
psql -U "$DB_USER" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -f sql/schema.sql

# 4. Start Dagster UI and Streamlit dashboard (in background)
echo "[4/5] Starting Dagster UI and Streamlit dashboard..."
mkdir -p logs
dagster dev -f dags_or_jobs/bank_dq_dags.py > logs/dagster.log 2>&1 &
streamlit run visualization/main.py > logs/streamlit.log 2>&1 &

echo "==== DONE! ===="
echo "• Dagster UI:    http://localhost:3000"
echo "• Streamlit UI:  http://localhost:8501"
echo "=> Open Dagster UI to run pipelines (generate data, quality check, monitoring, etc.)"
