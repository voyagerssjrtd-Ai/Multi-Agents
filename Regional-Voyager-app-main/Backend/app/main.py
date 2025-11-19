# Backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from graph.router_graph import graph

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat(req: ChatRequest):
    state = {"input_text": req.message}
    try:
        result = graph.invoke(state)
        # langgraph returns merged dict; output key is the final assistant text
        return {
            "response": result.get("output") or "No response produced",
            "meta": {
                "intent": result.get("intent"),
                "agent": result.get("target_agent")
            }
        }
    except Exception as e:
        return {"response": f"❌ Error invoking graph: {e}"}

@app.get("/")
def root():
    return {"status": "running"}
