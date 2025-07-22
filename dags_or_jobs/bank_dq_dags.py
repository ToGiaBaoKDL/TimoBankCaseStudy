import logging
import os
import sys
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
    """Setup logger with file handler"""
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
    """Configuration for customer/account/device generation"""
    num_customers: int = 50
    num_accounts_per_customer: int = 2
    num_devices_per_customer: int = 2


class TransactionConfig(Config):
    """Configuration for transaction generation"""
    num_transactions: int = 150


# ===== JOB 1: CUSTOMER, ACCOUNT, DEVICE GENERATION =====

@op
def generate_customers_accounts_devices(context, config: DataGenerationConfig) -> Dict[str, Any]:
    """Generate customers, bank accounts, and devices"""
    logger = get_dagster_logger()
    file_logger = setup_logger('CustomerDataGeneration')

    logger.info("Starting customer, account, and device generation")
    file_logger.info("Starting customer, account, and device generation")

    try:
        session = Session()
        with session.begin():
            # Generate customers
            customers = populate_customers(session, num_customers=config.num_customers)
            logger.info(f"Generated {len(customers)} customers")
            file_logger.info(f"Generated {len(customers)} customers")

            # Generate bank accounts
            accounts = populate_bank_accounts(
                session, customers,
                num_accounts_per_customer=config.num_accounts_per_customer
            )
            logger.info(f"Generated {len(accounts)} bank accounts")
            file_logger.info(f"Generated {len(accounts)} bank accounts")

            # Generate devices
            devices = populate_devices(
                session, customers,
                num_devices_per_customer=config.num_devices_per_customer
            )
            logger.info(f"Generated {len(devices)} devices")
            file_logger.info(f"Generated {len(devices)} devices")

            session.commit()
            logger.info("Customer, account, and device generation completed successfully")
            file_logger.info("Customer, account, and device generation completed successfully")

            # Log materialization
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
        logger.error(f"Customer, account, and device generation failed: {str(e)}")
        file_logger.error(f"Customer, account, and device generation failed: {str(e)}")
        raise
    finally:
        session.close()
        file_logger.info("Database session closed for customer/account/device generation")


@job
def customer_data_generation_job():
    """Job to generate customers, accounts, and devices"""
    generate_customers_accounts_devices()


# ===== JOB 2: TRANSACTION GENERATION =====

@op
def generate_payment_transactions(context, config: TransactionConfig) -> Dict[str, Any]:
    """Generate payment transactions and authentication logs"""
    logger = get_dagster_logger()
    file_logger = setup_logger('TransactionDataGeneration')

    logger.info("Starting payment transaction generation")
    file_logger.info("Starting payment transaction generation")

    try:
        session = Session()
        with session.begin():
            # Convert SQLAlchemy objects to dictionaries
            def model_to_dict(obj):
                return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}

            # Fetch accounts and devices
            from src.models import BankAccount, Device
            accounts = [model_to_dict(acc) for acc in session.query(BankAccount).all()]

            # Generate payment transactions
            transactions = populate_payment_transactions(
                session,
                num_transactions=config.num_transactions
            )
            logger.info(f"Generated {len(transactions)} payment transactions")
            file_logger.info(f"Generated {len(transactions)} payment transactions")

            # Generate authentication logs
            auth_logs = populate_authentication_logs(session, transactions, accounts)
            logger.info(f"Generated {len(auth_logs)} authentication logs")
            file_logger.info(f"Generated {len(auth_logs)} authentication logs")

            session.commit()
            logger.info("Payment transaction generation completed successfully")
            file_logger.info("Payment transaction generation completed successfully")

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
        logger.error(f"Payment transaction generation failed: {str(e)}")
        file_logger.error(f"Payment transaction generation failed: {str(e)}")
        raise
    finally:
        session.close()
        file_logger.info("Database session closed for payment transaction generation")


@job
def transaction_generation_job():
    """Job to generate payment transactions and authentication logs"""
    generate_payment_transactions()


# ===== JOB 3: DATA QUALITY CHECKS AND MONITORING =====

@op
def run_data_quality_checks(context) -> Dict[str, Any]:
    """Run data quality checks"""
    logger = get_dagster_logger()
    file_logger = setup_logger('DataQualityChecks')

    logger.info("Starting data quality checks")
    file_logger.info("Starting data quality checks")

    try:
        checker = DataQualityChecker()
        checker.run_checks()
        issue_count = len(checker.issues)

        if issue_count > 0:
            logger.warning(f"Data quality checks found {issue_count} issues")
            file_logger.warning(f"Data quality checks found {issue_count} issues")
        else:
            logger.info("Data quality checks passed with no issues")
            file_logger.info("Data quality checks passed with no issues")

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
        logger.error(f"Data quality checks failed: {str(e)}")
        file_logger.error(f"Data quality checks failed: {str(e)}")
        raise
    finally:
        file_logger.info("Data quality checks completed")


@op
def run_risk_monitoring(context) -> Dict[str, Any]:
    """Run risk monitoring checks"""
    logger = get_dagster_logger()
    file_logger = setup_logger('RiskMonitoring')

    logger.info("Starting risk monitoring checks")
    file_logger.info("Starting risk monitoring checks")

    try:
        monitor = RiskMonitor()
        monitor.run_checks()
        issue_count = len(monitor.issues)

        if issue_count > 0:
            logger.warning(f"Risk monitoring found {issue_count} issues")
            file_logger.warning(f"Risk monitoring found {issue_count} issues")
        else:
            logger.info("Risk monitoring passed with no issues")
            file_logger.info("Risk monitoring passed with no issues")

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
        logger.error(f"Risk monitoring failed: {str(e)}")
        file_logger.error(f"Risk monitoring failed: {str(e)}")
        raise
    finally:
        file_logger.info("Risk monitoring completed")


@job
def quality_and_monitoring_job():
    """Job to run data quality checks and risk monitoring"""
    quality_result = run_data_quality_checks()
    risk_result = run_risk_monitoring()


# ===== SCHEDULES =====

# Schedule 1: Customer data generation every 6 hours
customer_data_schedule = ScheduleDefinition(
    job=customer_data_generation_job,
    cron_schedule="0 */6 * * *",  # Every 6 hours
    default_status=DefaultScheduleStatus.RUNNING
)

# Schedule 2: Transaction generation every 3 hours
transaction_data_schedule = ScheduleDefinition(
    job=transaction_generation_job,
    cron_schedule="0 */3 * * *",  # Every 3 hours
    default_status=DefaultScheduleStatus.RUNNING
)

# Schedule 3: Quality checks and monitoring every 12 hours
quality_monitoring_schedule = ScheduleDefinition(
    job=quality_and_monitoring_job,
    cron_schedule="0 */12 * * *",  # Every 12 hours
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
