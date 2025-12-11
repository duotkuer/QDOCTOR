from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
import hashlib
import pdfplumber
from pathlib import Path
from typing import List, Dict, Tuple
from sentence_transformers import SentenceTransformer
from groq import Groq
import httpx
from config import settings

class RAGService:
    def __init__(self):
        print("Initializing RAGService...")
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
        
        # Initialize Qdrant client
        if settings.QDRANT_API_KEY:
            self.client = QdrantClient(
                url=settings.QDRANT_URL,
                api_key=settings.QDRANT_API_KEY
            )
        else:
            self.client = QdrantClient(url=settings.QDRANT_URL)
        
        # Ensure collection exists
        self._ensure_collection_exists()
        
        # Initialize Groq client
        self.groq_client = Groq(api_key=settings.GROQ_API_KEY)
        print("RAGService initialized.")

    def _ensure_collection_exists(self):
        """Creates the collection if it doesn't exist."""
        try:
            self.client.get_collection(settings.QDRANT_COLLECTION_NAME)
            print(f"Collection '{settings.QDRANT_COLLECTION_NAME}' already exists.")
        except Exception:
            print(f"Creating collection '{settings.QDRANT_COLLECTION_NAME}'...")
            self.client.create_collection(
                collection_name=settings.QDRANT_COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=settings.EMBEDDING_DIMENSION,
                    distance=Distance.COSINE
                )
            )
            print(f"Collection '{settings.QDRANT_COLLECTION_NAME}' created successfully.")

    def _pdf_to_text(self, path: Path) -> str:
        """Extracts text from a single PDF file."""
        try:
            with pdfplumber.open(path) as pdf:
                return "\n\n".join(page.extract_text() for page in pdf.pages if page.extract_text())
        except Exception as e:
            print(f"Error reading {path.name}: {e}")
            return ""

    def _chunk_text(self, text: str) -> List[str]:
        """Splits text into overlapping chunks."""
        if not text: return []
        chunks = []
        start = 0
        while start < len(text):
            end = start + settings.CHUNK_SIZE
            chunks.append(text[start:end])
            start += settings.CHUNK_SIZE - settings.CHUNK_OVERLAP
        return chunks

    def build_index(self):
        """Processes PDFs from the configured directory and builds the Qdrant index."""
        print(f"Checking for new PDFs in {settings.PDF_DIR}...")
        pdf_files = list(settings.PDF_DIR.glob("*.pdf"))
        
        documents_to_add = []
        for pdf_file in pdf_files:
            text = self._pdf_to_text(pdf_file)
            if not text: continue
            
            chunks = self._chunk_text(text)
            for i, chunk in enumerate(chunks):
                chunk_id = hashlib.sha1(f"{pdf_file.name}:{i}".encode()).hexdigest()
                
                # Check if this chunk ID already exists in Qdrant
                try:
                    self.client.retrieve(
                        collection_name=settings.QDRANT_COLLECTION_NAME,
                        ids=[int(chunk_id[:15], 16) % (2**63)]  # Convert hash to valid ID
                    )
                    continue  # Skip if exists
                except:
                    pass  # Proceed if doesn't exist
                
                documents_to_add.append({
                    "id": chunk_id,
                    "text": chunk,
                    "metadata": {"source": pdf_file.name}
                })

        if not documents_to_add:
            print("No new documents to index. Vector store is up to date.")
            return 0

        print(f"Found {len(documents_to_add)} new chunks to index...")
        
        texts = [doc['text'] for doc in documents_to_add]
        embeddings = self.model.encode(texts, convert_to_tensor=False, show_progress_bar=True)
        
        # Prepare points for Qdrant
        points = [
            PointStruct(
                id=int(doc['id'][:15], 16) % (2**63),  # Convert hash to valid positive ID
                vector=embedding.tolist(),
                payload={
                    "text": doc['text'],
                    "source": doc['metadata']['source']
                }
            )
            for doc, embedding in zip(documents_to_add, embeddings)
        ]
        
        self.client.upsert(
            collection_name=settings.QDRANT_COLLECTION_NAME,
            points=points
        )
        print(f"Successfully indexed {len(documents_to_add)} chunks.")
        return len(documents_to_add)

    def retrieve(self, query: str, top_k: int) -> List[Dict]:
        """Retrieves top_k relevant context chunks from the vector store."""
        query_embedding = self.model.encode([query], convert_to_tensor=False)[0].tolist()
        
        results = self.client.search(
            collection_name=settings.QDRANT_COLLECTION_NAME,
            query_vector=query_embedding,
            limit=top_k
        )
        
        retrieved_chunks = []
        for result in results:
            retrieved_chunks.append({
                "id": str(result.id),
                "text": result.payload.get('text', ''),
                "source": result.payload.get('source', 'N/A'),
                "score": result.score
            })
        return retrieved_chunks
    
    def _build_prompt(self, contexts: List[dict], question: str) -> Tuple[str, str]:
        """Builds the system and user prompts for the LLM."""
        system_prompt = (
    "You are QDoctor, an expert and empathetic AI assistant supporting mental health professionals. "
    "Engage users in a natural, conversational, and supportive tone—warm but always professional. "
    "Your goal is to provide concise, insightful, and supportive information strictly on mental health topics. "
    "If a user begins with a greeting, respond warmly, introduce yourself as QDoctor, and explain briefly how you can assist, "
    "while remaining focused on mental health matters. "
    "Always use the information from the provided context where applicable, expressing it creatively and in your own words. "
    "Never start sentences with phrases like 'According to the documents' or 'Based on the...'; "
    "instead, integrate the information naturally as if you already know it. "
    "If the context does not contain the answer, respond with: 'I don’t have that information at the moment.' "
    "Whenever you include facts, definitions, or recommendations from a source, cite it at the end of the sentence using the document name "
    "without the file extension, for example: Kenya Mental Health Policy."
)


        context_str = "\n\n---\n\n".join(
            f"Source: {c.get('source', 'N/A')}\n\nContent: {c.get('text', '')}" for c in contexts
        )

        user_prompt = f"**Context Documents:**\n{context_str}\n\n**Question:**\n{question}"
        return system_prompt, user_prompt

    async def generate(self, query: str, context: List[Dict]) -> str:
        """Generates an answer using the LLM with the provided context."""
        system_prompt, user_prompt = self._build_prompt(context, query)
        
        try:
            chat_completion = self.groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                model=settings.LLM_MODEL,
                temperature=0.1,  # Lower temperature for more factual responses
                max_tokens=1024,
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            print(f"Error during LLM call: {e}")
            raise RuntimeError(f"Failed to get a response from the LLM provider: {e}")