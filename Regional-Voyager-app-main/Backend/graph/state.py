from typing import TypedDict, Optional, Any

class AgentState(TypedDict, total=False):
    input_text: str   # <-- FIXED: rename correctly
    intent: Optional[str]
    target_agent: Optional[str]
    sql: Optional[str]
    sql_error: Optional[str]
    rows: Optional[Any]
    output: Optional[str]
