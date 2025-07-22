from sqlalchemy import ForeignKey, CheckConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql.sqltypes import String, Numeric, Boolean, DateTime, Date, SmallInteger
from sqlalchemy.dialects.postgresql import INTEGER, BIGINT
from datetime import datetime


class Base(DeclarativeBase):
    pass


class Banks(Base):
    __tablename__ = 'banks'
    bank_id: Mapped[int] = mapped_column(INTEGER, primary_key=True, autoincrement=True)
    bank_code: Mapped[str] = mapped_column(String(10), nullable=False, unique=True)
    bank_name: Mapped[str] = mapped_column(String(50), nullable=False)
    is_domestic: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.current_timestamp())


class OtherBanksCustomers(Base):
    __tablename__ = 'other_banks_customers'
    customer_id: Mapped[int] = mapped_column(INTEGER, primary_key=True, autoincrement=True)
    bank_id: Mapped[int] = mapped_column(INTEGER, ForeignKey('banks.bank_id'), nullable=False)
    cccd_number: Mapped[str] = mapped_column(String(12), unique=True, nullable=True)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(10), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.current_timestamp())

    __table_args__ = (
        CheckConstraint("cccd_number ~ '^[0-9]{12}$'", name='chk_cccd_number_other'),
        CheckConstraint("phone_number ~ '^[0-9]{10}$'", name='chk_phone_number_other'),
    )


class OtherBanksAccounts(Base):
    __tablename__ = 'other_banks_accounts'
    account_id: Mapped[int] = mapped_column(INTEGER, primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(INTEGER, ForeignKey('other_banks_customers.customer_id'), nullable=False)
    account_number: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    balance: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False, server_default='0.00')
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.current_timestamp())
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.current_timestamp())


class Customer(Base):
    __tablename__ = 'customers'
    customer_id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    customer_type: Mapped[str] = mapped_column(String(20), nullable=False)
    cccd_number: Mapped[str] = mapped_column(String(12), unique=True, nullable=True)
    tax_code: Mapped[str] = mapped_column(String(10), unique=True)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    date_of_birth: Mapped[Date] = mapped_column(Date, nullable=True)
    phone_number: Mapped[str] = mapped_column(String(10), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(100), nullable=True)
    address: Mapped[str] = mapped_column(String, nullable=False)
    registration_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.current_timestamp())
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default='active')
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.current_timestamp())
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.current_timestamp())

    __table_args__ = (
        CheckConstraint("customer_type IN ('individual', 'organization')", name='chk_customer_type'),
        CheckConstraint("status IN ('active', 'inactive', 'suspended')", name='chk_status'),
        CheckConstraint("cccd_number ~ '^[0-9]{12}$'", name='chk_cccd_number'),
        CheckConstraint("tax_code ~ '^[0-9]{10}$'", name='chk_tax_code'),
        CheckConstraint("phone_number ~ '^[0-9]{10}$'", name='chk_phone_number'),
        CheckConstraint(
            "(customer_type = 'individual' AND cccd_number IS NOT NULL) OR "
            "(customer_type = 'organization' AND tax_code IS NOT NULL)",
            name='chk_identity'
        ),
    )


class BankAccount(Base):
    __tablename__ = 'bank_accounts'
    account_id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(BIGINT, ForeignKey('customers.customer_id'), nullable=False)
    account_number: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    account_type: Mapped[str] = mapped_column(String(20), nullable=False)
    balance: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False, server_default='0.00')
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default='active')
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.current_timestamp())
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.current_timestamp())

    __table_args__ = (
        CheckConstraint("account_type IN ('savings', 'checking', 'ewallet')", name='chk_account_type'),
        CheckConstraint("status IN ('active', 'inactive', 'frozen')", name='chk_status'),
    )


class Device(Base):
    __tablename__ = 'devices'
    device_id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(BIGINT, ForeignKey('customers.customer_id'), nullable=False)
    device_type: Mapped[str] = mapped_column(String(20), nullable=False)
    device_identifier: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    os_info: Mapped[str] = mapped_column(String(100), nullable=False)
    is_trusted: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default='false')
    first_seen: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.current_timestamp())
    last_seen: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.current_timestamp())
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.current_timestamp())
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default='active')

    __table_args__ = (
        CheckConstraint("device_type IN ('mobile', 'computer', 'tablet')", name='chk_device_type'),
        CheckConstraint("status IN ('active', 'blocked', 'suspicious')", name='chk_status'),
    )


class AuthenticationMethod(Base):
    __tablename__ = 'authentication_methods'
    auth_id: Mapped[int] = mapped_column(SmallInteger, primary_key=True, autoincrement=True)
    method_type: Mapped[str] = mapped_column(String(50), nullable=False)
    method_name: Mapped[str] = mapped_column(String(100), nullable=False)
    security_level: Mapped[str] = mapped_column(String(1), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)

    __table_args__ = (
        CheckConstraint(
            "method_type IN ('sms_otp', 'email_otp', 'voice_otp', 'soft_otp_basic', 'soft_otp_advanced', "
            "'token_otp_basic', 'token_otp_advanced', 'biometric', 'fido', 'digital_signature', "
            "'two_channel', 'matrix_card')",
            name='chk_method_type'
        ),
        CheckConstraint("security_level IN ('A', 'B', 'C', 'D')", name='chk_security_level'),
    )


class PaymentTransaction(Base):
    __tablename__ = 'payment_transactions'
    transaction_id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    from_account_id: Mapped[int] = mapped_column(BIGINT, ForeignKey('bank_accounts.account_id'), nullable=False)
    to_account_internal_id: Mapped[int] = mapped_column(BIGINT, ForeignKey('bank_accounts.account_id'), nullable=True)
    to_account_external_id: Mapped[int] = mapped_column(BIGINT, ForeignKey('other_banks_accounts.account_id'), nullable=True)
    customer_id: Mapped[int] = mapped_column(BIGINT, ForeignKey('customers.customer_id'), nullable=False)
    transaction_type: Mapped[str] = mapped_column(String(50), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    security_level: Mapped[str] = mapped_column(String(1), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    transaction_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.current_timestamp())
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default='pending')
    device_id: Mapped[int] = mapped_column(BIGINT, ForeignKey('devices.device_id'), nullable=False)
    is_suspicious: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default='false')
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.current_timestamp())

    __table_args__ = (
        CheckConstraint(
            "transaction_type IN ('transfer_same_bank_same_owner', 'transfer_same_bank_diff_owner', "
            "'transfer_interbank_domestic', 'transfer_interbank_international', 'payment_goods_services', "
            "'ewallet_topup', 'ewallet_withdrawal', 'inquiry', 'ewallet_transfer')",
            name='chk_transaction_type'
        ),
        CheckConstraint("security_level IN ('A', 'B', 'C', 'D')", name='chk_security_level'),
        CheckConstraint("status IN ('pending', 'completed', 'failed', 'cancelled')", name='chk_status'),
    )


class AuthenticationLog(Base):
    __tablename__ = 'authentication_logs'
    log_id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    transaction_id: Mapped[int] = mapped_column(BIGINT, ForeignKey('payment_transactions.transaction_id'), nullable=False)
    auth_method_id: Mapped[int] = mapped_column(SmallInteger, ForeignKey('authentication_methods.auth_id'), nullable=False)
    auth_result: Mapped[str] = mapped_column(String(20), nullable=False)
    auth_timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.current_timestamp())
    failure_reason: Mapped[str] = mapped_column(String(200), nullable=False)

    __table_args__ = (
        CheckConstraint("auth_result IN ('success', 'failed', 'expired', 'cancelled')", name='chk_auth_result'),
    )


class DailyTransactionSummary(Base):
    __tablename__ = 'daily_transaction_summaries'
    summary_id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    account_id: Mapped[int] = mapped_column(BIGINT, ForeignKey('bank_accounts.account_id'), nullable=False)
    customer_id: Mapped[int] = mapped_column(BIGINT, ForeignKey('customers.customer_id'), nullable=False)
    transaction_date: Mapped[Date] = mapped_column(Date, nullable=False)
    total_amount: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False, server_default='0.00')
    category_a_amount: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False, server_default='0.00')
    category_b_amount: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False, server_default='0.00')
    category_c_amount: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False, server_default='0.00')
    category_d_amount: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False, server_default='0.00')
    strong_auth_used: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default='false')
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.current_timestamp())
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.current_timestamp())

    __table_args__ = (
        CheckConstraint("unique (account_id, transaction_date)", name='unique_account_date'),
    )


class RiskAlert(Base):
    __tablename__ = 'risk_alerts'
    alert_id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    transaction_id: Mapped[int] = mapped_column(BIGINT, ForeignKey('payment_transactions.transaction_id'), nullable=False)
    alert_type: Mapped[str] = mapped_column(String(50), nullable=False)
    alert_message: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default='open')
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.current_timestamp())
    resolved_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    __table_args__ = (
        CheckConstraint(
            "alert_type IN ('high_value_transaction', 'suspicious_device', 'auth_failure', "
            "'daily_limit_exceeded', 'weak_authentication', 'unusual_pattern', 'compliance_violation')",
            name='chk_alert_type'
        ),
        CheckConstraint("status IN ('open', 'investigating', 'resolved', 'false_positive')", name='chk_status'),
    )
