import os
import sys

# Add backend directory to sys.path if running as script
if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from langchain_core.documents import Document
from app.ai.rag.vector_db import get_vector_store

# Sample knowledge base data
KNOWLEDGE_BASE = [
    {
        "content": "Our return policy allows returns within 30 days of purchase. The item must be in its original condition and packaging. To initiate a return, please go to your account dashboard and select 'Return Item'.",
        "metadata": {"source": "return_policy", "topic": "returns"}
    },
    {
        "content": "To reset your password, click on the 'Forgot Password' link on the login page. You will receive an email with a link to create a new password. The link is valid for 24 hours.",
        "metadata": {"source": "faq", "topic": "account_access"}
    },
    {
        "content": "If you are experiencing connection drops on our software, please ensure your firewall is not blocking port 443. Additionally, clearing your browser cache or restarting the router resolves the issue in 90% of cases.",
        "metadata": {"source": "troubleshooting", "topic": "technical_support"}
    },
    {
        "content": "We offer three pricing tiers: Basic ($9/mo), Pro ($29/mo), and Enterprise (Custom). You can upgrade or downgrade at any time. Prorated charges will apply.",
        "metadata": {"source": "pricing_page", "topic": "billing"}
    }
]

def ingest_knowledge_base():
    """Converts the knowledge base to embeddings and saves to Chroma."""
    try:
        vector_store = get_vector_store()
        
        documents = [
            Document(page_content=item["content"], metadata=item["metadata"])
            for item in KNOWLEDGE_BASE
        ]
        
        vector_store.add_documents(documents)
        print(f"Successfully ingested {len(documents)} documents into the Vector DB.")
        
    except Exception as e:
        print(f"Failed to ingest knowledge base: {e}")

if __name__ == "__main__":
    ingest_knowledge_base()
