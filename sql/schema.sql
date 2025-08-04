-- Customers table
CREATE TABLE customers (
    customer_id BIGSERIAL PRIMARY KEY,
    customer_type VARCHAR(20) NOT NULL CHECK (customer_type IN ('individual', 'organization')),
    cccd_number VARCHAR(12) UNIQUE CHECK (cccd_number ~ '^[0-9]{12}$'),
    tax_code VARCHAR(20) NOT NULL UNIQUE CHECK (tax_code ~ '^[0-9]{10}$'),
    full_name VARCHAR(200) NOT NULL,
    date_of_birth DATE,
    phone_number VARCHAR(10) NOT NULL UNIQUE CHECK (phone_number ~ '^[0-9]{10}$'),
    email VARCHAR(100),
    address TEXT NOT NULL,
    registration_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'suspended')),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_identity CHECK (
        (customer_type = 'individual' AND cccd_number IS NOT NULL) OR
        (customer_type = 'organization' AND tax_code IS NOT NULL)
    )
);

-- Bank accounts table
CREATE TABLE bank_accounts (
    account_id BIGSERIAL PRIMARY KEY,
    customer_id BIGSERIAL NOT NULL,
    account_number VARCHAR(30) NOT NULL UNIQUE,
    account_type VARCHAR(20) NOT NULL CHECK (account_type IN ('savings', 'checking', 'ewallet')),
    balance DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'frozen')),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE,
    CONSTRAINT chk_account_type CHECK (account_type IN ('savings', 'checking', 'ewallet'))
);

CREATE INDEX bank_accounts_customer_id_index ON bank_accounts (customer_id);
CREATE INDEX bank_accounts_account_id_index ON bank_accounts (account_id);

-- Devices table
CREATE TABLE devices (
    device_id BIGSERIAL PRIMARY KEY,
    customer_id BIGSERIAL NOT NULL,
    device_type VARCHAR(20) NOT NULL CHECK (device_type IN ('mobile', 'computer', 'tablet')),
    device_identifier VARCHAR(200) NOT NULL UNIQUE,
    os_info VARCHAR(100) NOT NULL,
    is_trusted BOOLEAN NOT NULL DEFAULT FALSE,
    first_seen TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'blocked', 'suspicious')),

    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE INDEX devices_device_identifier_index ON devices (device_identifier);

-- Authentication methods table
CREATE TABLE authentication_methods (
    auth_id SERIAL PRIMARY KEY,
    method_type VARCHAR(50) NOT NULL CHECK (method_type IN (
        'sms_otp', 'email_otp', 'voice_otp', 'soft_otp_basic', 'soft_otp_advanced',
        'token_otp_basic', 'token_otp_advanced', 'biometric', 'fido', 'digital_signature',
        'two_channel', 'matrix_card', 'pin_code'
    )),
    method_name VARCHAR(100) NOT NULL,
    security_level VARCHAR(1) NOT NULL CHECK (security_level IN ('A', 'B', 'C', 'D')),
    description VARCHAR(500) NOT NULL
);

-- Banks table
CREATE TABLE banks (
    bank_id SERIAL PRIMARY KEY,
    bank_code VARCHAR(10) NOT NULL UNIQUE,
    bank_name VARCHAR(50) NOT NULL,
    is_domestic BOOLEAN,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Other banks customers table
CREATE TABLE other_banks_customers (
    customer_id BIGSERIAL PRIMARY KEY,
    bank_id SERIAL NOT NULL,
    cccd_number VARCHAR(12) UNIQUE CHECK (cccd_number ~ '^[0-9]{12}$'),
    full_name VARCHAR(200) NOT NULL,
    phone_number VARCHAR(10) NOT NULL UNIQUE CHECK (phone_number ~ '^[0-9]{10}$'),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (bank_id) REFERENCES banks(bank_id) ON DELETE CASCADE
);

-- Other banks accounts table
CREATE TABLE other_banks_accounts(
    account_id BIGSERIAL PRIMARY KEY,
    customer_id BIGSERIAL NOT NULL,
    account_number VARCHAR(30) NOT NULL UNIQUE,
    balance DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (customer_id) REFERENCES other_banks_customers(customer_id) ON DELETE CASCADE
);

-- Daily transaction summaries table
CREATE TABLE daily_transaction_summaries (
    summary_id BIGSERIAL PRIMARY KEY,
    account_id BIGSERIAL NOT NULL,
    customer_id BIGSERIAL NOT NULL,
    transaction_date DATE NOT NULL,
    total_amount DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    category_a_amount DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    category_b_amount DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    category_c_amount DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    category_d_amount DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    strong_auth_used BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (account_id) REFERENCES bank_accounts(account_id) ,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    CONSTRAINT unique_account_date UNIQUE (account_id, transaction_date)
);

CREATE INDEX daily_transaction_summaries_account_id_transaction_date_index ON daily_transaction_summaries (account_id, transaction_date);
CREATE INDEX daily_transaction_summaries_total_amount_index ON daily_transaction_summaries (total_amount);

-- Payment transactions table
CREATE TABLE payment_transactions (
    transaction_id BIGSERIAL PRIMARY KEY,
    from_account_id BIGINT NOT NULL,
    to_account_internal_id BIGINT,
    to_account_external_id BIGINT,
    customer_id BIGINT NOT NULL,
    transaction_type VARCHAR(50) NOT NULL CHECK (transaction_type IN (
        'transfer_same_bank_same_owner', 'transfer_same_bank_diff_owner',
        'transfer_interbank_domestic', 'transfer_interbank_international',
        'payment_goods_services', 'ewallet_topup', 'ewallet_withdrawal',
        'inquiry', 'ewallet_transfer'
    )),
    amount DECIMAL(15,2) NOT NULL,
    security_level VARCHAR(1) NOT NULL CHECK (security_level IN ('A', 'B', 'C', 'D')),
    description VARCHAR(500) NOT NULL,
    transaction_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'completed', 'failed', 'cancelled')),
    device_id BIGINT NOT NULL,
    is_suspicious BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- FOREIGN KEYS
    FOREIGN KEY (from_account_id) REFERENCES bank_accounts(account_id),
    FOREIGN KEY (to_account_internal_id) REFERENCES bank_accounts(account_id),
    FOREIGN KEY (to_account_external_id) REFERENCES other_banks_accounts(account_id),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (device_id) REFERENCES devices(device_id)
);

CREATE INDEX payment_transactions_transaction_date_index ON payment_transactions (transaction_date);
CREATE INDEX payment_transactions_amount_index ON payment_transactions (amount);
CREATE INDEX payment_transactions_transaction_type_index ON payment_transactions (transaction_type);
CREATE INDEX payment_transactions_status_index ON payment_transactions (status);
CREATE INDEX payment_transactions_from_account_id_index ON payment_transactions (from_account_id, transaction_date);

-- Authentication logs table
CREATE TABLE authentication_logs (
    log_id BIGSERIAL PRIMARY KEY,
    transaction_id BIGINT NOT NULL,
    auth_method_id SMALLINT NOT NULL,
    auth_result VARCHAR(20) NOT NULL CHECK (auth_result IN ('success', 'failed', 'expired', 'cancelled')),
    auth_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    failure_reason VARCHAR(200) NOT NULL,

    FOREIGN KEY (transaction_id) REFERENCES payment_transactions(transaction_id) ON DELETE NO ACTION ON UPDATE NO ACTION,
    FOREIGN KEY (auth_method_id) REFERENCES authentication_methods(auth_id) ON DELETE NO ACTION ON UPDATE NO ACTION
);

CREATE INDEX authentication_logs_auth_result_index ON authentication_logs (auth_result);

-- Risk alerts table
CREATE TABLE risk_alerts (
    alert_id BIGSERIAL PRIMARY KEY,
    transaction_id BIGSERIAL NOT NULL,
    alert_type VARCHAR(50) NOT NULL CHECK (alert_type IN (
        'high_value_transaction', 'untrusted_device', 'auth_failure',
        'weak_authentication', 'unusual_pattern', 'inactive_account',
        'daily_limit_strong_auth', 'high_payment_volume',
        'unusual_cross_border_frequency', 'strong_auth_required', 'auth_failure_rate'
    )),
    alert_message VARCHAR(500) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'investigating', 'resolved', 'false_positive')),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,

    FOREIGN KEY (transaction_id) REFERENCES payment_transactions(transaction_id) ON DELETE NO ACTION ON UPDATE NO ACTION
);

CREATE INDEX risk_alerts_transaction_id_index ON risk_alerts (transaction_id);
CREATE INDEX risk_alerts_alert_type_index ON risk_alerts (alert_type);

-- Insert sample banks (expanded Vietnamese banks + international)
INSERT INTO banks (bank_code, bank_name, is_domestic) VALUES
('VCB', 'Vietcombank', TRUE),
('TCB', 'Techcombank', TRUE),
('ACB', 'Asia Commercial Bank', TRUE),
('SCB', 'Sacombank', TRUE),
('MBB', 'MB Bank', TRUE),
('VPB', 'VPBank', TRUE),
('BIDV', 'BIDV', TRUE),
('VTB', 'VietinBank', TRUE),
('CITI', 'Citibank', FALSE),
('HSBC', 'HSBC', FALSE);

-- Insert default authentication methods based on Appendix 02
INSERT INTO authentication_methods (auth_id, method_type, method_name, security_level, description) VALUES
(1, 'sms_otp', 'SMS OTP', 'B', 'One-time password sent via SMS'),
(2, 'email_otp', 'Email OTP', 'B', 'One-time password sent via email'),
(3, 'voice_otp', 'Voice OTP', 'B', 'One-time password delivered via voice call'),
(4, 'soft_otp_basic', 'Soft OTP Basic', 'B', 'Software-based OTP generator (basic)'),
(5, 'soft_otp_advanced', 'Soft OTP Advanced', 'C', 'Software-based OTP with transaction signing'),
(6, 'token_otp_basic', 'Token OTP Basic', 'B', 'Hardware token OTP generator (basic)'),
(7, 'token_otp_advanced', 'Token OTP Advanced', 'C', 'Hardware token OTP with transaction signing'),
(8, 'biometric', 'Biometric Authentication', 'C', 'Fingerprint, face recognition, or voice recognition'),
(9, 'fido', 'FIDO Authentication', 'C', 'Fast Identity Online standard authentication'),
(10, 'digital_signature', 'Digital Signature', 'C', 'Secure digital signature'),
(11, 'two_channel', 'Two-Channel Authentication', 'B', 'Authentication via separate communication channel'),
(12, 'matrix_card', 'Matrix Card OTP', 'B', 'Matrix card with OTP coordinates'),
(13, 'pin_code', 'PIN Code', 'A', 'Personal Identification Number used for authentication');


-- Trigger to enforce transaction classification based on 2345/QĐ-NHNN
CREATE OR REPLACE FUNCTION classify_transaction()
RETURNS TRIGGER AS $$
DECLARE
    customer_type VARCHAR(20);
    daily_total DECIMAL(15,2);
    tksth DECIMAL(15,2);
    has_strong_auth BOOLEAN;
BEGIN
    -- Get customer type
    SELECT c.customer_type INTO customer_type
    FROM customers c
    WHERE c.customer_id = NEW.customer_id;

    IF customer_type IS NULL THEN
        RAISE EXCEPTION 'Cannot determine customer type for customer_id %', NEW.customer_id;
    END IF;

    -- Check for strong authentication (C or D) in the same day
    SELECT EXISTS (
        SELECT 1
        FROM payment_transactions pt
        JOIN authentication_logs al ON pt.transaction_id = al.transaction_id
        JOIN authentication_methods am ON al.auth_method_id = am.auth_id
        WHERE pt.customer_id = NEW.customer_id
        AND pt.transaction_date::DATE = NEW.transaction_date::DATE
        AND pt.transaction_id != NEW.transaction_id
        AND am.security_level IN ('C', 'D')
        AND al.auth_result = 'success'
    ) INTO has_strong_auth;

    -- Calculate daily total (G + T) and Tksth (A + B transactions)
    SELECT COALESCE(SUM(t.amount), 0) INTO daily_total
    FROM payment_transactions t
    WHERE t.customer_id = NEW.customer_id
    AND t.transaction_date::DATE = NEW.transaction_date::DATE
    AND t.transaction_id != NEW.transaction_id;

    SELECT COALESCE(SUM(t.amount), 0) INTO tksth
    FROM payment_transactions t
    WHERE t.customer_id = NEW.customer_id
    AND t.transaction_date::DATE = NEW.transaction_date::DATE
    AND t.transaction_id != NEW.transaction_id
    AND t.security_level IN ('A', 'B');

    IF has_strong_auth THEN
        tksth := 0; -- Reset Tksth after C or D transaction
    END IF;

    -- Individual customers
    IF customer_type = 'individual' THEN
        -- Group I.1: Inquiry and same-bank same-owner transfers
        IF NEW.transaction_type IN ('inquiry', 'transfer_same_bank_same_owner') THEN
            NEW.security_level = 'A';

        -- Group I.2: Payment for goods and services
        ELSIF NEW.transaction_type = 'payment_goods_services' THEN
            IF NEW.amount + daily_total <= 5000000 THEN
                NEW.security_level = 'A';
            ELSIF NEW.amount + daily_total <= 100000000 THEN
                NEW.security_level = 'B';
            ELSIF NEW.amount + daily_total <= 1500000000 THEN
                NEW.security_level = 'C';
            ELSE
                NEW.security_level = 'D';
            END IF;

        -- Group I.3: Other domestic transfers and e-wallet operations
        ELSIF NEW.transaction_type IN ('transfer_same_bank_diff_owner', 'transfer_interbank_domestic',
                                      'ewallet_transfer', 'ewallet_topup', 'ewallet_withdrawal') THEN
            IF NEW.amount <= 10000000 AND NEW.amount + tksth <= 20000000 THEN
                NEW.security_level = 'B';
            ELSIF (NEW.amount <= 10000000 AND NEW.amount + tksth > 20000000 AND NEW.amount + daily_total <= 1500000000) OR
                  (NEW.amount > 10000000 AND NEW.amount <= 500000000 AND NEW.amount + daily_total <= 1500000000) THEN
                NEW.security_level = 'C';
            ELSIF (NEW.amount <= 10000000 AND NEW.amount + daily_total > 1500000000) OR
                  (NEW.amount > 10000000 AND NEW.amount <= 500000000 AND NEW.amount + daily_total > 1500000000) OR
                  (NEW.amount > 500000000) THEN
                NEW.security_level = 'D';
            END IF;

        -- Group I.4: International transfers
        ELSIF NEW.transaction_type = 'transfer_interbank_international' THEN
            IF NEW.amount <= 200000000 AND NEW.amount + daily_total <= 1000000000 THEN
                NEW.security_level = 'B';
            ELSE
                NEW.security_level = 'C';
            END IF;

        END IF;

    -- Organizational customers
    ELSIF customer_type = 'organization' THEN
        -- Group II.1: Inquiry
        IF NEW.transaction_type = 'inquiry' THEN
            NEW.security_level = 'A';

        -- Group II.2: Same-bank same-owner transfers
        ELSIF NEW.transaction_type = 'transfer_same_bank_same_owner' THEN
            NEW.security_level = 'A';

        -- Group II.3: Other domestic transfers, payments, and e-wallet operations
        ELSIF NEW.transaction_type IN ('transfer_same_bank_diff_owner', 'transfer_interbank_domestic',
                                      'payment_goods_services', 'ewallet_transfer', 'ewallet_topup',
                                      'ewallet_withdrawal') THEN
            IF NEW.amount <= 1000000000 AND NEW.amount + daily_total <= 10000000000 THEN
                NEW.security_level = 'B';
            ELSE
                NEW.security_level = 'C';
            END IF;

        -- Group II.4: International transfers
        ELSIF NEW.transaction_type = 'transfer_interbank_international' THEN
            IF NEW.amount <= 500000000 AND NEW.amount + daily_total <= 5000000000 THEN
                NEW.security_level = 'B';
            ELSE
                NEW.security_level = 'C';
            END IF;

        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_classify_transaction
BEFORE INSERT ON payment_transactions
FOR EACH ROW EXECUTE FUNCTION classify_transaction();


-- Trigger to update daily transaction summaries and check limits
CREATE OR REPLACE FUNCTION update_daily_summary()
RETURNS TRIGGER AS $$
DECLARE
    customer_type VARCHAR(20);
    has_strong_auth BOOLEAN;
    daily_total DECIMAL(15,2);
    daily_ab_total DECIMAL(15,2);
    transaction_group VARCHAR(10);
    is_trusted BOOLEAN;
    account_status VARCHAR(20);
    auth_failure_count INTEGER;
    required_level VARCHAR(1);
    high_value_count INTEGER;
    intl_transfer_count INTEGER;
    payment_count INTEGER;
BEGIN
    -- Error handling: Check for valid customer_id
    IF NEW.customer_id IS NULL THEN
        RAISE EXCEPTION 'Customer ID cannot be NULL for transaction %', NEW.transaction_id;
    END IF;

    -- Get customer type
    SELECT c.customer_type INTO customer_type
    FROM customers c
    WHERE c.customer_id = NEW.customer_id;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Customer % not found for transaction %', NEW.customer_id, NEW.transaction_id;
    END IF;

    -- Get account status
    SELECT ba.status INTO account_status
    FROM bank_accounts ba
    WHERE ba.account_id = NEW.from_account_id;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Account % not found for transaction %', NEW.from_account_id, NEW.transaction_id;
    END IF;

    -- Check if account is inactive or frozen
    IF account_status IN ('inactive', 'frozen') THEN
        INSERT INTO risk_alerts (
            alert_id, transaction_id, alert_type, alert_message, status, created_at, resolved_at
        ) VALUES (
            nextval('risk_alerts_alert_id_seq'),
            NEW.transaction_id,
            'inactive_account',
            format('Transaction %s from inactive or frozen account %s', NEW.transaction_id, NEW.from_account_id),
            CASE
                WHEN random() < 0.40 THEN 'open'
                WHEN random() < 0.70 THEN 'investigating'
                WHEN random() < 0.90 THEN 'resolved'
                ELSE 'false_positive'
            END,
            CURRENT_TIMESTAMP,
            CASE WHEN random() < 0.90 THEN NULL ELSE CURRENT_TIMESTAMP END
        );
        RAISE EXCEPTION 'Transaction %s not allowed from account %s with status %s', NEW.transaction_id, NEW.from_account_id, account_status;
    END IF;

    -- Get device trust status
    SELECT d.is_trusted INTO is_trusted
    FROM devices d
    WHERE d.device_id = NEW.device_id;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Device % not found for transaction %', NEW.device_id, NEW.transaction_id;
    END IF;

    -- Determine transaction group
    CASE NEW.transaction_type
        WHEN 'inquiry' THEN
            transaction_group := CASE WHEN customer_type = 'individual' THEN 'I.1' ELSE 'II.1' END;
        WHEN 'transfer_same_bank_same_owner' THEN
            transaction_group := CASE WHEN customer_type = 'individual' THEN 'I.1' ELSE 'II.2' END;
        WHEN 'payment_goods_services' THEN
            transaction_group := CASE WHEN customer_type = 'individual' THEN 'I.2' ELSE 'II.3' END;
        WHEN 'transfer_same_bank_diff_owner', 'transfer_interbank_domestic', 'ewallet_transfer', 'ewallet_topup', 'ewallet_withdrawal' THEN
            transaction_group := CASE WHEN customer_type = 'individual' THEN 'I.3' ELSE 'II.3' END;
        WHEN 'transfer_interbank_international' THEN
            transaction_group := CASE WHEN customer_type = 'individual' THEN 'I.4' ELSE 'II.4' END;
        ELSE
            transaction_group := 'unknown';
    END CASE;

    -- Determine required authentication level
    required_level := 'A';
    IF customer_type = 'individual' THEN
        IF transaction_group = 'I.2' THEN
            required_level := CASE
                WHEN NEW.amount > 1500000000 THEN 'D'
                WHEN NEW.amount > 100000000 THEN 'C'
                WHEN NEW.amount > 5000000 THEN 'B'
                ELSE 'A'
            END;
        ELSIF transaction_group = 'I.3' THEN
            required_level := CASE
                WHEN NEW.amount > 500000000 THEN 'D'
                WHEN NEW.amount > 10000000 THEN 'C'
                ELSE 'B'
            END;
        ELSIF transaction_group = 'I.4' THEN
            required_level := CASE
                WHEN NEW.amount > 200000000 THEN 'D'
                ELSE 'C'
            END;
        END IF;
    ELSE
        IF transaction_group = 'II.3' THEN
            required_level := CASE
                WHEN NEW.amount > 1000000000 THEN 'D'
                ELSE 'B'
            END;
        ELSIF transaction_group = 'II.4' THEN
            required_level := CASE
                WHEN NEW.amount > 500000000 THEN 'D'
                ELSE 'B'
            END;
        END IF;
    END IF;

    -- Check for strong authentication (C or D) on this transaction
    has_strong_auth := EXISTS (
        SELECT 1
        FROM authentication_logs al
        JOIN authentication_methods am ON al.auth_method_id = am.auth_id
        WHERE al.transaction_id = NEW.transaction_id
        AND am.security_level IN ('C', 'D')
        AND al.auth_result = 'success'
    );

    -- Check for authentication failures
    SELECT COUNT(*) INTO auth_failure_count
    FROM authentication_logs al
    WHERE al.transaction_id = NEW.transaction_id
    AND al.auth_result = 'failed';
    IF auth_failure_count > 0 THEN
        INSERT INTO risk_alerts (
            alert_id, transaction_id, alert_type, alert_message, status, created_at, resolved_at
        ) VALUES (
            nextval('risk_alerts_alert_id_seq'),
            NEW.transaction_id,
            'auth_failure',
            format('Authentication failure detected for transaction %s (%s failures)', NEW.transaction_id, auth_failure_count),
            CASE
                WHEN random() < 0.40 THEN 'open'
                WHEN random() < 0.70 THEN 'investigating'
                WHEN random() < 0.90 THEN 'resolved'
                ELSE 'false_positive'
            END,
            CURRENT_TIMESTAMP,
            CASE WHEN random() < 0.90 THEN NULL ELSE CURRENT_TIMESTAMP END
        );
    END IF;

    -- Check for high authentication failure rate in a day
    SELECT COUNT(*) INTO auth_failure_count
    FROM authentication_logs al
    JOIN payment_transactions pt ON al.transaction_id = pt.transaction_id
    WHERE pt.customer_id = NEW.customer_id
    AND pt.transaction_date::DATE = NEW.transaction_date::DATE
    AND al.auth_result = 'failed';
    IF auth_failure_count > 3 THEN
        INSERT INTO risk_alerts (
            alert_id, transaction_id, alert_type, alert_message, status, created_at, resolved_at
        ) VALUES (
            nextval('risk_alerts_alert_id_seq'),
            NEW.transaction_id,
            'auth_failure_rate',
            format('Customer %s has %s authentication failures on %s', NEW.customer_id, auth_failure_count, NEW.transaction_date::DATE),
            CASE
                WHEN random() < 0.40 THEN 'open'
                WHEN random() < 0.70 THEN 'investigating'
                WHEN random() < 0.90 THEN 'resolved'
                ELSE 'false_positive'
            END,
            CURRENT_TIMESTAMP,
            CASE WHEN random() < 0.90 THEN NULL ELSE CURRENT_TIMESTAMP END
        );
    END IF;

    -- Check for transactions > 10M VND without strong authentication
    IF NEW.amount > 10000000 AND NOT has_strong_auth THEN
        INSERT INTO risk_alerts (
            alert_id, transaction_id, alert_type, alert_message, status, created_at, resolved_at
        ) VALUES (
            nextval('risk_alerts_alert_id_seq'),
            NEW.transaction_id,
            'strong_auth_required',
            format('Transaction %s with amount %s VND used weak authentication (Level %s)', NEW.transaction_id, NEW.amount, NEW.security_level),
            CASE
                WHEN random() < 0.40 THEN 'open'
                WHEN random() < 0.70 THEN 'investigating'
                WHEN random() < 0.90 THEN 'resolved'
                ELSE 'false_positive'
            END,
            CURRENT_TIMESTAMP,
            CASE WHEN random() < 0.90 THEN NULL ELSE CURRENT_TIMESTAMP END
        );
    END IF;

    -- Check for untrusted device without strong authentication
    IF NOT is_trusted AND NOT has_strong_auth THEN
        INSERT INTO risk_alerts (
            alert_id, transaction_id, alert_type, alert_message, status, created_at, resolved_at
        ) VALUES (
            nextval('risk_alerts_alert_id_seq'),
            NEW.transaction_id,
            'untrusted_device',
            format('Transaction %s on untrusted device %s lacks strong authentication (C/D)', NEW.transaction_id, NEW.device_id),
            CASE
                WHEN random() < 0.40 THEN 'open'
                WHEN random() < 0.70 THEN 'investigating'
                WHEN random() < 0.90 THEN 'resolved'
                ELSE 'false_positive'
            END,
            CURRENT_TIMESTAMP,
            CASE WHEN random() < 0.90 THEN NULL ELSE CURRENT_TIMESTAMP END
        );
    END IF;

    -- Check for weak authentication
    IF NEW.security_level < required_level THEN
        INSERT INTO risk_alerts (
            alert_id, transaction_id, alert_type, alert_message, status, created_at, resolved_at
        ) VALUES (
            nextval('risk_alerts_alert_id_seq'),
            NEW.transaction_id,
            'weak_authentication',
            format('Weak authentication (Level %s) used for transaction %s requiring Level %s', NEW.security_level, NEW.transaction_id, required_level),
            CASE
                WHEN random() < 0.40 THEN 'open'
                WHEN random() < 0.70 THEN 'investigating'
                WHEN random() < 0.90 THEN 'resolved'
                ELSE 'false_positive'
            END,
            CURRENT_TIMESTAMP,
            CASE WHEN random() < 0.90 THEN NULL ELSE CURRENT_TIMESTAMP END
        );
    END IF;

    -- Check for high-value transaction
    IF (customer_type = 'individual' AND
        ((transaction_group = 'I.2' AND NEW.amount > 100000000) OR
         (transaction_group = 'I.3' AND (NEW.amount > 500000000 OR NEW.amount > 10000000)) OR
         (transaction_group = 'I.4' AND NEW.amount > 200000000))) OR
       (customer_type = 'organization' AND
        ((transaction_group = 'II.3' AND NEW.amount > 1000000000) OR
         (transaction_group = 'II.4' AND NEW.amount > 500000000))) THEN
        INSERT INTO risk_alerts (
            alert_id, transaction_id, alert_type, alert_message, status, created_at, resolved_at
        ) VALUES (
            nextval('risk_alerts_alert_id_seq'),
            NEW.transaction_id,
            'high_value_transaction',
            format('High-value transaction detected: %s VND for %s', NEW.amount, transaction_group),
            CASE
                WHEN random() < 0.40 THEN 'open'
                WHEN random() < 0.70 THEN 'investigating'
                WHEN random() < 0.90 THEN 'resolved'
                ELSE 'false_positive'
            END,
            CURRENT_TIMESTAMP,
            CASE WHEN random() < 0.90 THEN NULL ELSE CURRENT_TIMESTAMP END
        );
    END IF;

    -- Calculate daily totals and counts
    SELECT COALESCE(SUM(dts.total_amount), 0),
           COALESCE(SUM(dts.category_a_amount + dts.category_b_amount), 0),
           COUNT(*) FILTER (WHERE pt.amount > 100000000),
           COUNT(*) FILTER (WHERE pt.transaction_type = 'transfer_interbank_international'),
           COUNT(*) FILTER (WHERE pt.transaction_type = 'payment_goods_services')
    INTO daily_total, daily_ab_total, high_value_count, intl_transfer_count, payment_count
    FROM daily_transaction_summaries dts
    JOIN payment_transactions pt ON dts.account_id = pt.from_account_id
    WHERE dts.customer_id = NEW.customer_id
    AND dts.transaction_date = NEW.transaction_date::DATE
    AND pt.transaction_date::DATE = NEW.transaction_date::DATE;

    -- Adjust counts for the current transaction
    IF NEW.amount > 100000000 THEN
        high_value_count := high_value_count + 1;
    END IF;
    IF NEW.transaction_type = 'transfer_interbank_international' THEN
        intl_transfer_count := intl_transfer_count + 1;
    END IF;
    IF NEW.transaction_type = 'payment_goods_services' THEN
        payment_count := payment_count + 1;
    END IF;

    -- Check for unusual pattern (>3 high-value transactions)
    IF high_value_count > 3 THEN
        INSERT INTO risk_alerts (
            alert_id, transaction_id, alert_type, alert_message, status, created_at, resolved_at
        ) VALUES (
            nextval('risk_alerts_alert_id_seq'),
            NEW.transaction_id,
            'unusual_pattern',
            format('Unusual pattern: %s high-value transactions on %s', high_value_count, NEW.transaction_date::DATE),
            CASE
                WHEN random() < 0.40 THEN 'open'
                WHEN random() < 0.70 THEN 'investigating'
                WHEN random() < 0.90 THEN 'resolved'
                ELSE 'false_positive'
            END,
            CURRENT_TIMESTAMP,
            CASE WHEN random() < 0.90 THEN NULL ELSE CURRENT_TIMESTAMP END
        );
    END IF;

    -- Check for unusual cross-border frequency (organization-specific)
    IF customer_type = 'organization' AND intl_transfer_count > 3 THEN
        INSERT INTO risk_alerts (
            alert_id, transaction_id, alert_type, alert_message, status, created_at, resolved_at
        ) VALUES (
            nextval('risk_alerts_alert_id_seq'),
            NEW.transaction_id,
            'unusual_cross_border_frequency',
            format('Unusual frequency: %s international transfers on %s', intl_transfer_count, NEW.transaction_date::DATE),
            CASE
                WHEN random() < 0.40 THEN 'open'
                WHEN random() < 0.70 THEN 'investigating'
                WHEN random() < 0.90 THEN 'resolved'
                ELSE 'false_positive'
            END,
            CURRENT_TIMESTAMP,
            CASE WHEN random() < 0.90 THEN NULL ELSE CURRENT_TIMESTAMP END
        );
    END IF;

    -- Check for high payment volume (organization-specific)
    IF customer_type = 'organization' AND payment_count > 10 THEN
        INSERT INTO risk_alerts (
            alert_id, transaction_id, alert_type, alert_message, status, created_at, resolved_at
        ) VALUES (
            nextval('risk_alerts_alert_id_seq'),
            NEW.transaction_id,
            'high_payment_volume',
            format('High volume: %s payment transactions on %s', payment_count, NEW.transaction_date::DATE),
            CASE
                WHEN random() < 0.40 THEN 'open'
                WHEN random() < 0.70 THEN 'investigating'
                WHEN random() < 0.90 THEN 'resolved'
                ELSE 'false_positive'
            END,
            CURRENT_TIMESTAMP,
            CASE WHEN random() < 0.90 THEN NULL ELSE CURRENT_TIMESTAMP END
        );
    END IF;

    -- Check for daily total > 20M VND without strong authentication
    IF daily_total + NEW.amount > 20000000 AND NOT has_strong_auth AND NOT EXISTS (
        SELECT 1
        FROM payment_transactions pt
        JOIN authentication_logs al ON pt.transaction_id = al.transaction_id
        JOIN authentication_methods am ON al.auth_method_id = am.auth_id
        WHERE pt.customer_id = NEW.customer_id
        AND pt.transaction_date::DATE = NEW.transaction_date::DATE
        AND pt.transaction_id != NEW.transaction_id
        AND am.security_level IN ('C', 'D')
        AND al.auth_result = 'success'
    ) THEN
        INSERT INTO risk_alerts (
            alert_id, transaction_id, alert_type, alert_message, status, created_at, resolved_at
        ) VALUES (
            nextval('risk_alerts_alert_id_seq'),
            NEW.transaction_id,
            'daily_limit_strong_auth',
            format('Customer %s on %s has total amount %s VND without strong authentication', NEW.customer_id, NEW.transaction_date::DATE, daily_total + NEW.amount),
            CASE
                WHEN random() < 0.40 THEN 'open'
                WHEN random() < 0.70 THEN 'investigating'
                WHEN random() < 0.90 THEN 'resolved'
                ELSE 'false_positive'
            END,
            CURRENT_TIMESTAMP,
            CASE WHEN random() < 0.90 THEN NULL ELSE CURRENT_TIMESTAMP END
        );
    END IF;

    -- Reset Tksth to 0 if strong authentication was used
    IF has_strong_auth THEN
        daily_ab_total := 0;
    END IF;

    -- Update daily transaction summaries
    INSERT INTO daily_transaction_summaries (
        summary_id, account_id, customer_id, transaction_date,
        total_amount, category_a_amount, category_b_amount,
        category_c_amount, category_d_amount, strong_auth_used
    )
    VALUES (
        nextval('daily_transaction_summaries_summary_id_seq'),
        NEW.from_account_id, NEW.customer_id, NEW.transaction_date::DATE,
        NEW.amount,
        CASE WHEN NEW.security_level = 'A' THEN NEW.amount ELSE 0 END,
        CASE WHEN NEW.security_level = 'B' THEN NEW.amount ELSE 0 END,
        CASE WHEN NEW.security_level = 'C' THEN NEW.amount ELSE 0 END,
        CASE WHEN NEW.security_level = 'D' THEN NEW.amount ELSE 0 END,
        has_strong_auth
    )
    ON CONFLICT (account_id, transaction_date)
    DO UPDATE SET
        total_amount = daily_transaction_summaries.total_amount + EXCLUDED.total_amount,
        category_a_amount = daily_transaction_summaries.category_a_amount + EXCLUDED.category_a_amount,
        category_b_amount = daily_transaction_summaries.category_b_amount + EXCLUDED.category_b_amount,
        category_c_amount = daily_transaction_summaries.category_c_amount + EXCLUDED.category_c_amount,
        category_d_amount = daily_transaction_summaries.category_d_amount + EXCLUDED.category_d_amount,
        strong_auth_used = daily_transaction_summaries.strong_auth_used OR EXCLUDED.strong_auth_used,
        updated_at = CURRENT_TIMESTAMP;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create the trigger
CREATE TRIGGER trigger_update_daily_summary
AFTER INSERT ON payment_transactions
FOR EACH ROW EXECUTE FUNCTION update_daily_summary();
