import chromadb
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
        
        # Initialize persistent ChromaDB client
        self.db_client = chromadb.PersistentClient(path=str(settings.VECTOR_DB_DIR))
        self.collection = self.db_client.get_or_create_collection(name="documents")
        
        # Initialize Groq client
        self.groq_client = Groq(api_key=settings.GROQ_API_KEY)
        print("RAGService initialized.")

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
        """Processes PDFs from the configured directory and builds the ChromaDB index."""
        print(f"Checking for new PDFs in {settings.PDF_DIR}...")
        pdf_files = list(settings.PDF_DIR.glob("*.pdf"))
        
        documents_to_add = []
        for pdf_file in pdf_files:
            text = self._pdf_to_text(pdf_file)
            if not text: continue
            
            chunks = self._chunk_text(text)
            for i, chunk in enumerate(chunks):
                chunk_id = hashlib.sha1(f"{pdf_file.name}:{i}".encode()).hexdigest()
                
                # Check if this chunk ID already exists in the collection
                if not self.collection.get(ids=[chunk_id])['ids']:
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
        
        self.collection.add(
            ids=[doc['id'] for doc in documents_to_add],
            documents=texts,
            embeddings=embeddings.tolist(),
            metadatas=[doc['metadata'] for doc in documents_to_add]
        )
        print(f"Successfully indexed {len(documents_to_add)} chunks.")
        return len(documents_to_add)

    def retrieve(self, query: str, top_k: int) -> List[Dict]:
        """Retrieves top_k relevant context chunks from the vector store."""
        query_embedding = self.model.encode([query], convert_to_tensor=False)[0].tolist()
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        retrieved_chunks = []
        if results:
            for i in range(len(results['ids'][0])):
                retrieved_chunks.append({
                    "id": results['ids'][0][i],
                    "text": results['documents'][0][i],
                    "source": results['metadatas'][0][i]['source'],
                    "score": 1 - results['distances'][0][i] # Convert distance to similarity score
                })
        return retrieved_chunks
    
    def _build_prompt(self, contexts: List[dict], question: str) -> Tuple[str, str]:
        """Builds the system and user prompts for the LLM."""
        system_prompt = (
            "You are an expert AI assistant for mental health professionals. "
            "Your role is to provide accurate, concise information based *exclusively* on the context provided. "
            "Do not use any external knowledge. If the context does not contain the answer, state that clearly. "
            "Cite the source document for each piece of information using its filename, like `[some_document.pdf]`."
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