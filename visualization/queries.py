class SQLQueries:
    """
    A class to store all SQL queries used in the dashboard.
    NOTE: Queries have been updated to fix errors related to ambiguous columns and missing table joins.
    """
    # --- KPI Queries ---
    TOTAL_CUSTOMERS = "SELECT COUNT(*) FROM customers WHERE status = 'active';"
    TOTAL_OPEN_RISK_ALERTS = "SELECT COUNT(*) FROM risk_alerts WHERE status = 'open';"

    TOTAL_TRANSACTIONS = """
        SELECT COUNT(*)
        FROM payment_transactions pt
        JOIN customers c ON pt.customer_id = c.customer_id
        WHERE pt.transaction_date::DATE BETWEEN :start_date AND :end_date
        AND c.customer_type IN :customer_segments
        AND pt.transaction_type IN :transaction_types
        AND pt.status IN :transaction_statuses
        AND pt.security_level IN :security_levels; -- Add security_level filter
    """
    TOTAL_TRANSACTION_AMOUNT = """
        SELECT COALESCE(SUM(pt.amount), 0)
        FROM payment_transactions pt
        JOIN customers c ON pt.customer_id = c.customer_id
        WHERE pt.transaction_date::DATE BETWEEN :start_date AND :end_date
        AND c.customer_type IN :customer_segments
        AND pt.transaction_type IN :transaction_types
        AND pt.status IN :transaction_statuses
        AND pt.security_level IN :security_levels; -- Add security_level filter
    """
    ACTIVE_CUSTOMERS_PERIOD = """
        SELECT COUNT(DISTINCT pt.customer_id)
        FROM payment_transactions AS pt
        JOIN customers AS c ON pt.customer_id = c.customer_id
        WHERE pt.transaction_date::DATE BETWEEN :start_date AND :end_date
          AND c.customer_type IN :customer_segments
          AND pt.transaction_type IN :transaction_types
          AND pt.status IN :transaction_statuses
          AND pt.security_level IN :security_levels; -- Add security_level filter
    """
    SUSPICIOUS_TRANSACTION_AMOUNT = """
        SELECT COALESCE(SUM(pt.amount), 0)
        FROM payment_transactions AS pt
        JOIN customers AS c ON pt.customer_id = c.customer_id
        WHERE pt.is_suspicious = TRUE
          AND pt.transaction_date::DATE BETWEEN :start_date AND :end_date
          AND c.customer_type IN :customer_segments
          AND pt.transaction_type IN :transaction_types
          AND pt.security_level IN :security_levels; -- Add security_level filter
    """
    AUTHENTICATION_SUCCESS_RATE = """
        SELECT
            COALESCE(
                CAST(COUNT(CASE WHEN al.auth_result = 'success' THEN 1 END) AS DECIMAL) * 100.0 / NULLIF(COUNT(al.log_id), 0),
            0)
        FROM authentication_logs al
        JOIN payment_transactions pt ON al.transaction_id = pt.transaction_id
        JOIN customers c ON pt.customer_id = c.customer_id
        WHERE pt.transaction_date::DATE BETWEEN :start_date AND :end_date
        AND c.customer_type IN :customer_segments
        AND pt.transaction_type IN :transaction_types
        AND pt.security_level IN :security_levels; -- Add security_level filter
    """

    # --- Chart & Table Queries ---
    DAILY_TRANSACTION_TREND = """
        SELECT
            transaction_date::DATE AS transaction_day,
            COUNT(*) AS daily_transaction_count,
            SUM(amount) AS daily_transaction_amount
        FROM payment_transactions pt
        JOIN customers c ON pt.customer_id = c.customer_id
        WHERE pt.transaction_date::DATE BETWEEN :start_date AND :end_date
        AND c.customer_type IN :customer_segments
        AND pt.transaction_type IN :transaction_types
        AND pt.status IN :transaction_statuses
        AND pt.security_level IN :security_levels -- Add security_level filter
        GROUP BY transaction_day
        ORDER BY transaction_day;
    """
    TRANSACTION_VOLUME_BY_TYPE = """
        SELECT transaction_type, COUNT(*) as count
        FROM payment_transactions pt
        JOIN customers c ON pt.customer_id = c.customer_id
        WHERE pt.transaction_date::DATE BETWEEN :start_date AND :end_date
        AND c.customer_type IN :customer_segments
        AND pt.transaction_type IN :transaction_types
        AND pt.security_level IN :security_levels -- Add security_level filter
        GROUP BY transaction_type;
    """
    TRANSACTION_STATUS_DISTRIBUTION = """
        SELECT pt.status, COUNT(*) as count
        FROM payment_transactions pt
        JOIN customers c ON pt.customer_id = c.customer_id
        WHERE pt.transaction_date::DATE BETWEEN :start_date AND :end_date
        AND c.customer_type IN :customer_segments
        AND pt.transaction_type IN :transaction_types
        AND pt.status IN :transaction_statuses
        AND pt.security_level IN :security_levels -- Add security_level filter
        GROUP BY pt.status;
    """
    CUSTOMER_TYPE_DISTRIBUTION = """
        SELECT c.customer_type, COUNT(DISTINCT c.customer_id) as count
        FROM customers c
        JOIN payment_transactions pt ON c.customer_id = pt.customer_id
        WHERE pt.transaction_date::DATE BETWEEN :start_date AND :end_date
        AND c.customer_type IN :customer_segments
        AND pt.security_level IN :security_levels -- Add security_level filter
        GROUP BY c.customer_type;
    """
    DEVICE_TYPE_DISTRIBUTION = """
        SELECT d.device_type, COUNT(DISTINCT d.device_id) as count
        FROM devices d
        JOIN customers c ON d.customer_id = c.customer_id
        WHERE c.customer_type IN :customer_segments
        GROUP BY d.device_type;
    """
    TRUSTED_VS_UNTRUSTED_DEVICES = """
        SELECT d.is_trusted, COUNT(d.device_id) as count
        FROM devices d
        JOIN customers c ON d.customer_id = c.customer_id
        WHERE c.customer_type IN :customer_segments
        GROUP BY d.is_trusted;
    """
    AUTH_METHOD_ANALYSIS = """
        SELECT
            am.method_name,
            am.security_level,
            COUNT(al.log_id) AS total_attempts,
            ROUND(
                (COUNT(al.log_id) FILTER (WHERE al.auth_result = 'success')::DECIMAL /
                 NULLIF(COUNT(al.log_id), 0) * 100),
                2
            ) AS success_rate
        FROM
            authentication_methods am
        LEFT JOIN authentication_logs al ON am.auth_id = al.auth_method_id
        JOIN payment_transactions pt ON al.transaction_id = pt.transaction_id
        JOIN customers c ON pt.customer_id = c.customer_id
        WHERE pt.transaction_date::DATE BETWEEN :start_date AND :end_date
          AND pt.transaction_type IN :transaction_types
          AND c.customer_type IN :customer_segments
          AND pt.security_level IN :security_levels -- Add security_level filter
        GROUP BY
            am.method_name, am.security_level
        ORDER BY
            total_attempts DESC;
    """
    AUTH_RESULT_BREAKDOWN = """
        SELECT auth_result, COUNT(*) AS count
        FROM authentication_logs al
        JOIN payment_transactions pt ON al.transaction_id = pt.transaction_id
        JOIN customers c ON pt.customer_id = c.customer_id
        WHERE pt.transaction_date::DATE BETWEEN :start_date AND :end_date
        AND pt.transaction_type IN :transaction_types
        AND al.auth_result IN :auth_results
        AND c.customer_type IN :customer_segments
        AND pt.security_level IN :security_levels -- Add security_level filter
        GROUP BY auth_result;
    """
    RISK_ALERT_TYPES_DISTRIBUTION = """
        SELECT alert_type, COUNT(*) as count
        FROM risk_alerts ra
        JOIN payment_transactions pt ON ra.transaction_id = pt.transaction_id
        JOIN customers c ON pt.customer_id = c.customer_id
        WHERE pt.transaction_date::DATE BETWEEN :start_date AND :end_date
        AND pt.transaction_type IN :transaction_types
        AND ra.status IN :alert_statuses
        AND c.customer_type IN :customer_segments
        AND pt.security_level IN :security_levels -- Add security_level filter
        GROUP BY alert_type;
    """
    RECENT_RISKY_TRANSACTIONS = """
        SELECT
            pt.transaction_id, c.full_name, pt.amount, pt.transaction_type,
            pt.transaction_date, ra.alert_type
        FROM payment_transactions pt
        JOIN customers c ON pt.customer_id = c.customer_id
        LEFT JOIN risk_alerts ra ON pt.transaction_id = ra.transaction_id
        WHERE pt.is_suspicious = TRUE
        AND pt.transaction_date::DATE BETWEEN :start_date AND :end_date
        AND pt.transaction_type IN :transaction_types
        AND c.customer_type IN :customer_segments
        AND pt.security_level IN :security_levels -- Add security_level filter
        ORDER BY pt.transaction_date DESC
        LIMIT 20;
    """
    TRANSACTION_HEATMAP = """
        SELECT
            EXTRACT(ISODOW FROM transaction_date) AS day_of_week,
            EXTRACT(HOUR FROM transaction_date) AS hour_of_day,
            COUNT(transaction_id) AS transaction_count
        FROM payment_transactions pt
        JOIN customers c ON pt.customer_id = c.customer_id
        WHERE pt.transaction_date::DATE BETWEEN :start_date AND :end_date
          AND c.customer_type IN :customer_segments
          AND pt.transaction_type IN :transaction_types
          AND pt.status IN :transaction_statuses
          AND pt.security_level IN :security_levels -- Add security_level filter
        GROUP BY day_of_week, hour_of_day
        ORDER BY day_of_week, hour_of_day;
    """
    TRANSACTION_FUNNEL = """
        WITH filtered_transactions AS (
            SELECT pt.transaction_id FROM payment_transactions pt
            JOIN customers c ON pt.customer_id = c.customer_id
            WHERE pt.transaction_date::DATE BETWEEN :start_date AND :end_date
              AND c.customer_type IN :customer_segments
              AND pt.transaction_type IN :transaction_types
              AND pt.status IN :transaction_statuses
              AND pt.security_level IN :security_levels -- Add security_level filter
        )
        SELECT '1. Initiated' as stage, COUNT(*) as value FROM filtered_transactions
        UNION ALL
        SELECT '2. Authenticated' as stage, COUNT(DISTINCT al.transaction_id) as value
        FROM authentication_logs al
        WHERE al.transaction_id IN (SELECT transaction_id FROM filtered_transactions) AND al.auth_result = 'success'
        UNION ALL
        SELECT '3. Completed' as stage, COUNT(pt.transaction_id) as value
        FROM payment_transactions pt
        WHERE pt.transaction_id IN (SELECT transaction_id FROM filtered_transactions) AND pt.status = 'completed';
    """
    HIGH_VALUE_TRANSACTION_REPORT = """
        SELECT
            pt.transaction_id, pt.transaction_type, pt.amount, pt.security_level,
            pt.transaction_date, pt.status AS transaction_status, c.full_name, c.customer_type
        FROM payment_transactions pt
        JOIN customers c ON pt.customer_id = c.customer_id
        WHERE pt.transaction_date::DATE BETWEEN :start_date AND :end_date
        AND c.customer_type IN :customer_segments
        AND pt.transaction_type IN :transaction_types
        AND pt.security_level IN :security_levels -- Add security_level filter
        AND (
            (c.customer_type = 'individual' AND pt.amount > 100000000) OR
            (c.customer_type = 'organization' AND pt.amount > 1000000000)
        )
        ORDER BY pt.amount DESC;
    """
    AUTHENTICATION_FAILURE_REPORT = """
        SELECT
            al.log_id, al.failure_reason, al.auth_timestamp, am.method_name,
            pt.transaction_id, pt.amount, c.full_name, d.device_type, d.is_trusted
        FROM authentication_logs al
        JOIN authentication_methods am ON al.auth_method_id = am.auth_id
        JOIN payment_transactions pt ON al.transaction_id = pt.transaction_id
        JOIN customers c ON pt.customer_id = c.customer_id
        JOIN devices d ON pt.device_id = d.device_id
        WHERE al.auth_result = 'failed'
        AND al.auth_timestamp::DATE BETWEEN :start_date AND :end_date
        AND c.customer_type IN :customer_segments
        AND pt.security_level IN :security_levels -- Add security_level filter
        ORDER BY al.auth_timestamp DESC;
    """

    # New queries for Customer Behavior tab
    AVG_TRANSACTION_VALUE_BY_CUSTOMER_TYPE = """
        SELECT c.customer_type, AVG(pt.amount) AS avg_amount
        FROM payment_transactions pt
        JOIN customers c ON pt.customer_id = c.customer_id
        WHERE pt.transaction_date::DATE BETWEEN :start_date AND :end_date
        AND c.customer_type IN :customer_segments
        AND pt.transaction_type IN :transaction_types
        AND pt.status IN :transaction_statuses
        AND pt.security_level IN :security_levels
        GROUP BY c.customer_type;
    """  #

    TRANSACTION_COUNT_BY_CUSTOMER_TYPE = """
        SELECT c.customer_type, COUNT(pt.transaction_id) AS transaction_count
        FROM payment_transactions pt
        JOIN customers c ON pt.customer_id = c.customer_id
        WHERE pt.transaction_date::DATE BETWEEN :start_date AND :end_date
        AND c.customer_type IN :customer_segments
        AND pt.transaction_type IN :transaction_types
        AND pt.status IN :transaction_statuses
        AND pt.security_level IN :security_levels
        GROUP BY c.customer_type;
    """  #

    TOP_ACTIVE_CUSTOMERS = """
        SELECT c.full_name, c.customer_type, COUNT(pt.transaction_id) AS transaction_count, SUM(pt.amount) AS total_transaction_amount
        FROM payment_transactions pt
        JOIN customers c ON pt.customer_id = c.customer_id
        WHERE pt.transaction_date::DATE BETWEEN :start_date AND :end_date
        AND c.customer_type IN :customer_segments
        AND pt.transaction_type IN :transaction_types
        AND pt.status IN :transaction_statuses
        AND pt.security_level IN :security_levels
        GROUP BY c.customer_id, c.full_name, c.customer_type
        ORDER BY transaction_count DESC
        LIMIT 10;
    """  #

    TRANSACTION_FREQUENCY_BY_HOUR = """
        SELECT
            TO_CHAR(transaction_date, 'Day') AS day_of_week,
            EXTRACT(HOUR FROM transaction_date) AS hour_of_day,
            COUNT(*) AS transaction_count
        FROM payment_transactions
        WHERE transaction_date::DATE BETWEEN :start_date AND :end_date
        AND security_level IN :security_levels
        GROUP BY 1, 2
        ORDER BY 1, 2;
    """  #

    # Query for Funnel Chart by Security Level
    TRANSACTION_COUNT_BY_SECURITY_LEVEL = """
        SELECT
            pt.security_level,
            COUNT(pt.transaction_id) AS transaction_count
        FROM payment_transactions pt
        JOIN customers c ON pt.customer_id = c.customer_id
        WHERE pt.transaction_date::DATE BETWEEN :start_date AND :end_date
        AND c.customer_type IN :customer_segments
        AND pt.transaction_type IN :transaction_types
        AND pt.status IN :transaction_statuses
        GROUP BY pt.security_level
        ORDER BY pt.security_level;
    """  #
