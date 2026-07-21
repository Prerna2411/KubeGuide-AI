import logfire
from app.agents.state import AgentState
from app.gateway.client import portkey_client, extract_cache_status


def generate_node(state: AgentState):
    """
    Synthesizes a response using both Documentation Context AND Conversation History.
    Uses the native Portkey client (not LangChain) so we can read the
    x-portkey-cache-status response header and surface Cache: Hit in the UI.
    """
    query = state["current_query"]

    history_str = ""
    for msg in state["messages"][:-1]:
        role = "User" if msg["role"] == "user" else "Assistant"
        history_str += f"{role}: {msg['content']}\n"

    user_msg = state["messages"][-1]["content"] if state["messages"] else ""

    if query == "CONVERSATIONAL":
        logfire.info("Generating conversational response using memory.")
        prompt = f"""
        You are a friendly and helpful Enterprise AI Assistant.
        Answer the user's latest message using the CONVERSATION HISTORY below.

        CONVERSATION HISTORY:
        {history_str}

        LATEST MESSAGE:
        "{user_msg}"
        """
    else:
        logfire.info("Generating technical RAG response.")
        max_context_chars = 25000
        full_context = ""

        for doc in state["documents"]:
            if len(full_context) + len(doc) < max_context_chars:
                full_context += doc + "\n\n"
            else:
                logfire.warning("Context truncated to fit Groq TPM limits.")
                break

        
        prompt = f"""
            You are a Senior Kubernetes and Enterprise Infrastructure Architect.

            Your task is to answer the user's question using ONLY the documentation below.

            Instructions:

            - Produce a clear, complete answer.
            - NEVER copy documentation verbatim.
            - NEVER list the retrieved chunks.
            - NEVER repeat the documentation.
            - Summarize the information.
            - If useful, include commands in markdown.
            - If the documentation doesn't answer the question, clearly say so.
            - Do not mention "documentation", "retrieved context", "chunks", or "sources".

            Documentation:
            {full_context}

            Conversation History:
            {history_str}

            Question:
            {user_msg}

            Answer:
            """
                    

    with logfire.span("✍️ LLM Synthesis"):
        try:
            response = portkey_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            
            print("=" * 80)
            print(response)
            print("=" * 80)

            try:
                print(response.model_dump())
            except Exception:
                pass
            
            
            #content = response.choices[0].message.content
            
            message = response.choices[0].message

            print(message)

            content = message.content

            print("CONTENT =", repr(content))
            cache_status = extract_cache_status(response)
            is_cache_hit = cache_status == "HIT"

            if is_cache_hit:
                logfire.info("⚡ Gateway Cache Hit — response served from Portkey cache.")
                plan_update = state["plan"] + ["Cache: Hit ⚡"]
                status = "Cache hit — instant response."
            else:
                logfire.info("✅ Response synthesised via LLM.")
                plan_update = state["plan"]
                status = "Response generated."

            return {
                "final_answer": content,
                "status": status,
                "plan": plan_update,
                "messages": [{"role": "assistant", "content": content}]
            }
            content = response.choices[0].message.content
            print("RETURNED FINAL ANSWER:", content)
            logfire.info(
                f"📝 Generated Answer Length: {len(content) if content else 0}"
            )

            

        except Exception as e:
            logfire.error(f"LLM Generation failed: {e}")
            raise e