from pydantic import BaseModel
from typing import List, Optional

class QueryRequest(BaseModel):
    question: str
    top_k: int = 3

class ContextChunk(BaseModel):
    id: str
    text: str
    source: str
    score: float

class QueryResponse(BaseModel):
    answer: str
    was_cached: bool
    context: Optional[List[ContextChunk]] = None