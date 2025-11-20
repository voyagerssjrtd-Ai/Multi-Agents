CREATE TABLE IF NOT EXISTS sales_history (
    sale_date DATE,
    sku TEXT,
    qty INTEGER
);

-- Materialized view for fast aggregation
CREATE TABLE IF NOT EXISTS aggregated_sales AS
SELECT
    sku,
    DATE_TRUNC('day', sale_date) AS day,
    SUM(qty) AS daily_qty
FROM sales_history
GROUP BY sku, day;

-- Feature view for ML time series (used by ARIMA/LSTM)
CREATE TABLE IF NOT EXISTS sku_features AS
SELECT
    sku,
    day,
    daily_qty,
    AVG(daily_qty) OVER (PARTITION BY sku ORDER BY day ROWS 7 PRECEDING) AS rolling_7d,
    SUM(daily_qty) OVER (PARTITION BY sku ORDER BY day ROWS 30 PRECEDING) AS rolling_30d,
    LAG(daily_qty, 1) OVER (PARTITION BY sku ORDER BY day) AS prev_day_sales
FROM aggregated_sales;
