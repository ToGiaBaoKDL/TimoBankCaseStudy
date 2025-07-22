-- 1. Customer Overview Report
-- Provides a comprehensive summary of customer details, their accounts, and registered devices
SELECT 
    c.customer_id,
    c.customer_type,
    c.full_name,
    c.cccd_number,
    c.tax_code,
    c.phone_number,
    c.email,
    c.registration_date,
    c.status AS customer_status,
    COUNT(DISTINCT ba.account_id) AS total_accounts,
    COALESCE(SUM(ba.balance), 0) AS total_balance,
    COUNT(DISTINCT d.device_id) AS total_devices,
    STRING_AGG(DISTINCT d.device_type, ', ') AS device_types
FROM 
    customers c
    LEFT JOIN bank_accounts ba ON c.customer_id = ba.customer_id
    LEFT JOIN devices d ON c.customer_id = d.customer_id
WHERE 
    c.status = 'active'
GROUP BY 
    c.customer_id,
    c.customer_type,
    c.full_name,
    c.cccd_number,
    c.tax_code,
    c.phone_number,
    c.email,
    c.registration_date,
    c.status
HAVING 
    COUNT(DISTINCT ba.account_id) > 0
ORDER BY 
    c.registration_date DESC;

-- 2. Transaction Summary Report
-- Summarizes transactions by customer and date range with security level breakdown
SELECT 
    c.customer_id,
    c.full_name,
    c.customer_type,
    dts.transaction_date,
    COUNT(pt.transaction_id) AS transaction_count,
    COALESCE(SUM(pt.amount), 0) AS total_transaction_amount,
    COUNT(pt.transaction_id) FILTER (WHERE pt.security_level = 'A') AS level_a_transactions,
    COUNT(pt.transaction_id) FILTER (WHERE pt.security_level = 'B') AS level_b_transactions,
    COUNT(pt.transaction_id) FILTER (WHERE pt.security_level = 'C') AS level_c_transactions,
    COUNT(pt.transaction_id) FILTER (WHERE pt.security_level = 'D') AS level_d_transactions,
    COUNT(pt.transaction_id) FILTER (WHERE pt.status = 'completed') AS completed_transactions,
    COUNT(pt.transaction_id) FILTER (WHERE pt.status = 'failed') AS failed_transactions
FROM 
    customers c
    JOIN daily_transaction_summaries dts ON c.customer_id = dts.customer_id
    JOIN payment_transactions pt ON dts.account_id = pt.from_account_id 
        AND dts.transaction_date = pt.transaction_date::DATE
WHERE 
    dts.transaction_date BETWEEN CURRENT_DATE - INTERVAL '30 days' AND CURRENT_DATE
GROUP BY 
    c.customer_id,
    c.full_name,
    c.customer_type,
    dts.transaction_date
ORDER BY 
    dts.transaction_date DESC, 
    c.customer_id;

-- 3. Risk Alerts Analysis
-- Detailed analysis of risk alerts by type and status with transaction details
SELECT 
    ra.alert_id,
    ra.alert_type,
    ra.alert_message,
    ra.status AS alert_status,
    ra.created_at AS alert_created_at,
    pt.transaction_id,
    pt.transaction_type,
    pt.amount,
    pt.security_level,
    c.full_name,
    c.customer_type,
    d.device_type,
    d.is_trusted,
    STRING_AGG(am.method_name, ', ') AS auth_methods_used
FROM 
    risk_alerts ra
    JOIN payment_transactions pt ON ra.transaction_id = pt.transaction_id
    JOIN customers c ON pt.customer_id = c.customer_id
    JOIN devices d ON pt.device_id = d.device_id
    LEFT JOIN authentication_logs al ON pt.transaction_id = al.transaction_id
    LEFT JOIN authentication_methods am ON al.auth_method_id = am.auth_id
WHERE 
    ra.created_at >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY 
    ra.alert_id,
    ra.alert_type,
    ra.alert_message,
    ra.status,
    ra.created_at,
    pt.transaction_id,
    pt.transaction_type,
    pt.amount,
    pt.security_level,
    c.full_name,
    c.customer_type,
    d.device_type,
    d.is_trusted
ORDER BY 
    ra.created_at DESC;

-- 4. Authentication Failure Report
-- Analyzes authentication failures with reasons and associated transactions
SELECT 
    al.log_id,
    al.auth_result,
    al.failure_reason,
    al.auth_timestamp,
    am.method_name,
    am.security_level,
    pt.transaction_id,
    pt.transaction_type,
    pt.amount,
    c.full_name,
    c.customer_type,
    d.device_type,
    d.device_identifier,
    d.is_trusted
FROM 
    authentication_logs al
    JOIN authentication_methods am ON al.auth_method_id = am.auth_id
    JOIN payment_transactions pt ON al.transaction_id = pt.transaction_id
    JOIN customers c ON pt.customer_id = c.customer_id
    JOIN devices d ON pt.device_id = d.device_id
WHERE 
    al.auth_result = 'failed'
    AND al.auth_timestamp >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY 
    al.auth_timestamp DESC;

-- 5. High-Value Transaction Report
-- Lists transactions exceeding specified thresholds by customer type
SELECT 
    pt.transaction_id,
    pt.transaction_type,
    pt.amount,
    pt.security_level,
    pt.transaction_date,
    pt.status AS transaction_status,
    c.full_name,
    c.customer_type,
    ba.account_number,
    d.device_type,
    d.is_trusted,
    CASE 
        WHEN c.customer_type = 'individual' THEN 
            CASE 
                WHEN pt.transaction_type = 'payment_goods_services' AND pt.amount > 100000000 THEN 'High'
                WHEN pt.transaction_type IN ('transfer_same_bank_diff_owner', 'transfer_interbank_domestic', 
                    'ewallet_transfer', 'ewallet_topup', 'ewallet_withdrawal') AND pt.amount > 500000000 THEN 'High'
                WHEN pt.transaction_type = 'transfer_interbank_international' AND pt.amount > 200000000 THEN 'High'
                ELSE 'Normal'
            END
        WHEN c.customer_type = 'organization' THEN 
            CASE 
                WHEN pt.transaction_type IN ('transfer_same_bank_diff_owner', 'transfer_interbank_domestic', 
                    'payment_goods_services', 'ewallet_transfer', 'ewallet_topup', 'ewallet_withdrawal') 
                    AND pt.amount > 1000000000 THEN 'High'
                WHEN pt.transaction_type = 'transfer_interbank_international' AND pt.amount > 500000000 THEN 'High'
                ELSE 'Normal'
            END
    END AS value_category
FROM 
    payment_transactions pt
    JOIN customers c ON pt.customer_id = c.customer_id
    JOIN bank_accounts ba ON pt.from_account_id = ba.account_id
    JOIN devices d ON pt.device_id = d.device_id
WHERE 
    pt.transaction_date >= CURRENT_DATE - INTERVAL '30 days'
    AND (
        (c.customer_type = 'individual' AND (
            (pt.transaction_type = 'payment_goods_services' AND pt.amount > 100000000) OR
            (pt.transaction_type IN ('transfer_same_bank_diff_owner', 'transfer_interbank_domestic', 
                'ewallet_transfer', 'ewallet_topup', 'ewallet_withdrawal') AND pt.amount > 500000000) OR
            (pt.transaction_type = 'transfer_interbank_international' AND pt.amount > 200000000)
        )) OR
        (c.customer_type = 'organization' AND (
            (pt.transaction_type IN ('transfer_same_bank_diff_owner', 'transfer_interbank_domestic', 
                'payment_goods_services', 'ewallet_transfer', 'ewallet_topup', 'ewallet_withdrawal') 
                AND pt.amount > 1000000000) OR
            (pt.transaction_type = 'transfer_interbank_international' AND pt.amount > 500000000)
        ))
    )
ORDER BY 
    pt.amount DESC;

-- 6. Daily Transaction Limit Monitoring
-- Monitors daily transaction limits and strong authentication usage
SELECT 
    dts.summary_id,
    dts.transaction_date,
    c.full_name,
    c.customer_type,
    ba.account_number,
    dts.total_amount,
    dts.category_a_amount,
    dts.category_b_amount,
    dts.category_c_amount,
    dts.category_d_amount,
    dts.strong_auth_used,
    CASE 
        WHEN c.customer_type = 'individual' AND dts.total_amount > 1500000000 THEN 'Above Limit'
        WHEN c.customer_type = 'organization' AND dts.total_amount > 10000000000 THEN 'Above Limit'
        ELSE 'Within Limit'
    END AS limit_status
FROM 
    daily_transaction_summaries dts
    JOIN customers c ON dts.customer_id = c.customer_id
    JOIN bank_accounts ba ON dts.account_id = ba.account_id
WHERE 
    dts.transaction_date = CURRENT_DATE
    AND (
        (c.customer_type = 'individual' AND dts.total_amount > 1500000000) OR
        (c.customer_type = 'organization' AND dts.total_amount > 10000000000)
    )
ORDER BY 
    dts.total_amount DESC;

-- 7. Device Usage Report
-- Summarizes device usage patterns and trust status
SELECT 
    c.customer_id,
    c.full_name,
    c.customer_type,
    d.device_id,
    d.device_type,
    d.device_identifier,
    d.os_info,
    d.is_trusted,
    d.first_seen,
    d.last_seen,
    COUNT(pt.transaction_id) AS transaction_count,
    COALESCE(SUM(pt.amount), 0) AS total_transaction_amount
FROM 
    customers c
    JOIN devices d ON c.customer_id = d.customer_id
    LEFT JOIN payment_transactions pt ON d.device_id = pt.device_id
WHERE 
    d.last_seen >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY 
    c.customer_id,
    c.full_name,
    c.customer_type,
    d.device_id,
    d.device_type,
    d.device_identifier,
    d.os_info,
    d.is_trusted,
    d.first_seen,
    d.last_seen
ORDER BY 
    d.last_seen DESC;

-- 8. Interbank Transaction Analysis
-- Analyzes transactions involving other banks
SELECT 
    pt.transaction_id,
    pt.transaction_type,
    pt.amount,
    pt.transaction_date,
    pt.status,
    c.full_name AS from_customer,
    c.customer_type,
    ba.account_number AS from_account,
    oba.account_number AS to_account,
    obc.full_name AS to_customer,
    b.bank_name AS to_bank,
    b.is_domestic
FROM 
    payment_transactions pt
    JOIN customers c ON pt.customer_id = c.customer_id
    JOIN bank_accounts ba ON pt.from_account_id = ba.account_id
    LEFT JOIN other_banks_accounts oba ON pt.to_account_external_id = oba.account_id
    LEFT JOIN other_banks_customers obc ON oba.customer_id = obc.customer_id
    LEFT JOIN banks b ON obc.bank_id = b.bank_id
WHERE 
    pt.transaction_type IN ('transfer_interbank_domestic', 'transfer_interbank_international')
    AND pt.transaction_date >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY 
    pt.transaction_date DESC;

-- 9. Authentication Method Usage Report
-- Shows usage statistics for different authentication methods
SELECT 
    am.method_type,
    am.method_name,
    am.security_level,
    COUNT(al.log_id) AS total_attempts,
    COUNT(al.log_id) FILTER (WHERE al.auth_result = 'success') AS successful_attempts,
    COUNT(al.log_id) FILTER (WHERE al.auth_result = 'failed') AS failed_attempts,
    ROUND(
        (COUNT(al.log_id) FILTER (WHERE al.auth_result = 'success')::FLOAT / 
         NULLIF(COUNT(al.log_id), 0) * 100)::NUMERIC, 
        2
    ) AS success_rate
FROM 
    authentication_methods am
    LEFT JOIN authentication_logs al ON am.auth_id = al.auth_method_id
WHERE 
    al.auth_timestamp >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY 
    am.method_type,
    am.method_name,
    am.security_level
ORDER BY 
    total_attempts DESC;

-- 10. Account Activity Report
-- Summarizes account activity including balances and transaction volumes
SELECT 
    ba.account_id,
    ba.account_number,
    ba.account_type,
    ba.balance,
    ba.status AS account_status,
    c.full_name,
    c.customer_type,
    COUNT(pt.transaction_id) AS total_transactions,
    COALESCE(SUM(pt.amount) FILTER (WHERE pt.status = 'completed'), 0) AS total_completed_amount,
    COUNT(pt.transaction_id) FILTER (WHERE pt.status = 'failed') AS failed_transactions,
    MAX(pt.transaction_date) AS last_transaction_date
FROM 
    bank_accounts ba
    JOIN customers c ON ba.customer_id = c.customer_id
    LEFT JOIN payment_transactions pt ON ba.account_id = pt.from_account_id
WHERE 
    pt.transaction_date >= CURRENT_DATE - INTERVAL '30 days'
    OR pt.transaction_date IS NULL
GROUP BY 
    ba.account_id,
    ba.account_number,
    ba.account_type,
    ba.balance,
    ba.status,
    c.full_name,
    c.customer_type
ORDER BY 
    ba.balance DESC;