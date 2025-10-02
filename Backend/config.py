import os
from pydantic_settings import BaseSettings
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    # --- File Paths ---
    BASE_DIR: Path = Path(__file__).resolve().parent
    PDF_DIR: Path = BASE_DIR / "pdfs"
    VECTOR_DB_DIR: Path = BASE_DIR / "vector_store"

    # --- RAG & Embedding ---
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    
    # --- LLM Provider ---
    GROQ_API_KEY: str = os.environ.get("GROQ_API_KEY")
    LLM_MODEL: str = "llama-3.1-8b-instant"

    # --- Semantic Cache ---
    CACHE_COLLECTION_NAME: str = "semantic_cache"
    SIMILARITY_THRESHOLD: float = 0.95 # Threshold for semantic cache hit
    
    # --- Short-Term (L1) Cache ---
    SHORT_TERM_TTL: int = 600    # 10 minutes
    SHORT_TERM_MAX_SIZE: int = 128 # Max entries in TTL cache
    
# Instantiate settings to be imported by other modules
settings = Settings()