import re
from typing import Optional
from agents.db_agent import get_table_names
from agents.llm_agent import call_llm, load_prompt
from agents.llm_agent import MODEL_REGISTRY

SQL_SYSTEM_PROMPT = load_prompt("sql_system_prompt.txt")

# ---------------------------------------------------
#  RULE-BASED SQL (zero hallucinations)
# ---------------------------------------------------

def rule_based_sql(user_input: str) -> Optional[str]:
    q = user_input.lower()

    # 1) List all products
    if any(x in q for x in ["list products", "all products", "show products", "product list"]):
        return """
        SELECT sku, name, category, safety_stock, reorder_point, lead_time_days
        FROM products
        ORDER BY name ASC;
        """

    # 2) List inventory with qty
    if any(x in q for x in ["inventory", "stock report", "inventory status", "stock level"]):
        return """
        SELECT p.sku, p.name, p.category, i.qty, i.reserved, i.updated_at
        FROM products p
        JOIN inventory i ON p.sku = i.sku
        ORDER BY i.qty ASC;
        """

    # 3) Low stock
    if "low stock" in q:
        return """
        SELECT p.sku, p.name, i.qty, p.reorder_point
        FROM products p
        JOIN inventory i ON p.sku = i.sku
        WHERE i.qty <= p.reorder_point
        ORDER BY i.qty ASC;
        """

    # 4) Category queries ("how many fruits")
    m = re.search(r"(how much|how many|count)\s+([a-z\s]+)", q)
    if m:
        category = m.group(2).strip()
        return f"""
        SELECT p.sku, p.name, i.qty
        FROM products p
        JOIN inventory i ON p.sku = i.sku
        WHERE LOWER(p.category) LIKE LOWER('%{category}%');
        """

    # 5) Product-specific ("Red Apple")
    m = re.search(r"(how much|qty|quantity|stock|check)\s+(.+)", q)
    if m:
        product_name = m.group(2).strip()
        return f"""
        SELECT p.sku, p.name, i.qty
        FROM products p
        LEFT JOIN inventory i ON p.sku = i.sku
        WHERE LOWER(p.name) LIKE LOWER('%{product_name}%');
        """

    # Cannot handle — escalate to LLM
    return None


# ---------------------------------------------------
#  LLM-BASED SQL (for complex analytics)
# ---------------------------------------------------

def llm_based_sql(user_input: str) -> str:
    tables = get_table_names()
    system = SQL_SYSTEM_PROMPT.format(tables=", ".join(tables))
    prompt = f"User request: {user_input}\nReturn only SQL or --NO_SQL--."

    sql = call_llm(system, prompt, MODEL_REGISTRY["sql"]).strip()
    return sql


# ---------------------------------------------------
#  SQL VALIDATION
# ---------------------------------------------------

def validate_sql(sql: str) -> str:
    # No multiple statements
    if ";" in sql and sql.count(";") > 1:
        raise ValueError("Multiple SQL statements not allowed")

    # Must be SELECT
    if not re.match(r"^\s*select\b", sql, re.I):
        raise ValueError("Only SELECT queries allowed")

    # Must only use permitted tables
    allowed = set(get_table_names())
    found_tables = set(re.findall(r"\bfrom\s+([A-Za-z0-9_]+)", sql, re.I))
    found_tables |= set(re.findall(r"\bjoin\s+([A-Za-z0-9_]+)", sql, re.I))

    if not found_tables.issubset(allowed):
        raise ValueError(f"Unauthorized table access: {found_tables - allowed}")

    return sql


# ---------------------------------------------------
#  MAIN ENTRY POINT (Hybrid Logic)
# ---------------------------------------------------

def generate_sql(user_input: str) -> str:
    # Phase 1 → Try rule-based SQL
    rule_sql = rule_based_sql(user_input)
    if rule_sql:
        return validate_sql(rule_sql)

    # Phase 2 → LLM-based SQL
    sql = llm_based_sql(user_input)

    if sql.startswith("--NO_SQL--"):
        raise ValueError("Query cannot be answered by SQL")

    return validate_sql(sql)
