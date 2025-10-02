import hashlib
import json 
from typing import Optional, Tuple, List, Dict
from cachetools import TTLCache
from sentence_transformers import SentenceTransformer
import chromadb
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from config import settings
from schemas import QueryResponse, ContextChunk

class CacheService:
    def __init__(self):
        print("Initializing CacheService...")
        # L1 Cache: Fast, in-memory, exact-match cache with a time-to-live
        self.l1_cache = TTLCache(maxsize=settings.SHORT_TERM_MAX_SIZE, ttl=settings.SHORT_TERM_TTL)
        
        # L2 Cache: Slower, persistent, semantic-match cache
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
        self.db_client = chromadb.PersistentClient(path=str(settings.VECTOR_DB_DIR))
        self.l2_collection = self.db_client.get_or_create_collection(name=settings.CACHE_COLLECTION_NAME)
        print("CacheService initialized.")

    def _make_key(self, text: str) -> str:
        """Creates a deterministic SHA256 hash for a given text string."""
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def get(self, query: str) -> Optional[QueryResponse]:
        """
        Tries to retrieve a response from the cache.
        1. Checks L1 cache for an exact match.
        2. Checks L2 cache for a semantically similar match.
        """
        # --- L1 Cache Check (Exact Match) ---
        key = self._make_key(query)
        cached_l1 = self.l1_cache.get(key)
        if cached_l1:
            print(f"L1 Cache HIT for key: {key[:8]}")
            return QueryResponse(**cached_l1)

        # --- L2 Cache Check (Semantic Match) ---
        query_embedding = self.model.encode([query])[0]
        
        results = self.l2_collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=1
        )
        
        if results and results['ids'][0]:
            # Calculate similarity between query and the best match from cache
            # ChromaDB returns distance, so we can't directly use it as a similarity threshold.
            # We must fetch the embedding and calculate cosine similarity manually.
            match_id = results['ids'][0][0]
            match_data = self.l2_collection.get(ids=[match_id], include=["embeddings", "metadatas"])
            
            cached_embedding = np.array(match_data['embeddings'][0])
            similarity = cosine_similarity([query_embedding], [cached_embedding])[0][0]
            
            if similarity >= settings.SIMILARITY_THRESHOLD:
                print(f"L2 Cache HIT with similarity {similarity:.4f}")
                cached_answer = match_data['metadatas'][0]['answer']
                context_json_string = match_data['metadatas'][0].get('context')
                
                # Parse the JSON string back into a list of dictionaries
                if context_json_string:
                    context_dicts = json.loads(context_json_string)
                    context_objects = [ContextChunk(**c) for c in context_dicts]
                else:
                    context_objects = None
                
                response = QueryResponse(answer=cached_answer, was_cached=True, context=context_objects)
                
                # Also store this hit in the L1 cache for faster access next time
                self.l1_cache[key] = response.model_dump()
                return response

        print("Cache MISS")
        return None

    def set(self, query: str, response: QueryResponse):
        """Stores a new question-answer pair in both L1 and L2 caches."""
        key = self._make_key(query)
        
        # Store in L1 cache (no change needed here)
        self.l1_cache[key] = response.model_dump()
        print(f"Stored in L1 Cache with key: {key[:8]}")

        # Store in L2 cache
        query_embedding = self.model.encode([query])[0].tolist()
        context_dicts = [c.model_dump() for c in response.context] if response.context else []
        context_json_string = json.dumps(context_dicts) 
        
        self.l2_collection.add(
            ids=[key],
            embeddings=[query_embedding],
            metadatas=[{"query": query, "answer": response.answer, "context": context_json_string}]
        )
        print(f"Stored in L2 Cache with key: {key[:8]}")