"""Load the project's local policy files into the Gemini/Chroma knowledge base."""
import sys
from pathlib import Path

if __name__ == "__main__":
    sys.path.append(str(Path(__file__).resolve().parents[3]))

from langchain_core.documents import Document

from app.ai.rag.vector_db import get_vector_store

KNOWLEDGE_BASE_DIR = Path(__file__).resolve().parents[4] / "data" / "knowledge_base"


def title_for(path: Path) -> str:
    return path.stem.replace("_", " ").title()


def chunk_text(text: str, size: int = 700) -> list[str]:
    """Split small policy documents at paragraph boundaries for focused retrieval."""
    paragraphs = [paragraph.strip() for paragraph in text.split("\n\n") if paragraph.strip()]
    chunks: list[str] = []
    current = ""
    for paragraph in paragraphs:
        if current and len(current) + len(paragraph) + 2 > size:
            chunks.append(current)
            current = paragraph
        else:
            current = f"{current}\n\n{paragraph}".strip()
    if current:
        chunks.append(current)
    return chunks


def load_documents() -> list[Document]:
    documents = []
    for path in sorted(KNOWLEDGE_BASE_DIR.glob("*.txt")):
        for index, chunk in enumerate(chunk_text(path.read_text(encoding="utf-8"))):
            documents.append(Document(
                page_content=chunk,
                metadata={"source": path.stem, "title": title_for(path), "chunk": index},
            ))
    return documents


def ingest_knowledge_base():
    """Create embeddings for the local fictional company policies."""
    documents = load_documents()
    if not documents:
        raise RuntimeError(f"No knowledge-base files found in {KNOWLEDGE_BASE_DIR}")
    vector_store = get_vector_store()
    vector_store.add_documents(documents)
    print(f"Successfully ingested {len(documents)} knowledge-base chunks into the Vector DB.")


if __name__ == "__main__":
    ingest_knowledge_base()
