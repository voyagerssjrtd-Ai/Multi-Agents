# Backend/agents/db_agent.py
import sqlite3
from typing import List, Dict, Any

DB_PATH = "db/inventory.db"  # adjust path if needed

def _connect():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def get_table_names() -> List[str]:
    try:
        conn = _connect()
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [r["name"] for r in cur.fetchall()]
        conn.close()
        return tables
    except Exception:
        return []

def query_db(query: str) -> List[Dict[str, Any]]:
    """
    Execute a validated SELECT query and return rows as list of dicts.
    """
    try:
        # Simple safety guard: only allow SELECT
        q_stripped = query.strip().lower()
        if not q_stripped.startswith("select"):
            return [{"error": "Only SELECT queries are allowed"}]

        conn = _connect()
        cur = conn.cursor()
        cur.execute(query)
        rows = [dict(row) for row in cur.fetchall()]
        conn.close()
        return rows
    except Exception as e:
        return [{"error": str(e)}]
