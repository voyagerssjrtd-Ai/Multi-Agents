# Backend/agents/format_agent.py
from typing import List, Dict
from agents.llm_agent import call_llm, load_prompt
from agents.llm_agent import MODEL_REGISTRY
FORMAT_PROMPT = load_prompt("format_prompt.txt")
def format_rows(rows: List[Dict]) -> str:
    # if error returned by db agent, pass through
    if not rows:
        return "No rows returned."

    if isinstance(rows, list) and len(rows) == 1 and "error" in rows[0]:
        return f"Error from DB: {rows[0]['error']}"

    preview = rows if len(rows) <= 20 else rows[:20]

    user_prompt = f"Rows (JSON):\n{preview}\n\nReturn a short human summary and a small table (or bullet list) describing these rows."

    return call_llm(FORMAT_PROMPT, user_prompt, model=MODEL_REGISTRY.get("formatter"))