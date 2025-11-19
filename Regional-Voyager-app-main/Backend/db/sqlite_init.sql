PRAGMA journal_mode=WAL;

-- 1. Product catalog
CREATE TABLE IF NOT EXISTS products (
    sku TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT,
    unit TEXT DEFAULT 'pcs',
    safety_stock INTEGER DEFAULT 0,
    reorder_point INTEGER DEFAULT 0,
    lead_time_days INTEGER DEFAULT 7,
    metadata JSON
);

-- 2. Current stock levels (Fast OLTP table)
CREATE TABLE IF NOT EXISTS inventory (
    sku TEXT PRIMARY KEY,
    qty INTEGER NOT NULL DEFAULT 0,
    reserved INTEGER NOT NULL DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sku) REFERENCES products(sku)
);

-- 3. Real-time sales log
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sku TEXT NOT NULL,
    qty INTEGER NOT NULL,
    sale_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sku) REFERENCES products(sku)
);

-- 4. Supplier info
CREATE TABLE IF NOT EXISTS suppliers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    lead_time_days INTEGER DEFAULT 7,
    rating REAL DEFAULT 5.0
);

-- 5. Forecast data (written by forecasting engine)
CREATE TABLE IF NOT EXISTS sku_forecasts (
    sku TEXT PRIMARY KEY,
    forecast_qty INTEGER,
    expected_stockout_date TEXT,
    recommended_order_qty INTEGER,
    model_used TEXT,
    model_confidence REAL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. Audit log (for governance & traceability)
CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user TEXT,
    action TEXT,
    sku TEXT,
    payload JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
