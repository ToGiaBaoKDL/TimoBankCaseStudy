import logging
import os
from logging.handlers import TimedRotatingFileHandler
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import sessionmaker
from models import (
    Customer, BankAccount, Device, PaymentTransaction
)
import re
from datetime import datetime
from rich.console import Console
from rich.table import Table
from dotenv import load_dotenv


# Load environment variables
load_dotenv()


# Logging setup
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

log_file = os.path.join(LOG_DIR, 'data_quality_standards.log')

logger = logging.getLogger('DataQualityChecker')
logger.setLevel(logging.INFO)
handler = TimedRotatingFileHandler(
    log_file,
    when='midnight',
    interval=1,
    backupCount=7,
    delay=True
)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Database connection setup
db_params = {
    'dbname': os.getenv("DB_NAME", "postgres"),
    'user': os.getenv("DB_USER", "postgres"),
    'password': os.getenv("DB_PASSWORD", "yourpassword"),
    'host': os.getenv("DB_HOST", "localhost"),
    'port': '5432'
}
connection_string = f"postgresql://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['dbname']}"
engine = create_engine(connection_string)
Session = sessionmaker(bind=engine)
console = Console()


class DataQualityChecker:
    def __init__(self):
        self.issues = []
        self.session = Session()
        logger.info("Initialized DataQualityChecker")

    def log_issue(self, check_type: str, table: str, description: str, record_id: str = ''):
        issue = {
            'timestamp': datetime.now(),
            'check_type': check_type,
            'table': table,
            'description': description,
            'record_id': record_id
        }
        self.issues.append(issue)
        logger.warning(
            f"Data quality issue - Type: {check_type}, Table: {table}, ID: {record_id or 'N/A'}, Description: {description}")

    def check_null_values(self):
        """Check for null values in critical fields"""
        logger.info("Starting null values check")
        try:
            # Customer checks
            customer_nulls = self.session.execute(
                select(Customer).where(
                    (Customer.customer_id.is_(None)) |
                    (Customer.customer_type.is_(None)) |
                    (Customer.tax_code.is_(None)) |
                    (Customer.full_name.is_(None)) |
                    (Customer.phone_number.is_(None)) |
                    (Customer.status.is_(None))
                )
            ).scalars().all()
            for customer in customer_nulls:
                self.log_issue("null_check", "customers",
                               f"Null values in critical fields for customer_id: {customer.customer_id}",
                               str(customer.customer_id))
            logger.info(f"Found {len(customer_nulls)} null issues in customers table")

            # BankAccount checks
            account_nulls = self.session.execute(
                select(BankAccount).where(
                    (BankAccount.account_id.is_(None)) |
                    (BankAccount.customer_id.is_(None)) |
                    (BankAccount.account_number.is_(None)) |
                    (BankAccount.account_type.is_(None)) |
                    (BankAccount.status.is_(None))
                )
            ).scalars().all()
            for account in account_nulls:
                self.log_issue("null_check", "bank_accounts",
                               f"Null values in critical fields for account_id: {account.account_id}",
                               str(account.account_id))
            logger.info(f"Found {len(account_nulls)} null issues in bank_accounts table")

            # Device checks
            device_nulls = self.session.execute(
                select(Device).where(
                    (Device.device_id.is_(None)) |
                    (Device.customer_id.is_(None)) |
                    (Device.device_type.is_(None)) |
                    (Device.device_identifier.is_(None)) |
                    (Device.status.is_(None))
                )
            ).scalars().all()
            for device in device_nulls:
                self.log_issue("null_check", "devices",
                               f"Null values in critical fields for device_id: {device.device_id}",
                               str(device.device_id))
            logger.info(f"Found {len(device_nulls)} null issues in devices table")
        except Exception as e:
            logger.error(f"Error in null values check: {str(e)}")
            raise

    def check_uniqueness(self):
        """Check uniqueness constraints"""
        logger.info("Starting uniqueness check")
        try:
            # CCCD uniqueness (for individuals)
            cccd_counts = self.session.execute(
                select(Customer.cccd_number, func.count())
                .where(Customer.cccd_number.is_not(None))
                .group_by(Customer.cccd_number)
                .having(func.count() > 1)
            ).all()
            for cccd, count in cccd_counts:
                self.log_issue("uniqueness_check", "customers",
                               f"Duplicate CCCD number: {cccd} (count: {count})", cccd)
            logger.info(f"Found {len(cccd_counts)} CCCD uniqueness issues")

            # Tax code uniqueness
            tax_counts = self.session.execute(
                select(Customer.tax_code, func.count())
                .group_by(Customer.tax_code)
                .having(func.count() > 1)
            ).all()
            for tax_code, count in tax_counts:
                self.log_issue("uniqueness_check", "customers",
                               f"Duplicate tax code: {tax_code} (count: {count})", tax_code)
            logger.info(f"Found {len(tax_counts)} tax code uniqueness issues")

            # Phone number uniqueness
            phone_counts = self.session.execute(
                select(Customer.phone_number, func.count())
                .group_by(Customer.phone_number)
                .having(func.count() > 1)
            ).all()
            for phone, count in phone_counts:
                self.log_issue("uniqueness_check", "customers",
                               f"Duplicate phone number: {phone} (count: {count})", phone)
            logger.info(f"Found {len(phone_counts)} phone number uniqueness issues")

            # Account number uniqueness
            account_counts = self.session.execute(
                select(BankAccount.account_number, func.count())
                .group_by(BankAccount.account_number)
                .having(func.count() > 1)
            ).all()
            for account_num, count in account_counts:
                self.log_issue("uniqueness_check", "bank_accounts",
                               f"Duplicate account number: {account_num} (count: {count})", account_num)
            logger.info(f"Found {len(account_counts)} account number uniqueness issues")
        except Exception as e:
            logger.error(f"Error in uniqueness check: {str(e)}")
            raise

    def check_cccd_format(self):
        """Validate CCCD format (12 digits)"""
        logger.info("Starting CCCD format check")
        try:
            cccd_pattern = re.compile(r'^\d{12}$')
            customers = self.session.execute(
                select(Customer).where(Customer.cccd_number.is_not(None))
            ).scalars().all()
            invalid_cccds = 0
            for customer in customers:
                if not cccd_pattern.match(customer.cccd_number):
                    self.log_issue("format_check", "customers",
                                   f"Invalid CCCD format for customer_id: {customer.customer_id} (CCCD: {customer.cccd_number})",
                                   str(customer.customer_id))
                    invalid_cccds += 1
            logger.info(f"Found {invalid_cccds} invalid CCCD formats")
        except Exception as e:
            logger.error(f"Error in CCCD format check: {str(e)}")
            raise

    def check_foreign_key_integrity(self):
        """Check foreign key constraints"""
        logger.info("Starting foreign key integrity check")
        try:
            # BankAccount customer_id
            invalid_accounts = self.session.execute(
                select(BankAccount).where(
                    ~BankAccount.customer_id.in_(select(Customer.customer_id))
                )
            ).scalars().all()
            for account in invalid_accounts:
                self.log_issue("foreign_key_check", "bank_accounts",
                               f"Invalid customer_id: {account.customer_id} for account_id: {account.account_id}",
                               str(account.account_id))
            logger.info(f"Found {len(invalid_accounts)} invalid foreign keys in bank_accounts")

            # Device customer_id
            invalid_devices = self.session.execute(
                select(Device).where(
                    ~Device.customer_id.in_(select(Customer.customer_id))
                )
            ).scalars().all()
            for device in invalid_devices:
                self.log_issue("foreign_key_check", "devices",
                               f"Invalid customer_id: {device.customer_id} for device_id: {device.device_id}",
                               str(device.device_id))
            logger.info(f"Found {len(invalid_devices)} invalid foreign keys in devices")

            # PaymentTransaction checks
            invalid_transactions = self.session.execute(
                select(PaymentTransaction).where(
                    (~PaymentTransaction.from_account_id.in_(select(BankAccount.account_id))) |
                    (~PaymentTransaction.customer_id.in_(select(Customer.customer_id))) |
                    (~PaymentTransaction.device_id.in_(select(Device.device_id)))
                )
            ).scalars().all()
            for tx in invalid_transactions:
                self.log_issue("foreign_key_check", "payment_transactions",
                               f"Invalid foreign key in transaction_id: {tx.transaction_id}",
                               str(tx.transaction_id))
            logger.info(f"Found {len(invalid_transactions)} invalid foreign keys in payment_transactions")
        except Exception as e:
            logger.error(f"Error in foreign key check: {str(e)}")
            raise

    def generate_summary(self) -> Table:
        """Generate summary table of issues"""
        logger.info("Generating summary table")
        table = Table(title="Data Quality Check Summary")
        table.add_column("Timestamp", style="cyan")
        table.add_column("Check Type", style="magenta")
        table.add_column("Table", style="green")
        table.add_column("Description", style="yellow")
        table.add_column("Record ID", style="blue")

        for issue in self.issues:
            table.add_row(
                issue['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                issue['check_type'],
                issue['table'],
                issue['description'],
                issue['record_id'] or "N/A"
            )
        logger.info(f"Summary table generated with {len(self.issues)} issues")
        return table

    def run_checks(self):
        """Run all data quality checks"""
        logger.info("Starting all data quality checks")
        console.print("[bold green]Starting Data Quality Checks...[/bold green]")
        try:
            self.check_null_values()
            self.check_uniqueness()
            self.check_cccd_format()
            self.check_foreign_key_integrity()
            console.print("[bold green]Data Quality Checks Completed[/bold green]")
            console.print(self.generate_summary())
            logger.info("All data quality checks completed successfully")
        except Exception as e:
            logger.error(f"Failed to complete data quality checks: {str(e)}")
            console.print(f"[bold red]Error during checks: {str(e)}[/bold red]")
            raise

    def __del__(self):
        logger.info("Closing database session")
        self.session.close()


def main():
    logger.info("Starting data quality check script")
    try:
        checker = DataQualityChecker()
        checker.run_checks()
        logger.info("Data quality check script completed")
    except Exception as e:
        logger.error(f"Script failed: {str(e)}")
        console.print(f"[bold red]Script failed: {str(e)}[/bold red]")


if __name__ == "__main__":
    main()
