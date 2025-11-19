# Backend/agents/sql_agent.py
import re
from typing import List
from agents.llm_agent import call_llm, load_prompt, MODEL_REGISTRY
from agents.db_agent import get_table_names

SQL_SYSTEM_PROMPT = load_prompt("sql_system_prompt.txt")

def generate_sql(user_input: str) -> str:
    """
    Ask the LLM to produce SQL for user_input. Then validate SQL.
    Returns SQL string or raises ValueError on invalid SQL.
    """
    tables = get_table_names()
    system = SQL_SYSTEM_PROMPT.format(tables=", ".join(tables))

    prompt = f"User request: {user_input}\n\nReturn only a single SQLite SELECT statement or --NO_SQL--."

    # use the 'sql' model from registry
    sql = call_llm(system, prompt, model=MODEL_REGISTRY.get("sql")).strip()

    if not sql:
        raise ValueError("Empty response from SQL generator")

    if sql.startswith("--NO_SQL--"):
        raise ValueError("LLM decided this is not a SQL request")

    # Basic validation:
    if ";" in sql and sql.count(";") > 1:
        raise ValueError("Multiple statements not allowed")

    if not re.match(r"^\s*select\b", sql, re.I):
        raise ValueError("Only SELECT queries are allowed")

    # Ensure only allowed tables are used
    allowed = set(tables)
    found_tables = set(re.findall(r"\bfrom\s+([A-Za-z0-9_]+)", sql, re.I))
    found_tables |= set(re.findall(r"\bjoin\s+([A-Za-z0-9_]+)", sql, re.I))

    if not found_tables.issubset(allowed):
        raise ValueError(f"SQL references unauthorized tables: {found_tables - allowed}")

    return sql
