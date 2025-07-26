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
        email = fake.email() if random.choices([True, False], weights=[90, 10])[0] else None
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
            account_type = random.choices(['savings', 'checking', 'ewallet'], weights=[45, 35, 20])[0]
            balance = round(random.uniform(0, 1000000000), 2)
            status = random.choices(['active', 'inactive', 'frozen'], weights=[96, 3, 1])[0]

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
            is_trusted = random.choices([True, False], weights=[96, 4])[0]
            status = random.choices(['active', 'blocked', 'suspicious'], weights=[97, 2, 1])[0]

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


# Define amount distribution for transactions
AMOUNT_DISTRIBUTION = {
    # Min, Max, Weight
    (Decimal('10000'), Decimal('10000000')): 0.30,
    (Decimal('10000001'), Decimal('100000000')): 0.40,
    (Decimal('100000001'), Decimal('500000000')): 0.20,
    (Decimal('500000001'), Decimal('1000000000')): 0.05,
    # Edge cases (remaining 0.05 weight will be distributed here or in the above ranges)
    # These are specific values, not ranges, to hit thresholds
    'edge_cases': [
        Decimal('5000000'), Decimal('5000001'),  # Around 5M
        Decimal('10000000'), Decimal('10000001'),  # Around 10M
        Decimal('20000000'), Decimal('20000001'),  # Around 20M
        Decimal('100000000'), Decimal('100000001'),  # Around 100M
        Decimal('500000000'), Decimal('500000001'),  # Around 500M
        Decimal('1500000000'), Decimal('1500000001'),  # Around 1.5B
        Decimal('1000000000'), Decimal('1000000001'),  # Around 1B (for international)
        Decimal('5000000000'), Decimal('5000000001'),  # Around 5B (for organization international)
        Decimal('10000000000'), Decimal('10000000001'),  # Around 10B (for organization domestic)
        Decimal('0.01'),  # Minimum possible amount
        Decimal('99999999999.99')  # A very large amount (e.g., 100B)
    ],
    'edge_case_weight': 0.05
}


def generate_amount_based_on_distribution(current_balance: Decimal) -> Decimal:
    """Generates a transaction amount based on predefined distribution and current balance."""
    choice = random.random()

    # Handle edge cases
    if choice < AMOUNT_DISTRIBUTION['edge_case_weight']:
        amount = random.choice(AMOUNT_DISTRIBUTION['edge_cases'])
        if amount <= current_balance:
            return amount
        # If edge case amount is too high, try to find a smaller one or fall through to normal distribution
        for _ in range(3):  # Retry a few times for a suitable edge case
            smaller_edge_cases = [a for a in AMOUNT_DISTRIBUTION['edge_cases'] if a <= current_balance]
            if smaller_edge_cases:
                return random.choice(smaller_edge_cases)

    # Handle normal distribution
    cumulative_weight = 0
    for (min_val, max_val), weight in AMOUNT_DISTRIBUTION.items():
        if isinstance(min_val, Decimal):  # Check if it's a range
            cumulative_weight += weight
            if choice < cumulative_weight + AMOUNT_DISTRIBUTION['edge_case_weight']:
                # Ensure amount does not exceed current balance
                upper_bound = min(max_val, current_balance)
                if min_val <= upper_bound:
                    return Decimal(str(round(random.uniform(float(min_val), float(upper_bound)), 2)))
                else:
                    # If the range is above balance, try smaller ranges or a small default
                    return Decimal(
                        str(round(random.uniform(10000, float(min(current_balance, Decimal('1000000')))), 2)))

    # Fallback if no range matches or balance is too low for chosen range
    return Decimal(str(round(random.uniform(10000, float(min(current_balance, Decimal('1000000')))), 2)))


# Populate payment_transactions with edge cases
def populate_payment_transactions(
        session: Session,
        num_transactions: int = 250,
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
                elif transaction_type == 'inquiry':
                    amount = Decimal('0.00')

                if transaction_type != 'inquiry':
                    # Generate amount based on distribution and current balance
                    amount = generate_amount_based_on_distribution(from_balance)
                    if amount <= 0:
                        retries += 1
                        continue

                # Set transaction status
                status = random.choices(['pending', 'completed', 'failed', 'cancelled'],
                                        weights=[0.1, 0.8, 0.05, 0.05], k=1)[0]

                # If transaction is completed, ensure balance is sufficient
                if status == 'completed' and from_balance < amount:
                    retries += 1
                    continue

                # Set transaction date
                transaction_date = datetime.now() - timedelta(seconds=random.randint(0, 30 * 86400))

                # Generate transaction details
                description = f"{transaction_type} on {transaction_date.strftime('%Y-%m-%d %H:%M:%S')}"
                device_id = random.choice(active_devices)['device_id']
                if transaction_type != 'inquiry':
                    is_suspicious = random.random() < (0.2 if amount > 1000000000 else 0.1)
                else:
                    is_suspicious = False
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
        # Access attributes using dot notation for SQLAlchemy ORM objects
        customer_id = account.customer_id
        customer_type = session.execute(
            select(Customer.customer_type).where(Customer.customer_id == customer_id)
        ).scalar_one_or_none()
        account_to_customer_type[account.account_id] = customer_type or 'individual'

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
            transactions = populate_payment_transactions(session, 250)
            populate_authentication_logs(session, transactions, accounts)
            print("Data population completed successfully.")
    except Exception as e:
        print(f"Error: {e}")
        session.rollback()
    finally:
        session.close()


if __name__ == "__main__":
    main()
