import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database connection parameters
DB_PARAMS = {
    'dbname': os.getenv("DB_NAME", "postgres"),
    'user': os.getenv("DB_USER", "postgres"),
    'password': os.getenv("DB_PASSWORD", "yourpassword"), # IMPORTANT: Use strong passwords and handle securely
    'host': os.getenv("DB_HOST", "localhost"),
    'port': '5432'
}

# Construct connection string
CONNECTION_STRING = (
    f"postgresql://{DB_PARAMS['user']}:{DB_PARAMS['password']}@{DB_PARAMS['host']}:"
    f"{DB_PARAMS['port']}/{DB_PARAMS['dbname']}"
)

# Default filter options (derived from schema.sql CHECK constraints)
DEFAULT_CUSTOMER_SEGMENTS = ["individual", "organization"]
ALL_TRANSACTION_TYPES = [
    "transfer_same_bank_same_owner", "transfer_same_bank_diff_owner",
    "transfer_interbank_domestic", "transfer_interbank_international",
    "payment_goods_services", "ewallet_topup", "ewallet_withdrawal",
    "inquiry", "ewallet_transfer"
]
ALL_TRANSACTION_STATUSES = ["completed", "failed", "pending", "cancelled"]
ALL_AUTH_RESULTS = ["success", "failed", "expired", "cancelled"]
ALL_SECURITY_LEVELS = ["A", "B", "C", "D"]
ALL_ALERT_STATUSES = ["open", "investigating", "resolved", "false_positive"]

# Convert lists to tuples for SQL `IN` clause (PostgreSQL expects tuples for `ANY`)
DEFAULT_CUSTOMER_SEGMENTS_TUPLE = tuple(DEFAULT_CUSTOMER_SEGMENTS)
ALL_TRANSACTION_TYPES_TUPLE = tuple(ALL_TRANSACTION_TYPES)
ALL_TRANSACTION_STATUSES_TUPLE = tuple(ALL_TRANSACTION_STATUSES)
ALL_AUTH_RESULTS_TUPLE = tuple(ALL_AUTH_RESULTS)
ALL_SECURITY_LEVELS_TUPLE = tuple(ALL_SECURITY_LEVELS)
ALL_ALERT_STATUSES_TUPLE = tuple(ALL_ALERT_STATUSES)

# Path to logo image
LOGO_PATH = "visualization/timo_logo.png"
