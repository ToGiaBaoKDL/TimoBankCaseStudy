from sqlalchemy import create_engine, func, select, update
from sqlalchemy.orm import sessionmaker
from faker import Faker
import random
from rich.progress import track
from datetime import datetime, timedelta
import uuid
from typing import List, Dict
from decimal import Decimal
from models import (
    Customer, BankAccount, Device, AuthenticationMethod, PaymentTransaction,
    AuthenticationLog, OtherBanksAccounts
)
from dotenv import load_dotenv
import os


# Load environment variables
load_dotenv()

# Initialize Faker for realistic data
fake = Faker('vi_VN')
random.seed()

# Database connection parameters
db_params = {
    'dbname': os.getenv("DB_NAME", "postgres"),
    'user': os.getenv("DB_USER", "postgres"),
    'password': os.getenv("DB_PASSWORD", "yourpassword"),
    'host': os.getenv("DB_HOST", "localhost"),
    'port': '5432'
}
connection_string = f"postgresql://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['dbname']}"

# Create SQLAlchemy engine
engine = create_engine(connection_string)
Session = sessionmaker(bind=engine)


# Helper functions
def generate_random_digits(length: int) -> str:
    return ''.join(str(random.randint(0, 9)) for _ in range(length))


def random_cccd(session: Session) -> str:
    while True:
        cccd = generate_random_digits(12)
        count = session.execute(select(func.count()).where(Customer.cccd_number == cccd)).scalar_one_or_none()
        if count == 0:
            return cccd


def random_tax_code(session: Session) -> str:
    while True:
        tax_code = generate_random_digits(10)
        count = session.execute(select(func.count()).where(Customer.tax_code == tax_code)).scalar_one_or_none()
        if count == 0:
            return tax_code


def random_phone_number(session: Session) -> str:
    prefixes = ['090', '091', '093', '094', '096', '097', '098']
    while True:
        phone = f"{random.choice(prefixes)}{generate_random_digits(7)}"
        count = session.execute(select(func.count()).where(Customer.phone_number == phone)).scalar_one_or_none()
        if count == 0:
            return phone


def random_account_number(session: Session) -> str:
    while True:
        account_number = f"TIMO{random.randint(1000000000000000, 9999999999999999)}"
        count = session.execute(select(func.count()).where(BankAccount.account_number == account_number)).scalar_one_or_none()
        if count == 0:
            return account_number


def random_device_identifier() -> str:
    return str(uuid.uuid4())


def random_date(start_date: datetime, end_date: datetime) -> datetime:
    time_between = end_date - start_date
    days = time_between.days
    random_days = random.randint(0, days)
    return start_date + timedelta(days=random_days)


# Populate customers
def populate_customers(session: Session, num_customers: int = 60) -> List[Dict]:
    customers = []
    for _ in track(range(num_customers), description="Generating customers..."):
        customer_type = random.choices(['individual', 'organization'], weights=[90, 10])[0]
        cccd_number = random_cccd(session) if customer_type == 'individual' else None
        tax_code = random_tax_code(session)
        full_name = fake.name() if customer_type == 'individual' else fake.company()
        date_of_birth = random_date(datetime(1980, 1, 1), datetime(2005, 1, 1)) if customer_type == 'individual' else None
        phone_number = random_phone_number(session)
        email = fake.email() if random.choice([True, False]) else None
        address = fake.address()
        status = random.choices(['active', 'inactive', 'suspended'], weights=[95, 3, 2])[0]

        customer_id = session.execute(select(func.nextval('customers_customer_id_seq'))).scalar_one()

        customers.append({
            'customer_id': customer_id,
            'customer_type': customer_type,
            'cccd_number': cccd_number,
            'tax_code': tax_code,
            'full_name': full_name,
            'date_of_birth': date_of_birth,
            'phone_number': phone_number,
            'email': email,
            'address': address,
            'status': status
        })

    session.bulk_insert_mappings(Customer, customers)
    return customers


# Populate bank_accounts
def populate_bank_accounts(session: Session, customers: List[Dict], num_accounts_per_customer: int = 2) -> List[Dict]:
    accounts = []
    for customer in track(customers, description="Generating customers' timo accounts..."):
        customer_id = customer['customer_id']
        for _ in range(random.randint(1, num_accounts_per_customer)):
            account_id = session.execute(select(func.nextval('bank_accounts_account_id_seq'))).scalar_one()
            account_number = random_account_number(session)
            account_type = random.choices(['savings', 'checking', 'ewallet'], weights=[40, 30, 30])[0]
            balance = round(random.uniform(0, 1000000000), 2)
            status = random.choices(['active', 'inactive', 'frozen'], weights=[95, 3, 2])[0]

            accounts.append({
                'account_id': account_id,
                'customer_id': customer_id,
                'account_number': account_number,
                'account_type': account_type,
                'balance': balance,
                'status': status
            })

    session.bulk_insert_mappings(BankAccount, accounts)
    return accounts


# Populate devices
def populate_devices(session: Session, customers: List[Dict], num_devices_per_customer: int = 2) -> List[Dict]:
    devices = []
    for customer in track(customers, description="Generating customers' devices..."):
        customer_id = customer['customer_id']
        for _ in range(random.randint(1, num_devices_per_customer)):
            device_id = session.execute(select(func.nextval('devices_device_id_seq'))).scalar_one()
            device_type = random.choice(['mobile', 'computer', 'tablet'])
            device_identifier = random_device_identifier()
            os_info = random.choice(['Android 12', 'iOS 16', 'Windows 11', 'macOS Ventura', 'Windows 10',
                                     'iOS 15', 'Android 11', 'macOS Big Sur', 'Windows 7', 'Android 10'])
            is_trusted = random.choices([True, False], weights=[95, 5])[0]
            status = random.choices(['active', 'blocked', 'suspicious'], weights=[95, 3, 2])[0]

            devices.append({
                'device_id': device_id,
                'customer_id': customer_id,
                'device_type': device_type,
                'device_identifier': device_identifier,
                'os_info': os_info,
                'is_trusted': is_trusted,
                'status': status
            })

    session.bulk_insert_mappings(Device, devices)
    return devices


# Verify authentication_methods
def verify_authentication_methods(session: Session) -> bool:
    count = session.execute(select(func.count()).select_from(AuthenticationMethod)).scalar_one_or_none()
    if count is None or count < 12:
        raise Exception("Authentication methods not fully populated. Please run schema.sql first.")
    return True


# Populate payment_transactions with edge cases
def populate_payment_transactions(
        session: Session,
        num_transactions: int = 200,
        max_retries: int = 3
) -> list[dict]:
    def model_to_dict(obj):
        return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}

    # Fetch existing data from database
    active_accounts = [model_to_dict(acc) for acc in session.scalars(
        select(BankAccount).where(BankAccount.status == 'active')
    ).all()]

    active_devices = [model_to_dict(dev) for dev in session.scalars(
        select(Device).where(Device.status == 'active')
    ).all()]

    other_banks_accounts = [model_to_dict(acc) for acc in session.scalars(
        select(OtherBanksAccounts)
    ).all()]

    # Check if required data exists
    if not active_accounts:
        raise ValueError("No active bank accounts found in database")
    if not active_devices:
        raise ValueError("No active devices found in database")

    # Organize accounts by customer
    accounts_by_customer = {}
    for account in active_accounts:
        customer_id = account['customer_id']
        if customer_id not in accounts_by_customer:
            accounts_by_customer[customer_id] = []
        accounts_by_customer[customer_id].append(account)

    # Initialize balance tracking
    other_bank_account_ids = set(acc['account_id'] for acc in other_banks_accounts)
    account_balances = {acc['account_id']: Decimal(str(acc.get('balance', 0.00))) for acc in active_accounts}
    other_bank_balances = {acc['account_id']: Decimal(str(acc.get('balance', 0.00))) for acc in other_banks_accounts}

    transactions = []

    for _ in track(range(num_transactions), description="Generating timo bank transactions..."):
        retries = 0
        while retries < max_retries:
            try:
                # Select transaction type
                transaction_type = random.choices(
                    [
                        'transfer_same_bank_same_owner',
                        'transfer_same_bank_diff_owner',
                        'transfer_interbank_domestic',
                        'transfer_interbank_international',
                        'payment_goods_services',
                        'ewallet_topup',
                        'ewallet_withdrawal',
                        'inquiry',
                        'ewallet_transfer'
                    ],
                    weights=[0.2, 0.2, 0.15, 0.1, 0.15, 0.1, 0.05, 0.03, 0.07],
                    k=1
                )[0]

                # Select source account
                from_account = random.choice(active_accounts)
                from_account_id = from_account['account_id']
                customer_id = from_account['customer_id']
                from_balance = account_balances.get(from_account_id, Decimal('0.00'))

                # Determine destination account
                to_account_internal_id = None
                to_account_external_id = None
                if transaction_type == 'transfer_same_bank_same_owner':
                    customer_accounts = accounts_by_customer.get(customer_id, [])
                    if len(customer_accounts) <= 1:
                        retries += 1
                        continue
                    to_account = random.choice(
                        [acc for acc in customer_accounts if acc['account_id'] != from_account_id])
                    to_account_internal_id = to_account['account_id']
                elif transaction_type == 'transfer_same_bank_diff_owner':
                    other_customer_accounts = [acc for acc in active_accounts if acc['customer_id'] != customer_id]
                    if not other_customer_accounts:
                        retries += 1
                        continue
                    to_account = random.choice(other_customer_accounts)
                    to_account_internal_id = to_account['account_id']
                elif transaction_type in ['transfer_interbank_domestic', 'transfer_interbank_international',
                                          'ewallet_transfer']:
                    if not other_bank_account_ids:
                        retries += 1
                        continue
                    to_account = random.choice(other_banks_accounts)
                    to_account_external_id = to_account['account_id']

                # Set transaction status
                status = random.choices(['pending', 'completed', 'failed', 'cancelled'],
                                        weights=[0.2, 0.7, 0.05, 0.05], k=1)[0]

                # Determine amount with edge cases
                if random.random() < 0.05:
                    amount = random.choice([
                        Decimal('0.01'),  # Minimum amount
                        Decimal('9999999999.99'),  # Maximum amount
                        Decimal(str(round(random.uniform(0, 0.99), 2))),  # Very small amount
                    ])
                else:
                    max_amount = min(from_balance, Decimal('5000000000')) if status == 'completed' else Decimal(
                        '5000000000')
                    amount = Decimal(str(round(random.uniform(100000, float(max_amount)), 2)))

                if amount <= 0:
                    retries += 1
                    continue

                if status == 'completed' and from_balance < amount:
                    retries += 1
                    continue

                # Set transaction date
                transaction_date = datetime.now()
                if random.random() < 0.1:
                    transaction_date -= timedelta(days=random.randint(1, 365))

                # Generate transaction details
                description = f"{transaction_type} on {transaction_date.strftime('%Y-%m-%d %H:%M:%S')}"
                device_id = random.choice(active_devices)['device_id']
                is_suspicious = random.random() < (0.3 if amount > 1000000000 else 0.05)
                transaction_id = session.execute(
                    select(func.nextval('payment_transactions_transaction_id_seq'))).scalar_one()

                # Create transaction dictionary
                transaction = {
                    'transaction_id': transaction_id,
                    'from_account_id': from_account_id,
                    'to_account_internal_id': to_account_internal_id,
                    'to_account_external_id': to_account_external_id,
                    'customer_id': customer_id,
                    'transaction_type': transaction_type,
                    'amount': amount,
                    'security_level': 'A',
                    'description': description,
                    'transaction_date': transaction_date,
                    'status': status,
                    'device_id': device_id,
                    'is_suspicious': is_suspicious,
                    'created_at': datetime.now()
                }

                transactions.append(transaction)

                # Update balances for completed transactions
                if status == 'completed':
                    account_balances[from_account_id] -= amount
                    session.execute(
                        update(BankAccount)
                        .where(BankAccount.account_id == from_account_id)
                        .values(balance=account_balances[from_account_id], updated_at=datetime.now())
                    )

                    if to_account_internal_id:
                        account_balances[to_account_internal_id] = account_balances.get(to_account_internal_id,
                                                                                        Decimal('0.00')) + amount
                        session.execute(
                            update(BankAccount)
                            .where(BankAccount.account_id == to_account_internal_id)
                            .values(balance=account_balances[to_account_internal_id], updated_at=datetime.now())
                        )
                    elif to_account_external_id:
                        other_bank_balances[to_account_external_id] = other_bank_balances.get(to_account_external_id,
                                                                                              Decimal('0.00')) + amount
                        session.execute(
                            update(OtherBanksAccounts)
                            .where(OtherBanksAccounts.account_id == to_account_external_id)
                            .values(balance=other_bank_balances[to_account_external_id], updated_at=datetime.now())
                        )

                break

            except Exception as e:
                retries += 1
                if retries == max_retries:
                    print(f"Failed to create transaction after {max_retries} attempts: {str(e)}")
                    break
                continue

    if transactions:
        session.bulk_insert_mappings(PaymentTransaction, transactions)
    return transactions


# Populate authentication_logs
def populate_authentication_logs(session: Session, transactions: List[Dict], accounts: List[Dict]) -> List[Dict]:
    logs = []

    auth_methods = {
        'A': [13],  # PIN Code
        'B': [1, 2, 3, 4, 6, 11, 12],  # SMS OTP, Email OTP, Voice OTP, Soft OTP Basic, Token OTP Basic, Two-Channel, Matrix Card
        'C': [5, 7, 8, 9, 10],  # Soft OTP Advanced, Token OTP Advanced, Biometric, FIDO, Digital Signature
        'D': [8, 10]  # Biometric, Digital Signature
    }
    d_secondary_methods = [5, 7, 9]  # Soft OTP Advanced, Token OTP Advanced, FIDO

    account_to_customer_type = {}
    for account in accounts:
        customer_type = account.get('customer_type', 'individual')
        account_to_customer_type[account['account_id']] = customer_type

    for transaction in track(transactions, description="Generating transactions' logs..."):
        transaction_id = transaction['transaction_id']
        from_account_id = transaction['from_account_id']
        security_level = session.execute(
            select(PaymentTransaction.security_level).where(PaymentTransaction.transaction_id == transaction_id)
        ).scalar_one_or_none() or 'A'
        customer_type = account_to_customer_type.get(from_account_id, 'individual')

        allowed_methods = []
        if security_level == 'A':
            allowed_methods = auth_methods['A'] + auth_methods['B'] + auth_methods['C'] + auth_methods['D'] + d_secondary_methods
        elif security_level == 'B':
            allowed_methods = auth_methods['B'] + auth_methods['C'] + auth_methods['D'] + d_secondary_methods
        elif security_level == 'C':
            allowed_methods = auth_methods['C'] + auth_methods['D'] + d_secondary_methods
        elif security_level == 'D':
            allowed_methods = auth_methods['D']

        if customer_type == 'organization':
            allowed_methods = [m for m in allowed_methods if m != 8 or security_level in ['C', 'D']]

        if not allowed_methods:
            allowed_methods = auth_methods['A']

        num_attempts = random.randint(1, 2) if security_level in ['C', 'D'] else 1

        for i in range(num_attempts):
            log_id = session.execute(select(func.nextval('authentication_logs_log_id_seq'))).scalar_one()
            if security_level == 'D' and num_attempts > 1:
                if i == 0:
                    auth_method_id = random.choice(allowed_methods)
                else:
                    available_secondary = [m for m in d_secondary_methods if m in allowed_methods]
                    auth_method_id = random.choice(available_secondary) if available_secondary else random.choice(allowed_methods)
            else:
                auth_method_id = random.choice(allowed_methods)

            auth_result = random.choices(['success', 'failed', 'expired', 'cancelled'], weights=[95, 3, 1, 1])[0]
            failure_reason = '' if auth_result == 'success' else fake.sentence()

            logs.append({
                'log_id': log_id,
                'transaction_id': transaction_id,
                'auth_method_id': auth_method_id,
                'auth_result': auth_result,
                'failure_reason': failure_reason,
                'auth_timestamp': datetime.now()
            })

    session.bulk_insert_mappings(AuthenticationLog, logs)
    return logs


# Main execution
def main():
    session = Session()
    try:
        with session.begin():
            verify_authentication_methods(session)
            customers = populate_customers(session, 50)
            accounts = populate_bank_accounts(session, customers, 2)
            devices = populate_devices(session, customers, 2)
            transactions = populate_payment_transactions(session, 150)
            populate_authentication_logs(session, transactions, accounts)
            print("Data population completed successfully.")
    except Exception as e:
        print(f"Error: {e}")
        session.rollback()
    finally:
        session.close()


if __name__ == "__main__":
    main()
