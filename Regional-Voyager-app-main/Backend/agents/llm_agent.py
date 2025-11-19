# Backend/agents/llm_agent.py
import os
from pathlib import Path
import httpx

# ======================
#  ENV + MODEL CONFIG
# ======================
GENAI_BASE_URL = os.getenv("AZURE_MAAS_BASE_URL", "https://genailab.tcs.in/v1")
GENAI_API_KEY  = os.getenv("AZURE_MAAS_API_KEY", "sk-WnxRDjT2EFDS6zzGYaI5Jw")
GENAI_MODEL    = os.getenv("GENAI_MODEL", "azure_ai/genailab-maas-DeepSeek-V3-0324")

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {GENAI_API_KEY}",
}

PROMPT_DIR = Path("config/prompts")

# Registry of model choices for different agent roles (adjust to your available models)
MODEL_REGISTRY = {
    "sql": "azure/genailab-maas-gpt-4o-mini",          # concise reasoning for SQL generation
    "formatter": "azure/genailab-maas-gpt-4o-mini",    # summarization/formatting
    "conversation": "azure/genailab-maas-gpt-4o",      # friendly conversational
    "reasoning_fallback": "azure/genailab-maas-gpt-4o" # stronger reasoning fallback
}


# ======================
#  Helper: Read Prompt
# ======================
def load_prompt(file_name: str) -> str:
    """Load prompt text from /config/prompts folder."""
    file_path = PROMPT_DIR / file_name
    if not file_path.exists():
        return ""
    return file_path.read_text().strip()


# ======================
#  Base LLM Caller
# ======================
def call_llm(system_prompt: str, user_prompt: str, model: str | None = None) -> str:
    """
    Universal LLM call entry point with SSL bypass.
    model: optional override (use entries from MODEL_REGISTRY).
    """
    chosen_model = model or GENAI_MODEL

    payload = {
        "model": chosen_model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "stream": False
    }

    try:
        # SSL bypass client for corporate environments (verify=False)
        with httpx.Client(verify=False, timeout=30) as client:
            r = client.post(
                f"{GENAI_BASE_URL}/chat/completions",
                headers=HEADERS,
                json=payload
            )

        if r.status_code != 200:
            return f"⚠️ LLM Error [{r.status_code}]: {r.text}"

        data = r.json()
        # defensive access
        return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"⚠️ LLM request failed: {e}"


# ======================
#  Conversational Agent
# ======================
def chat_agent(user_input: str) -> str:
    """Simple natural conversation agent using 'conversation' model."""
    system_prompt = load_prompt("conversation_system_prompt.txt") or \
        "You are a friendly helpful assistant. Respond clearly."
    return call_llm(system_prompt, user_input, model=MODEL_REGISTRY.get("conversation"))
