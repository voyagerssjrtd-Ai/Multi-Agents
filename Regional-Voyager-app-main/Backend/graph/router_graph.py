# Backend/graph/router_graph.py
from langgraph.graph import StateGraph, END
from graph.state import AgentState
from agents.router_agent import route_query
from agents.sql_agent import generate_sql
from agents.db_agent import query_db
from agents.format_agent import format_rows
from agents.llm_agent import call_llm, load_prompt, MODEL_REGISTRY

# ------------------------ Nodes ------------------------

def router_node(state: AgentState):
    user_input = state.get("input_text", "") or ""
    route = route_query(user_input)

    # DO NOT OVERWRITE THE STATE — MERGE IT
    return {
        "input_text": user_input,
        "intent": route["intent"],
        "target_agent": route["target_agent"]
    }


def sql_gen_node(state: AgentState):
    user_input = state.get("input_text", "")
    try:
        sql = generate_sql(user_input)
        return {
            "input_text": user_input,
            "sql": sql,
            "intent": state.get("intent"),
            "target_agent": "sql"
        }
    except Exception as e:
        return {
            "input_text": user_input,
            "sql_error": str(e),
            "intent": state.get("intent"),
            "target_agent": "llm"
        }


def db_exec_node(state: AgentState):
    sql = state.get("sql")
    rows = query_db(sql) if sql else [{"error": "No SQL"}]
    return {
        "input_text": state.get("input_text"),
        "rows": rows,
        "intent": state.get("intent"),
        "target_agent": "sql"
    }


def formatter_node(state: AgentState):
    out = format_rows(state.get("rows", []))
    return {
        "input_text": state.get("input_text"),
        "output": out,
        "intent": state.get("intent"),
        "target_agent": "sql"
    }


def llm_node(state: AgentState):
    fallback_prompt = load_prompt("conversation_system_prompt.txt") or "You are a helpful assistant."
    reply = call_llm(
        fallback_prompt,
        state.get("input_text", ""),
        model=MODEL_REGISTRY["reasoning_fallback"]
    )
    state["output"] = reply
    return state


def fallback_node(state: AgentState):
    state["output"] = "🤖 Sorry — I couldn't understand or perform that operation."
    return state


# ------------------------ Build Graph ------------------------

graph = StateGraph(AgentState)

graph.add_node("router", router_node)
graph.add_node("sql_gen", sql_gen_node)
graph.add_node("db_exec", db_exec_node)
graph.add_node("format", formatter_node)
graph.add_node("llm", llm_node)
graph.add_node("fallback", fallback_node)

graph.set_entry_point("router")

graph.add_conditional_edges(
    "router",
    lambda s: s.get("target_agent"),
    {
        "sql": "sql_gen",
        "llm": "llm",
        None: "fallback",
    }
)

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
