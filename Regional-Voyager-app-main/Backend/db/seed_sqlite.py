import sqlite3
import datetime

DB_PATH = "db/inventory.db"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

print("Seeding database with correct schema...")

# -------- Create Schema --------
cur.executescript("""
PRAGMA journal_mode=WAL;

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

CREATE TABLE IF NOT EXISTS inventory (
    sku TEXT PRIMARY KEY,
    qty INTEGER NOT NULL DEFAULT 0,
    reserved INTEGER NOT NULL DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sku) REFERENCES products(sku)
);

CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sku TEXT NOT NULL,
    qty INTEGER NOT NULL,
    sale_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sku) REFERENCES products(sku)
);

CREATE TABLE IF NOT EXISTS suppliers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    lead_time_days INTEGER DEFAULT 7,
    rating REAL DEFAULT 5.0
);

CREATE TABLE IF NOT EXISTS sku_forecasts (
    sku TEXT PRIMARY KEY,
    forecast_qty INTEGER,
    expected_stockout_date TEXT,
    recommended_order_qty INTEGER,
    model_used TEXT,
    model_confidence REAL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user TEXT,
    action TEXT,
    sku TEXT,
    payload JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

# -------- Suppliers --------
suppliers = [
    (1, "Acme Corp", "acme@example.com", "9876543210", 7, 4.5),
    (2, "Global Traders", "global@example.com", "9123456780", 5, 4.0),
    (3, "FreshSupply", "fresh@example.com", "9988776655", 10, 4.8),
]

cur.executemany("""
INSERT OR REPLACE INTO suppliers (id, name, email, phone, lead_time_days, rating)
VALUES (?, ?, ?, ?, ?, ?)
""", suppliers)

# -------- Products --------
products = [
    ("SKU001", "Red Apple", "Fruits", "pcs", 10, 20, 3, None),
    ("SKU002", "Banana", "Fruits", "pcs", 15, 25, 2, None),
    ("SKU003", "Tomato", "Vegetables", "kg", 5, 15, 1, None),
]

cur.executemany("""
INSERT OR REPLACE INTO products (sku, name, category, unit, safety_stock,
reorder_point, lead_time_days, metadata)
VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""", products)

# -------- Inventory --------
now = datetime.datetime.now().isoformat()

inventory = [
    ("SKU001", 50, 5, now),
    ("SKU002", 30, 3, now),
    ("SKU003", 10, 1, now),
]

cur.executemany("""
INSERT OR REPLACE INTO inventory (sku, qty, reserved, updated_at)
VALUES (?, ?, ?, ?)
""", inventory)

conn.commit()
conn.close()

print("Seeding complete.")
