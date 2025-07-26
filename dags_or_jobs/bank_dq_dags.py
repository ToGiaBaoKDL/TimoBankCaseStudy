import logging
import os
import sys
import random
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from typing import Dict, Any

from dagster import (
    job,
    op,
    Config,
    get_dagster_logger,
    AssetMaterialization,
    MetadataValue,
    ScheduleDefinition,
    Definitions,
    DefaultScheduleStatus,
)

# Add src directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

# Import functions from src
from src.generate_data_timo import (
    populate_customers,
    populate_bank_accounts,
    populate_devices,
    populate_payment_transactions,
    populate_authentication_logs,
    Session
)
from src.data_quality_standards import DataQualityChecker
from src.monitoring_audit import RiskMonitor

# Setup logging
log_dir = os.path.join(project_root, 'logs')
os.makedirs(log_dir, exist_ok=True)


def setup_logger(name: str) -> logging.Logger:
    """Setup logger with file handler to write logs to a specific file."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Check if handler already exists to avoid duplicate handlers
    if not logger.handlers:
        handler = TimedRotatingFileHandler(
            os.path.join(log_dir, f'{name.lower()}.log'),
            when='midnight',
            interval=1,
            backupCount=7
        )
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


class DataGenerationConfig(Config):
    """Configuration for customer/account/device generation."""
    num_customers: int = random.randint(0, 80)
    num_accounts_per_customer: int = 2
    num_devices_per_customer: int = 2


class TransactionConfig(Config):
    """Configuration for transaction generation."""
    num_transactions: int = random.randint(150, 300)


# ===== JOB 1: CUSTOMER, ACCOUNT, DEVICE GENERATION =====

@op
def generate_customers_accounts_devices(context, config: DataGenerationConfig) -> Dict[str, Any]:
    """
    Generate customers, bank accounts, and devices.
    Logs the number of records generated for each entity.
    """
    dagster_logger = get_dagster_logger()
    file_logger = setup_logger('CustomerDataGeneration')

    dagster_logger.info("Initiating customer, account, and device data generation process.")
    file_logger.info("Initiating customer, account, and device data generation process.")
    session = Session()

    try:
        dagster_logger.info(f"Attempting to generate {config.num_customers} customers.")
        file_logger.info(f"Attempting to generate {config.num_customers} customers.")
        with session.begin():
            # Generate customers
            customers = populate_customers(session, num_customers=config.num_customers)
            dagster_logger.info(f"Successfully generated {len(customers)} customers.")
            file_logger.info(f"Successfully generated {len(customers)} customers.")

            # Generate bank accounts
            dagster_logger.info(
                f"Generating bank accounts for {len(customers)} customers, {config.num_accounts_per_customer} per customer.")
            file_logger.info(
                f"Generating bank accounts for {len(customers)} customers, {config.num_accounts_per_customer} per customer.")
            accounts = populate_bank_accounts(
                session, customers,
                num_accounts_per_customer=config.num_accounts_per_customer
            )
            dagster_logger.info(f"Generated {len(accounts)} bank accounts.")
            file_logger.info(f"Generated {len(accounts)} bank accounts.")

            # Generate devices
            dagster_logger.info(
                f"Generating devices for {len(customers)} customers, {config.num_devices_per_customer} per customer.")
            file_logger.info(
                f"Generating devices for {len(customers)} customers, {config.num_devices_per_customer} per customer.")
            devices = populate_devices(
                session, customers,
                num_devices_per_customer=config.num_devices_per_customer
            )
            dagster_logger.info(f"Generated {len(devices)} devices.")
            file_logger.info(f"Generated {len(devices)} devices.")

            session.commit()
            dagster_logger.info("Customer, account, and device data generation completed and committed successfully.")
            file_logger.info("Customer, account, and device data generation completed and committed successfully.")

            # Log materialization to Dagster UI
            context.log_event(
                AssetMaterialization(
                    asset_key="customers_accounts_devices",
                    metadata={
                        "num_customers": len(customers),
                        "num_accounts": len(accounts),
                        "num_devices": len(devices),
                        "generation_time": MetadataValue.timestamp(datetime.now().timestamp())
                    }
                )
            )

            return {
                'customers_count': len(customers),
                'accounts_count': len(accounts),
                'devices_count': len(devices),
                'timestamp': datetime.now().isoformat()
            }

    except Exception as e:
        dagster_logger.error(f"Customer, account, and device generation failed: {str(e)}")
        file_logger.error(f"Customer, account, and device generation failed: {str(e)}")
        session.rollback()  # Ensure rollback on error
        raise
    finally:
        session.close()
        file_logger.info("Database session closed for customer/account/device generation.")


@job
def customer_data_generation_job():
    """Job to generate customers, accounts, and devices."""
    generate_customers_accounts_devices()


# ===== JOB 2: TRANSACTION GENERATION =====

@op
def generate_payment_transactions(context, config: TransactionConfig) -> Dict[str, Any]:
    """
    Generate payment transactions and authentication logs.
    Logs the number of transactions and authentication logs generated.
    """
    dagster_logger = get_dagster_logger()
    file_logger = setup_logger('TransactionDataGeneration')

    dagster_logger.info("Initiating payment transaction and authentication log generation.")
    file_logger.info("Initiating payment transaction and authentication log generation.")
    session = Session()

    try:
        with session.begin():
            from src.models import BankAccount, Device
            accounts = [acc for acc in session.query(BankAccount).all()]  # Fetch as SQLAlchemy objects
            # devices = [dev for dev in session.query(Device).all()] # Not directly used here

            # Generate payment transactions
            dagster_logger.info(f"Attempting to generate {config.num_transactions} payment transactions.")
            file_logger.info(f"Attempting to generate {config.num_transactions} payment transactions.")
            transactions = populate_payment_transactions(
                session,
                num_transactions=config.num_transactions
            )
            dagster_logger.info(f"Successfully generated {len(transactions)} payment transactions.")
            file_logger.info(f"Successfully generated {len(transactions)} payment transactions.")

            # Generate authentication logs
            dagster_logger.info(f"Generating authentication logs for {len(transactions)} transactions.")
            file_logger.info(f"Generating authentication logs for {len(transactions)} transactions.")
            auth_logs = populate_authentication_logs(session, transactions, accounts)
            dagster_logger.info(f"Generated {len(auth_logs)} authentication logs.")
            file_logger.info(f"Generated {len(auth_logs)} authentication logs.")

            session.commit()
            dagster_logger.info(
                "Payment transaction and authentication log generation completed and committed successfully.")
            file_logger.info(
                "Payment transaction and authentication log generation completed and committed successfully.")

            context.log_event(
                AssetMaterialization(
                    asset_key="payment_transactions_auth_logs",
                    metadata={
                        "num_transactions": len(transactions),
                        "num_auth_logs": len(auth_logs),
                        "generation_time": MetadataValue.timestamp(datetime.now().timestamp())
                    }
                )
            )

            return {
                'transactions_count': len(transactions),
                'auth_logs_count': len(auth_logs),
                'timestamp': datetime.now().isoformat()
            }

    except Exception as e:
        dagster_logger.error(f"Payment transaction and authentication log generation failed: {str(e)}")
        file_logger.error(f"Payment transaction and authentication log generation failed: {str(e)}")
        session.rollback()  # Ensure rollback on error
        raise
    finally:
        session.close()
        file_logger.info("Database session closed for payment transaction generation.")


@job
def transaction_generation_job():
    """Job to generate payment transactions and authentication logs."""
    generate_payment_transactions()


# ===== JOB 3: DATA QUALITY CHECKS AND MONITORING =====

@op
def run_data_quality_checks(context) -> Dict[str, Any]:
    """
    Run data quality checks.
    Logs the start/end of checks and a summary of issues found.
    """
    dagster_logger = get_dagster_logger()
    file_logger = setup_logger('DataQualityChecks')

    dagster_logger.info("Initiating data quality checks.")
    file_logger.info("Initiating data quality checks.")

    try:
        checker = DataQualityChecker()
        checker.run_checks()
        issue_count = len(checker.issues)

        if issue_count > 0:
            dagster_logger.warning(f"Data quality checks completed with {issue_count} issues found.")
            file_logger.warning(f"Data quality checks completed with {issue_count} issues found.")

            for i, issue in enumerate(checker.issues):
                dagster_logger.debug(
                    f"Issue {i + 1}: {issue['description']} (Table: {issue['table']}, Record ID: {issue['record_id']})")
                file_logger.debug(
                    f"Issue {i + 1}: {issue['description']} (Table: {issue['table']}, Record ID: {issue['record_id']})")
        else:
            dagster_logger.info("Data quality checks completed successfully with no issues detected.")
            file_logger.info("Data quality checks completed successfully with no issues detected.")

        # Log materialization
        context.log_event(
            AssetMaterialization(
                asset_key="data_quality_check",
                metadata={
                    "issues_found": issue_count,
                    "check_time": MetadataValue.timestamp(datetime.now().timestamp()),
                    "status": "passed" if issue_count == 0 else "issues_found"
                }
            )
        )

        return {
            'issues_count': issue_count,
            'status': 'passed' if issue_count == 0 else 'issues_found',
            'timestamp': datetime.now().isoformat()
        }

    except Exception as e:
        dagster_logger.error(f"Data quality checks failed: {str(e)}")
        file_logger.error(f"Data quality checks failed: {str(e)}")
        raise
    finally:
        file_logger.info("Data quality checks operation finished.")


@op
def run_risk_monitoring(context) -> Dict[str, Any]:
    """
    Run risk monitoring checks.
    Logs the start/end of checks and a summary of issues found.
    """
    dagster_logger = get_dagster_logger()
    file_logger = setup_logger('RiskMonitoring')

    dagster_logger.info("Initiating risk monitoring checks.")
    file_logger.info("Initiating risk monitoring checks.")

    try:
        monitor = RiskMonitor()
        monitor.run_checks()
        issue_count = len(monitor.issues)

        if issue_count > 0:
            dagster_logger.warning(f"Risk monitoring checks completed with {issue_count} issues found.")
            file_logger.warning(f"Risk monitoring checks completed with {issue_count} issues found.")

            for i, issue in enumerate(monitor.issues):
                dagster_logger.debug(
                    f"Issue {i + 1}: {issue['description']} (Transaction ID: {issue['transaction_id']})")
                file_logger.debug(f"Issue {i + 1}: {issue['description']} (Transaction ID: {issue['transaction_id']})")
        else:
            dagster_logger.info("Risk monitoring checks completed successfully with no issues detected.")
            file_logger.info("Risk monitoring checks completed successfully with no issues detected.")

        # Log materialization
        context.log_event(
            AssetMaterialization(
                asset_key="risk_monitoring_check",
                metadata={
                    "issues_found": issue_count,
                    "check_time": MetadataValue.timestamp(datetime.now().timestamp()),
                    "status": "passed" if issue_count == 0 else "issues_found"
                }
            )
        )

        return {
            'issues_count': issue_count,
            'status': 'passed' if issue_count == 0 else 'issues_found',
            'timestamp': datetime.now().isoformat()
        }

    except Exception as e:
        dagster_logger.error(f"Risk monitoring failed: {str(e)}")
        file_logger.error(f"Risk monitoring failed: {str(e)}")
        raise
    finally:
        # RiskMonitor's __del__ method closes the session.
        file_logger.info("Risk monitoring operation finished.")


@job
def quality_and_monitoring_job():
    """Job to run data quality checks and risk monitoring."""
    quality_result = run_data_quality_checks()
    risk_result = run_risk_monitoring()


# ===== SCHEDULES =====

# Schedule 1: Customer data generation every 2 hours
customer_data_schedule = ScheduleDefinition(
    job=customer_data_generation_job,
    cron_schedule="* */2 * * *",  # Every 2 hours
    default_status=DefaultScheduleStatus.RUNNING
)

# Schedule 2: Transaction generation every 1 hour
transaction_data_schedule = ScheduleDefinition(
    job=transaction_generation_job,
    cron_schedule="* */1 * * *",  # Every 1 hour
    default_status=DefaultScheduleStatus.RUNNING
)

# Schedule 3: Quality checks and monitoring every 30 minutes
quality_monitoring_schedule = ScheduleDefinition(
    job=quality_and_monitoring_job,
    cron_schedule="*/30 * * * *",  # Every 30 minutes
    default_status=DefaultScheduleStatus.RUNNING
)

# Define all definitions for Dagster
defs = Definitions(
    jobs=[
        customer_data_generation_job,
        transaction_generation_job,
        quality_and_monitoring_job
    ],
    schedules=[
        customer_data_schedule,
        transaction_data_schedule,
        quality_monitoring_schedule
    ]
)
