# Backend/graph/router_graph.py
from langgraph.graph import StateGraph, END
from graph.state import AgentState
from agents.router_agent import route_query
from agents.sql_agent import generate_sql
from agents.db_agent import query_db
from agents.format_agent import format_rows
from agents.llm_agent import call_llm, load_prompt, MODEL_REGISTRY

# Nodes
def router_node(state: AgentState):
    user_input = state.get("input_text", "") or ""
    route = route_query(user_input)
    state["intent"] = route["intent"]
    state["target_agent"] = route["target_agent"]
    return state

def sql_gen_node(state: AgentState):
    user_input = state.get("input_text", "")
    try:
        sql = generate_sql(user_input)
        return {"sql": sql}
    except Exception as e:
        # fall back to LLM if SQL generation fails
        return {"sql_error": str(e), "target_agent": "llm"}

def db_exec_node(state: AgentState):
    sql = state.get("sql")
    if not sql:
        return {"rows": [{"error": "No SQL provided"}]}
    rows = query_db(sql)
    return {"rows": rows}

def formatter_node(state: AgentState):
    rows = state.get("rows", [])
    output = format_rows(rows)
    return {"output": output}

def llm_node(state: AgentState):
    fallback_prompt = load_prompt("conversation_system_prompt.txt") or "You are a helpful assistant."
    reply = call_llm(fallback_prompt, state.get("input_text", ""), model=MODEL_REGISTRY.get("reasoning_fallback"))
    return {"output": reply}

def fallback_node(state: AgentState):
    return {"output": "🤖 Sorry — I couldn't understand or perform that operation."}

# Build graph
graph = StateGraph(AgentState)

graph.add_node("router", router_node)
graph.add_node("sql_gen", sql_gen_node)
graph.add_node("db_exec", db_exec_node)
graph.add_node("format", formatter_node)
graph.add_node("llm", llm_node)
graph.add_node("fallback", fallback_node)

graph.set_entry_point("router")

# route: router -> sql_gen when db, else llm
graph.add_conditional_edges(
    "router",
    lambda s: s.get("target_agent"),
    {
        "db": "sql_gen",
        "llm": "llm",
        None: "fallback",
    },
)

# sql flow
graph.add_conditional_edges(
    "sql_gen",
    lambda s: "sql" if "sql" in s else "sql_error",
    {
        "sql": "db_exec",
        "sql_error": "llm"
    }
)

graph.add_edge("db_exec", "format")
graph.add_edge("format", END)

graph.add_edge("llm", END)
graph.add_edge("fallback", END)

graph = graph.compile()
