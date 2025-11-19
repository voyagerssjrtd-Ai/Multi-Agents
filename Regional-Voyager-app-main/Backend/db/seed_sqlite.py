import sqlite3
import datetime

DB_PATH = "db/inventory.db"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

print("Seeding database with correct schema...")

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
