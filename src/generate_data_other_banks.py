from sqlalchemy import create_engine, func, select, text
from sqlalchemy.orm import sessionmaker
from faker import Faker
import random
from rich.progress import track
from datetime import datetime
from typing import List, Dict
from models import Banks, OtherBanksCustomers, OtherBanksAccounts

# Initialize Faker for realistic Vietnamese data
fake = Faker('vi_VN')
random.seed()

# Database connection parameters
db_params = {
    'dbname': 'timo_digital_bank',
    'user': 'togiabao',
    'password': 'mysecretpassword',
    'host': '34.228.244.87',
    'port': '5432'
}
connection_string = f"postgresql://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['dbname']}"

# Create SQLAlchemy engine
engine = create_engine(connection_string)
Session = sessionmaker(bind=engine)

# Helper functions
generated_cccds = set()
generated_phones = set()
generated_accounts = set()


def get_next_id(session: Session, sequence_name: str) -> int:
    sql = f"SELECT nextval('{sequence_name}')"
    return session.execute(text(sql)).scalar()


def generate_random_digits(length: int) -> str:
    return ''.join(str(random.randint(0, 9)) for _ in range(length))


def random_cccd(session: Session) -> str:
    while True:
        cccd = generate_random_digits(12)
        if cccd in generated_cccds:
            continue
        exists = session.execute(
            select(func.count()).where(OtherBanksCustomers.cccd_number == cccd)
        ).scalar_one_or_none()
        if exists == 0:
            generated_cccds.add(cccd)
            return cccd


def random_phone_number(session: Session) -> str:
    prefixes = ['090', '091', '093', '094', '096', '097', '098']
    while True:
        phone = f"{random.choice(prefixes)}{generate_random_digits(7)}"
        if phone in generated_phones:
            continue
        exists = session.execute(
            select(func.count()).where(OtherBanksCustomers.phone_number == phone)
        ).scalar_one_or_none()
        if exists == 0:
            generated_phones.add(phone)
            return phone


def random_account_number(session: Session, bank_code: str) -> str:
    while True:
        account_number = f"{bank_code}{generate_random_digits(10)}"
        if account_number in generated_accounts:
            continue
        exists = session.execute(
            select(func.count()).where(OtherBanksAccounts.account_number == account_number)
        ).scalar_one_or_none()
        if exists == 0:
            generated_accounts.add(account_number)
            return account_number


# Retrieve existing banks
def model_to_dict(obj):
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}


def get_existing_banks(session: Session) -> List[Dict]:
    return [model_to_dict(bank) for bank in session.scalars(select(Banks)).all()]


# Populate other_banks_customers
def populate_other_banks_customers(session: Session, banks: List[Dict]) -> List[Dict]:
    customers = []
    customer_counts = {bank['bank_code']: 60 if bank['is_domestic'] else 30 for bank in banks}

    for bank in track(banks, description="Generating other banks customers..."):
        bank_code = bank['bank_code']
        bank_id = bank['bank_id']
        num_customers = customer_counts.get(bank_code, 10)
        for _ in range(num_customers):
            customer_id = get_next_id(session, 'other_banks_customers_customer_id_seq')
            cccd_number = random_cccd(session)
            full_name = fake.name()
            phone_number = random_phone_number(session)

            customers.append({
                'customer_id': customer_id,
                'bank_id': bank_id,
                'cccd_number': cccd_number,
                'full_name': full_name,
                'phone_number': phone_number,
                'created_at': datetime.now()
            })

    session.bulk_insert_mappings(OtherBanksCustomers, customers)
    return customers


# Populate other_banks_accounts
def populate_other_banks_accounts(session: Session, customers: List[Dict], banks: List[Dict]) -> List[Dict]:
    accounts = []
    bank_code_map = {bank['bank_id']: bank['bank_code'] for bank in banks}

    for customer in track(customers, description="Generating other banks accounts..."):
        customer_id = customer['customer_id']
        bank_id = customer['bank_id']
        bank_code = bank_code_map[bank_id]
        for _ in range(random.randint(1, 2)):
            account_id = get_next_id(session, 'other_banks_accounts_account_id_seq')
            account_number = random_account_number(session, bank_code)
            balance = round(random.uniform(0, 1000000000), 2)

            accounts.append({
                'account_id': account_id,
                'customer_id': customer_id,
                'account_number': account_number,
                'balance': balance,
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            })

    session.bulk_insert_mappings(OtherBanksAccounts, accounts)
    return accounts


# Main function to generate data
def generate_other_banks_customers_accounts():
    session = Session()
    try:
        with session.begin():
            banks = get_existing_banks(session)
            if not banks:
                raise Exception("No banks found in the banks table. Please populate it first.")
            customers = populate_other_banks_customers(session, banks)
            accounts = populate_other_banks_accounts(session, customers, banks)
            print(f"Generated {len(customers)} customers and {len(accounts)} accounts for {len(banks)} banks.")
    except Exception as e:
        print(f"Error: {e}")
        session.rollback()
    finally:
        session.close()


if __name__ == "__main__":
    generate_other_banks_customers_accounts()
