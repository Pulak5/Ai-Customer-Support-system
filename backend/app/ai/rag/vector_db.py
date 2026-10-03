import os
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.core.config import settings
from typing import List, Dict, Any

CHROMA_DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "chroma_db")

def get_vector_store() -> Chroma:
    """Returns a Chroma vector store instance."""
    if not settings.GOOGLE_API_KEY or settings.GOOGLE_API_KEY == "your-api-key-here":
        raise ValueError("Google API key not configured. Set GOOGLE_API_KEY in backend/.env")
        
    embeddings = GoogleGenerativeAIEmbeddings(
        model=settings.GEMINI_EMBEDDING_MODEL,
        google_api_key=settings.GOOGLE_API_KEY,
    )
    
    vector_store = Chroma(
        # Keep Gemini vectors separate from any existing OpenAI-embedded collection.
        collection_name="knowledge_base_gemini_v2",
        embedding_function=embeddings,
        persist_directory=CHROMA_DB_DIR
    )
    return vector_store


def reset_vector_store() -> Chroma:
    """Replace the local collection so re-indexing does not duplicate documents."""
    vector_store = get_vector_store()
    vector_store.delete_collection()
    return get_vector_store()

def similarity_search(query: str, k: int = 3) -> List[Dict[str, Any]]:
    """Searches the vector DB for the top k most relevant documents."""
    try:
        vector_store = get_vector_store()
        matches = vector_store.similarity_search_with_relevance_scores(query, k=k)
        results = []
        for doc, score in matches:
            results.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "relevance": round(max(0.0, min(float(score), 1.0)), 2),
            })
        return results
    except Exception as e:
        print(f"Error during similarity search: {e}")
        return []
