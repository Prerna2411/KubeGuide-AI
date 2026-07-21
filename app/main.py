# ============================================================
# CRITICAL: logfire MUST be configured before ALL other imports
# so that spans from all modules are captured from the start.
# ============================================================
import logfire
import os
from dotenv import load_dotenv

load_dotenv()
logfire.configure(token=os.getenv("LOGFIRE_TOKEN"))

# Now safe to import app modules - logfire is already active
from fastapi import FastAPI, Response
from app.agents.graph import rag_agent
#from app.guardrails.rails import initialize_rails, guard
from app.classifier import classify
from app.guardrails.rails import initialize_rails,output_guard
from pydantic import BaseModel
from typing import Optional


# Initialize FastAPI
app = FastAPI(title="Kube-Guide API")


@app.on_event("startup")
def startup_event():
    initialize_rails()

class QueryRequest(BaseModel):
    q: str
    thread_id: Optional[str] = "default_user"
    
    
@app.get("/")
def home():
    return {"message": "Enterprise LangGraph RAG API is live."}


@app.get("/graph")
def get_graph_image():
    """
    Returns the Mermaid image of the agent's workflow.
    """
    try:
        png_bytes = rag_agent.get_graph().draw_mermaid_png()
        return Response(content=png_bytes, media_type="image/png")
    except Exception as e:
        return {"error": f"Could not generate graph image: {e}"}
    
    
@app.post("/query")
def query(request: QueryRequest):
    """
    Executes the LangGraph RAG flow with memory using a POST request.
    """
    q = request.q
    thread_id = request.thread_id

    initial_state = {
        "messages": [{"role": "user", "content": q}],
        "current_query": q,
        "documents": [],
        "plan": ["Start"],
        "status": "Initializing Graph..."
    }
    
    # Configuration for Memory (Thread ID)
    config = {"configurable": {"thread_id": thread_id}}
    
    try:
        # Gate 1: NeMo Guardrails — blocks off-topic, jailbreaks, and handles dialog
        intent = classify(q)

        logfire.info(f"Intent = {intent.intent}")
        if intent.intent == "GREETING":

            return {
                "question": q,
                "answer": "Hello! I'm your Enterprise AI Assistant. How can I help you today?",
                "thought_process": ["Greeting"],
                "status": "completed",
                "sources": []
            }


        if intent.intent == "CAPABILITIES":

            return {
                "question": q,
                "answer": (
                    "I specialize in Kubernetes, Enterprise Networking, Intel Hardware, "
                    "Python, AI Engineering, LangChain, LangGraph, RAG systems, "
                    "LLMs and related enterprise technologies."
                ),
                "thought_process": ["Capabilities"],
                "status": "completed",
                "sources": []
            }


        if intent.intent == "FAREWELL":

            return {
                "question": q,
                "answer": "Goodbye! Have a great day.",
                "thought_process": ["Farewell"],
                "status": "completed",
                "sources": []
            }


        if intent.intent == "OFF_TOPIC":

            return {
                "question": q,
                "answer": (
                    "I'm an Enterprise AI Assistant focused on enterprise technology. "
                    "Please ask me about Kubernetes, AI, networking, Intel hardware, "
                    "or related technical topics."
                ),
                "thought_process": ["Off Topic"],
                "status": "blocked",
                "sources": []
            }


        if intent.intent == "JAILBREAK":

            return {
                "question": q,
                "answer": (
                    "I can't assist with requests to ignore or override my instructions. "
                    "If you have a technical question related to my supported domains, "
                    "I'll be happy to help."
                ),
                "thought_process": ["Jailbreak"],
                "status": "blocked",
                "sources": []
            }
        
        # Gate 2: LangGraph RAG pipeline
        # Run the graph synchronously to preserve Logfire context variables
        #final_output = rag_agent.invoke(initial_state, config=config)
        final_output = rag_agent.invoke(initial_state, config=config)

        answer = final_output.get("final_answer")

        #answer = output_guard(answer)
        answer = output_guard(
            question=q,
            answer=answer
        )

        return {
            "question": q,
            "answer": answer,
            "thought_process": final_output.get("plan"),
            "status": final_output.get("status"),
            "sources": final_output.get("documents", [])
        }
        
    except Exception as e:
        logfire.error(f"❌ Backend Execution Failed: {e}")
        return {
            "question": q,
            "answer": "I apologize, but I encountered an internal error while processing your request. Please try again later.",
            "thought_process": ["Error encountered during execution."],
            "status": "error",
            "sources": []
        }