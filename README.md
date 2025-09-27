# QDoctor Agent: System Documentation & Architecture

**Version:** 1.0  
**Date:** September 27, 2025  

---

## 1. Overview 📜

QDoctor is a specialized AI agent designed to serve as a secure, reliable, and context-aware assistant for doctors, therapists, and other professionals in the mental health sector.  

Its primary function is to answer queries by retrieving information from a curated knowledge base of trusted clinical documents, research papers, and policy guidelines.  

The agent is built with a **multi-layered security and reliability architecture**, ensuring responses are not only accurate but also safe, private, and compliant with healthcare standards.  

### 1.1 Core Principles

- **Accuracy**: Answers are grounded in a vetted, private knowledge base using a Retrieval-Augmented Generation (RAG) model.  
- **Security**: Multi-layered guardrails prevent the leakage of Protected Health Information (PHI) and protect the system from malicious prompts.  
- **Efficiency**: An integrated caching layer provides instantaneous responses to previously answered questions, reducing latency and computational cost.  
- **Reliability**: Includes self-correction and output validation to prevent hallucinations and ensure responses are aligned with clinical standards.  
- **Domain-Specificity**: Strictly limited to the domain of mental health and associated policies.  

---

## 2. System Architecture & Workflow 🧠

The agent operates through a **sequential, multi-stage pipeline**, where each stage is modular and responsible for a specific task.  

### Workflow Breakdown

1. **Query Ingestion** → User submits a query through a secure API endpoint.  
2. **Cache Check** → High-speed cache (Redis) checks if the query has been answered before.  
   - **Cache Hit** → Stored validated answer returned immediately.  
   - **Cache Miss** → Proceeds to RAG retrieval.  
3. **Context Construction (RAG)**  
   - Query converted into vector embeddings.  
   - Similarity search performed on vector DB (DSM-5, NICE guidelines, clinical trials).  
   - Top-k chunks retrieved as context.  
4. **Input Guardrail**  
   - **PII/PHI Sanitization**: Redacts sensitive info.  
   - **Prompt Injection Defense**: Blocks malicious instructions.  
5. **LLM Gateway**  
   - Routes to best-suited LLM (precise vs. fast).  
   - Formats inputs into structured prompts.  
   - Generates draft response.  
6. **Scoring & Self-Correction (Optional)**  
   - Draft scored for factual consistency.  
   - If low, triggers regeneration.  
7. **Output Guardrail**  
   - **Hallucination & Contradiction Check**.  
   - **Safety & Tone Analysis**.  
   - **Policy Enforcement**: Returns canned fallback if validation fails.  
8. **Response Delivery & Cache Update**  
   - Final response delivered to user.  
   - Query + answer stored in cache.  

---

## 3. Codebase Architecture 💻

```plaintext
qdoctor_agent/
├── main.py                 # API Entrypoint (FastAPI)
├── orchestration/
│   ├── __init__.py
│   └── agent_pipeline.py   # Main agent logic and workflow conductor
├── components/
│   ├── __init__.py
│   ├── cache_manager.py    # Redis caching logic
│   ├── rag_retriever.py    # Vector store interaction and context retrieval
│   ├── guardrails.py       # Input and Output validation modules
│   └── llm_gateway.py      # LLM API interaction, routing, and prompting
├── config/
│   ├── __init__.py
│   └── settings.py         # Configuration management (Pydantic)
├── prompts/
│   ├── __init__.py
│   └── templates.py        # Stores all prompt templates
├── knowledge_base/
│   ├── documents/          # Raw source documents (PDFs, TXTs)
│   └── ingest.py           # Script to process and load docs into vector store
├── tests/
│   ├── test_guardrails.py
│   └── test_pipeline.py
├── .env                    # Environment variables (API keys, DB URIs)
├── requirements.txt        # Python dependencies
└── Dockerfile              # Containerization for deployment
```

---

## 4. File-by-File Implementation Details 📝

### `main.py` (API Entrypoint)

- Exposes functionality via **FastAPI**.  
- Provides `/ask` endpoint.  
- Handles query validation, orchestration call, and error handling.  

**Pseudocode Example:**

```python
from fastapi import FastAPI, HTTPException
from orchestration.agent_pipeline import QDoctorAgent
from pydantic import BaseModel

app = FastAPI(title="QDoctor API")
agent = QDoctorAgent()

class QueryRequest(BaseModel):
    question: str

@app.post("/ask")
async def ask_qdoctor(request: QueryRequest):
    try:
        response = agent.run(request.question)
        return {"answer": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

### `orchestration/agent_pipeline.py` (Orchestrator)

- Core workflow controller.  
- Connects cache, retriever, guardrails, and LLM.  

**Pseudocode Example:**

```python
from components.cache_manager import CacheManager
from components.rag_retriever import RAGRetriever
from components.guardrails import InputGuardrail, OutputGuardrail
from components.llm_gateway import LLMGateway

class QDoctorAgent:
    def __init__(self):
        self.cache = CacheManager()
        self.retriever = RAGRetriever()
        self.input_guardrail = InputGuardrail()
        self.output_guardrail = OutputGuardrail()
        self.llm = LLMGateway()

    def run(self, query: str) -> str:
        # 1. Cache Check
        cached_response = self.cache.get(query)
        if cached_response:
            return cached_response

        # 2. Context Construction
        context = self.retriever.retrieve_context(query)
        if not context:
            return "I do not have enough information to answer that question."

        # 3. Input Guardrail
        is_safe, sanitized_query = self.input_guardrail.validate(query)
        if not is_safe:
            raise ValueError("Input failed security checks.")

        # 4. LLM Gateway
        raw_response = self.llm.generate(sanitized_query, context)

        # 5. Output Guardrail
        is_valid, final_response = self.output_guardrail.validate(raw_response, context)
        if not is_valid:
            return "My generated response failed validation. I cannot provide a reliable answer."

        # 6. Cache Update
        self.cache.set(query, final_response)
        return final_response
```

---

### `components/rag_retriever.py`

- Manages vector DB queries.  
- Embeds queries and retrieves top-k relevant docs.  

---

### `components/guardrails.py`

- **InputGuardrail** → Sanitizes PII, prevents injection.  
- **OutputGuardrail** → Validates factuality, safety, tone.  

---

### `components/llm_gateway.py`

- Abstracts LLM API calls.  
- Handles routing and prompt formatting.  
- Uses `prompts/templates.py` for consistency.  

---

## 5. Key Technologies & Dependencies 🛠️

- **Web Framework**: FastAPI, Uvicorn  
- **Orchestration/LLM Framework**: LangChain or LlamaIndex  
- **Vector Database**: ChromaDB (local), Pinecone, or Weaviate (cloud)  
- **Caching**: Redis  
- **Guardrails**: NVIDIA NeMo Guardrails, Guardrails AI, or custom implementation  
- **Configuration**: Pydantic  
- **LLM Providers**: OpenAI, Anthropic (Claude), Google (Gemini)  
- **Containerization**: Docker  

---
