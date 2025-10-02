import sys
import os
from pathlib import Path

# Ensure the Backend directory is in the system path for imports
sys.path.append(str(Path(__file__).resolve().parent.parent))

from rag import RAGService
from config import settings

def main():
    """
    Main function to run the data ingestion process.
    Initializes the RAGService and calls the build_index method.
    """
    print("--- Starting Data Ingestion Script ---")
    
    # Check if the PDF directory exists
    if not settings.PDF_DIR.exists() or not any(settings.PDF_DIR.iterdir()):
        print(f"Error: PDF directory '{settings.PDF_DIR}' is empty or does not exist.")
        print("Please add your PDF files to this directory and run the script again.")
        sys.exit(1)
        
    try:
        rag_service = RAGService()
        chunks_indexed = rag_service.build_index()
        
        if chunks_indexed > 0:
            print(f"\n✅ Ingestion complete. Indexed {chunks_indexed} new document chunks.")
        else:
            print("\n✅ No new documents to index. The knowledge base is up to date.")
            
        print(f"Vector database is located at: {settings.VECTOR_DB_DIR}")
        print("--- Ingestion Script Finished ---")
        
    except Exception as e:
        print(f"\n❌ An error occurred during ingestion: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
