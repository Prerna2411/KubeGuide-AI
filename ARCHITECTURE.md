# KubeGuide AI Architecture

This document describes the end-to-end architecture of **KubeGuide AI**, an enterprise-grade Agentic RAG system for Kubernetes documentation.

The application combines:

- LangGraph Agentic Workflow
- Groq Intent Classification
- Portkey LLM Gateway
- Gemini Embeddings
- FlashRank Reranking
- Qdrant Cloud
- NeMo Output Guardrails
- Integrated RAGAS Evaluation Suite
- Logfire Observability

---

# Overall System Architecture

```mermaid
graph LR

    %% ---------------- UI ----------------

    subgraph UI["🖥️ Streamlit Multipage UI"]
        CHAT["💬 Chat Assistant"]
        EVAL["🧪 Evaluation Suite"]
    end

    %% ---------------- Backend ----------------

    subgraph API["⚡ FastAPI Backend"]

        INTENT["🧠 Groq Intent Classifier"]

        PLANNER["📝 Planner Node"]

        RETRIEVER["🔍 Retriever Node"]

        RESPONDER["🤖 Responder Node"]

        OUTPUT["🛡️ NeMo Output Rails"]

        MEMORY[("💾 LangGraph Memory")]
    end

    %% ---------------- Retrieval ----------------

    subgraph RET["🔎 Retrieval"]

        EMB["Gemini Embeddings"]

        QD[(Qdrant Cloud)]

        FR["FlashRank"]

    end

    %% ---------------- Gateway ----------------

    subgraph GW["🌐 Portkey Gateway"]

        PK["Portkey"]

        G1["Groq Primary"]

        G2["Groq Fallback"]

    end

    %% ---------------- Ingestion ----------------

    subgraph ING["📥 Document Ingestion"]

        DOCS["PDF • DOCX • HTML • PPTX • TXT"]

        PROC["processed_data"]

        GEM["Gemini Embeddings"]

    end

    %% ---------------- Evaluation ----------------

    subgraph EV["🧪 Evaluation"]

        GOLD["Golden Dataset"]

        PIPE["Live Pipeline"]

        RAGAS["RAGAS"]

        TOOL["Tool Correctness"]

        JUDGE["Judge LLM"]

    end

    %% ---------------- Observability ----------------

    subgraph OBS["📈 Observability"]

        LOG["Pydantic Logfire"]

    end

    %% ---------------- Flow ----------------

    CHAT --> INTENT
    EVAL --> PIPE

    PIPE --> INTENT

    INTENT -->|Technical| PLANNER
    INTENT -->|Greeting| OUTPUT
    INTENT -->|Capabilities| OUTPUT
    INTENT -->|Farewell| OUTPUT
    INTENT -->|Off Topic| OUTPUT
    INTENT -->|Jailbreak| OUTPUT

    PLANNER --> RETRIEVER

    RETRIEVER --> EMB

    EMB --> QD

    QD --> FR

    FR --> RESPONDER

    RESPONDER --> OUTPUT

    OUTPUT --> CHAT

    PLANNER -. Memory .-> MEMORY
    RESPONDER -. Memory .-> MEMORY

    PLANNER --> PK
    RESPONDER --> PK

    PK --> G1
    PK -. Fallback .-> G2

    DOCS --> PROC

    PROC --> GEM

    GEM --> QD

    PIPE --> GOLD

    PIPE --> RAGAS

    PIPE --> TOOL

    RAGAS --> JUDGE

    INTENT -. Trace .-> LOG
    PLANNER -. Trace .-> LOG
    RETRIEVER -. Trace .-> LOG
    RESPONDER -. Trace .-> LOG


```

Query Processing Pipeline

```mermaid
flowchart LR

    U[👤 User] --> S[💬 Streamlit UI]

    S --> F[⚡ FastAPI]

    F --> I[🧠 Groq Intent Classifier]

    I -->|Technical| P[📝 Planner]

    I -->|Greeting| O[🛡️ Output Rails]

    I -->|Capabilities| O

    I -->|Farewell| O

    I -->|Off Topic| R[🚫 Reject]

    I -->|Jailbreak| R

    P --> T[🔍 Retriever]

    T --> Q[(Qdrant)]

    Q --> FR[⚡ FlashRank]

    FR --> RS[🤖 Responder]

    RS --> O

    O --> U
```


Retrieval Pipeline

```mermaid
flowchart LR

    D[Enterprise Documents]
        --> C[Chunking]

    C
        --> E[Gemini Embeddings]

    E
        --> Q[(Qdrant Cloud)]

    UQ[User Query]
        --> QE[Query Embedding]

    QE
        --> VS[Vector Search]

    VS
        --> Q

    Q
        --> FR[FlashRank]

    FR
        --> CT[Retrieved Context]

    CT
        --> LLM[Groq LLM]

    LLM
        --> ANS[Final Answer]
```

Evaluation Pipeline


```mermaid
flowchart LR

    G[Golden Dataset]
        --> P[Live FastAPI Calls]

    P
        --> R[Responses]

    R
        --> C[Retrieved Contexts]

    C
        --> GT[Guardrails Tests]

    GT
        --> RG[RAGAS]

    RG
        --> F1[Faithfulness]

    RG
        --> F2[Answer Relevancy]

    RG
        --> F3[Context Precision]

    RG
        --> F4[Context Recall]

    RG
        --> F5[Answer Correctness]

    R
        --> TC[Tool Correctness]

    R
        --> REP[Evaluation Report]
```


Deployment Architecture

```mermaid

graph LR

User

-->

Streamlit["Streamlit Multipage UI"]

-->

Render["FastAPI Backend (Render)"]

Render

-->

Portkey

Portkey

-->

Groq

Render

-->

Qdrant

Render

-->

Logfire

```
