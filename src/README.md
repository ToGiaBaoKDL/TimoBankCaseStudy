## Overview

The `src` directory contains the core business logic, data generation, data quality, risk monitoring, and ORM model definitions for the Timo Digital Bank Case Study. This is the heart of the simulation and analytics pipeline.

## File Descriptions

- **models.py**  
  - Defines all SQLAlchemy ORM models for the database schema.
  - Models include: `Customer`, `BankAccount`, `Device`, `AuthenticationMethod`, `PaymentTransaction`, `AuthenticationLog`, `RiskAlert`, and interbank entities.
  - Each model enforces business constraints (e.g., unique IDs, valid phone/CCCD, account types, status).
  - Centralizes all relationships and constraints for data integrity.

- **generate_data_timo.py**  
  - Generates synthetic data for Timo Bank: customers, accounts, devices, transactions, and authentication logs.
  - Uses Faker for realistic Vietnamese data.
  - Ensures referential integrity and covers edge cases (large transactions, suspicious activity, device trust).
  - Functions are modular: you can generate only customers, only accounts, etc.

- **generate_data_other_banks.py**  
  - Generates synthetic data for other banks (customers and accounts), supporting interbank transaction scenarios.
  - Simulates both domestic and international banks.
  - Ensures uniqueness and referential integrity for all generated data.

- **data_quality_standards.py**  
  - Implements automated data quality checks:
    - Null value detection in critical fields
    - Uniqueness constraints (ID, tax code, phone, account number)
    - Format validation (national ID, phone)
    - Foreign key integrity
  - Logs all issues to `logs/data_quality_standards.log`.
  - Can be run as a standalone script for batch data quality assessment.

- **monitoring_audit.py**  
  - Implements risk monitoring and audit logic:
    - Detects high-value transactions without strong authentication
    - Flags transactions from untrusted devices
    - Checks for daily transaction limit breaches
    - Aggregates and logs risk issues to `logs/monitoring_audit.log`
  - Can be run as a standalone script for batch risk monitoring.

- **__init__.py**  
  - Empty file to mark the directory as a Python package.

## Usage

- All scripts expect a PostgreSQL database initialized with the provided schema.
- Each script can be run independently for data generation, quality checks, or risk monitoring.
- Logging is performed to the `logs/` directory for traceability.
- All database connection parameters are set in the scripts or via environment variables. 