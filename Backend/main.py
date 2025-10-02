import asyncio
from fastapi import FastAPI, HTTPException
from schemas import QueryRequest, QueryResponse, ContextChunk
from rag import RAGService
from guardrails import GuardrailService
from memory import CacheService
from config import settings

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application startup...")
    if not settings.GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY environment variable not set!")
    print("Services initialized successfully.")
    yield
    # (Optional) Add any shutdown/cleanup logic here

app = FastAPI(
    title="QDOCTOR Clinical Assistant",
    description="An AI agent for mental health professionals using RAG.",
    version="1.0.0",
    lifespan=lifespan
)

# --- Service Initialization ---
# These are initialized once at startup and shared across requests.
rag_service = RAGService()
guardrail_service = GuardrailService()
cache_service = CacheService()

@app.post("/ask", response_model=QueryResponse)
async def ask_question(request: QueryRequest):
    """
    Receives a question, processes it through the RAG pipeline, and returns an answer.
    """
    # 1. Input Guardrail: Validate and sanitize the incoming question.
    is_safe, processed_query = guardrail_service.input_guard.validate(request.question)
    if not is_safe:
        raise HTTPException(status_code=400, detail=processed_query)

    # 2. Cache Check: Try to find a similar question in the cache.
    cached_response = cache_service.get(processed_query)
    if cached_response:
        return cached_response

    # 3. Retrieve Context: Get relevant document chunks from the vector store.
    retrieved_contexts = rag_service.retrieve(processed_query, top_k=request.top_k)
    
    if not retrieved_contexts:
        # If no context is found, return a safe, default response.
        fallback_answer = "I could not find relevant information in the knowledge base to answer this question."
        response = QueryResponse(answer=fallback_answer, was_cached=False, context=[])
        cache_service.set(processed_query, response) # Cache the "not found" response
        return response

    # 4. Generate Answer: Use the LLM to generate an answer based on the context.
    try:
        generated_answer = await rag_service.generate(processed_query, retrieved_contexts)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    # 5. Output Guardrail: Validate the generated answer for safety and relevance.
    is_valid, final_answer = guardrail_service.output_guard.validate(generated_answer, retrieved_contexts)
    if not is_valid:
        # If output guardrail fails, provide a safe fallback.
        final_answer = "The generated response did not pass safety checks. Please try rephrasing your question."

    # 6. Create and Cache Final Response
    context_objects = [ContextChunk(**c) for c in retrieved_contexts]
    final_response = QueryResponse(
        answer=final_answer, 
        was_cached=False, 
        context=context_objects
    )
    cache_service.set(processed_query, final_response)

    return final_response

@app.get("/")
def read_root():
    return {"message": "Welcome to the QDoctor API. Go to /docs for usage."}