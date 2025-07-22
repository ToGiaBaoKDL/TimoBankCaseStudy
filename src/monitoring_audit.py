import logging
import os
from logging.handlers import TimedRotatingFileHandler
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import sessionmaker
from models import (
    PaymentTransaction, AuthenticationLog,
    AuthenticationMethod, Device
)
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from typing import Optional


# Logging setup
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

log_file = os.path.join(LOG_DIR, 'monitoring_audit.log')

logger = logging.getLogger('DataQualityChecker')
logger.setLevel(logging.INFO)
handler = TimedRotatingFileHandler(
    log_file,
    when='midnight',
    interval=1,
    backupCount=7
)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Database connection setup
db_params = {
    'dbname': 'timo_digital_bank',
    'user': 'togiabao',
    'password': 'mysecretpassword',
    'host': '34.228.244.87',
    'port': '5432'
}
connection_string = f"postgresql://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['dbname']}"
engine = create_engine(connection_string)
Session = sessionmaker(bind=engine)
console = Console()


class RiskMonitor:
    def __init__(self):
        self.issues = []
        self.session = Session()
        logger.info("Initialized RiskMonitor")

    def log_issue(self, check_type: str, transaction_id: Optional[int], description: str):
        issue = {
            'timestamp': datetime.now(),
            'check_type': check_type,
            'transaction_id': transaction_id,
            'description': description
        }
        self.issues.append(issue)
        logger.warning(f"Risk issue - Type: {check_type}, Transaction ID: {transaction_id or 'N/A'}, Description: {description}")

    def check_strong_auth_for_high_value(self):
        """Check transactions > 10M VND have strong authentication"""
        logger.info("Starting strong authentication check for high-value transactions")
        try:
            transactions = self.session.execute(
                select(PaymentTransaction)
                .where(PaymentTransaction.amount > 10000000)
            ).scalars().all()

            strong_auth_methods = self.session.execute(
                select(AuthenticationMethod.auth_id)
                .where(AuthenticationMethod.security_level.in_(['C', 'D']))
            ).scalars().all()

            issues_found = 0
            for tx in transactions:
                has_strong_auth = self.session.execute(
                    select(func.count())
                    .select_from(AuthenticationLog)
                    .where(
                        (AuthenticationLog.transaction_id == tx.transaction_id) &
                        (AuthenticationLog.auth_method_id.in_(strong_auth_methods)) &
                        (AuthenticationLog.auth_result == 'success')
                    )
                ).scalar_one() > 0

                if not has_strong_auth:
                    self.log_issue(
                        "strong_auth_check",
                        tx.transaction_id,
                        f"High-value transaction {tx.transaction_id} (amount {tx.amount:,.2f} VND) exceeds 10M VND without strong authentication (C/D level)"
                    )
                    issues_found += 1
            logger.info(f"Found {issues_found} high-value transactions without strong authentication")
        except Exception as e:
            logger.error(f"Error in strong auth check: {str(e)}")
            raise

    def check_untrusted_device(self):
        """Check transactions from untrusted devices"""
        logger.info("Starting untrusted device check")
        try:
            transactions = self.session.execute(
                select(PaymentTransaction, Device)
                .join(Device, PaymentTransaction.device_id == Device.device_id)
                .where(Device.is_trusted == False)
            ).all()

            strong_auth_methods = self.session.execute(
                select(AuthenticationMethod.auth_id)
                .where(AuthenticationMethod.security_level.in_(['C', 'D']))
            ).scalars().all()

            issues_found = 0
            for tx, device in transactions:
                has_strong_auth = self.session.execute(
                    select(func.count())
                    .select_from(AuthenticationLog)
                    .where(
                        (AuthenticationLog.transaction_id == tx.transaction_id) &
                        (AuthenticationLog.auth_method_id.in_(strong_auth_methods)) &
                        (AuthenticationLog.auth_result == 'success')
                    )
                ).scalar_one() > 0

                if not has_strong_auth:
                    self.log_issue(
                        "untrusted_device_check",
                        tx.transaction_id,
                        f"Transaction {tx.transaction_id} on untrusted device {device.device_id} (amount {tx.amount:,.2f} VND) lacks strong authentication (C/D level)"
                    )
                    issues_found += 1
            logger.info(f"Found {issues_found} untrusted device transactions without strong authentication")
        except Exception as e:
            logger.error(f"Error in untrusted device check: {str(e)}")
            raise

    def check_daily_transaction_limit(self):
        """Check daily transaction total > 20M VND has strong authentication"""
        logger.info("Starting daily transaction limit check")
        try:
            one_day_ago = datetime.now() - timedelta(days=1)
            customer_totals = self.session.execute(
                select(
                    PaymentTransaction.customer_id,
                    func.sum(PaymentTransaction.amount).label('total_amount')
                )
                .where(PaymentTransaction.transaction_date >= one_day_ago)
                .group_by(PaymentTransaction.customer_id)
                .having(func.sum(PaymentTransaction.amount) > 20000000)
            ).all()

            strong_auth_methods = self.session.execute(
                select(AuthenticationMethod.auth_id)
                .where(AuthenticationMethod.security_level.in_(['C', 'D']))
            ).scalars().all()

            issues_found = 0
            for customer_id, total_amount in customer_totals:
                has_strong_auth = self.session.execute(
                    select(func.count())
                    .select_from(PaymentTransaction)
                    .join(AuthenticationLog, PaymentTransaction.transaction_id == AuthenticationLog.transaction_id)
                    .where(
                        (PaymentTransaction.customer_id == customer_id) &
                        (PaymentTransaction.transaction_date >= one_day_ago) &
                        (AuthenticationLog.auth_method_id.in_(strong_auth_methods)) &
                        (AuthenticationLog.auth_result == 'success')
                    )
                ).scalar_one() > 0

                if not has_strong_auth:
                    self.log_issue(
                        "daily_limit_check",
                        None,
                        f"Customer {customer_id} has daily transaction total of {total_amount:,.2f} VND exceeding 20M VND without any strong authentication (C/D level)"
                    )
                    issues_found += 1
            logger.info(f"Found {issues_found} customers with daily totals > 20M VND without strong authentication")
        except Exception as e:
            logger.error(f"Error in daily transaction limit check: {str(e)}")
            raise

    def generate_summary(self) -> Table:
        """Generate summary table of risk issues"""
        logger.info("Generating summary table")
        table = Table(title="Risk Monitoring Audit Summary")
        table.add_column("Timestamp", style="cyan")
        table.add_column("Check Type", style="magenta")
        table.add_column("Transaction ID", style="green")
        table.add_column("Description", style="yellow")

        for issue in self.issues:
            table.add_row(
                issue['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                issue['check_type'],
                str(issue['transaction_id']) if issue['transaction_id'] is not None else "N/A",
                issue['description']
            )
        logger.info(f"Summary table generated with {len(self.issues)} issues")
        return table

    def run_checks(self):
        """Run all risk monitoring checks"""
        logger.info("Starting all risk monitoring checks")
        console.print("[bold green]Starting Risk Monitoring Checks...[/bold green]")
        try:
            self.check_strong_auth_for_high_value()
            self.check_untrusted_device()
            self.check_daily_transaction_limit()
            console.print("[bold green]Risk Monitoring Checks Completed[/bold green]")
            console.print(self.generate_summary())
            logger.info("All risk monitoring checks completed successfully")
        except Exception as e:
            logger.error(f"Failed to complete risk monitoring checks: {str(e)}")
            console.print(f"[bold red]Error during checks: {str(e)}[/bold red]")
            raise

    def __del__(self):
        logger.info("Closing database session")
        self.session.close()


def main():
    logger.info("Starting risk monitoring script")
    try:
        monitor = RiskMonitor()
        monitor.run_checks()
        logger.info("Risk monitoring script completed")
    except Exception as e:
        logger.error(f"Script failed: {str(e)}")
        console.print(f"[bold red]Script failed: {str(e)}[/bold red]")


if __name__ == "__main__":
    main()
