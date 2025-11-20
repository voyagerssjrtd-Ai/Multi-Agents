# Backend/agents/router_agent.py
from pathlib import Path
import yaml
from typing import Dict, Any

RULES = yaml.safe_load(Path("config/router_rules.yaml").read_text())

def route_query(text: str) -> Dict[str, Any]:
    q = text.lower().strip()

    for rule in RULES["intents"]:
        for kw in rule["keywords"]:
            if kw in q:
                return {
                    "intent": rule["name"],
                    "target_agent": rule["target_agent"],
                    "type": "keyword"
                }

    fb = RULES["fallback"]
    return {
        "intent": fb["name"],
        "target_agent": fb["target_agent"],
        "type": "fallback"
    }
