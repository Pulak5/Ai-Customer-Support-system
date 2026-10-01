# TODO: Implement module logic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from app.core.config import settings


class GeminiUnavailableError(RuntimeError):
    """Raised when Gemini is temporarily unavailable after retrying a fallback model."""


def _chat_model(model: str, temperature: float) -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model=model,
        google_api_key=settings.GOOGLE_API_KEY,
        temperature=temperature,
        max_retries=1,
    )


def _invoke_with_fallback(invoke, temperature: float):
    """Try the preferred Gemini model, then a stable lower-demand fallback."""
    models = [settings.GEMINI_CHAT_MODEL]
    if settings.GEMINI_FALLBACK_CHAT_MODEL != settings.GEMINI_CHAT_MODEL:
        models.append(settings.GEMINI_FALLBACK_CHAT_MODEL)

    last_error = None
    for model in models:
        try:
            return invoke(_chat_model(model, temperature))
        except Exception as error:
            if "503" not in str(error) and "UNAVAILABLE" not in str(error):
                raise
            last_error = error

    raise GeminiUnavailableError(
        "Gemini is temporarily busy. Please try generating the reply again in a moment."
    ) from last_error


# 1. Define exactly what we want the AI to extract
class TicketTriageResult(BaseModel):
    category: str = Field(description="The category: billing, technical, sales, or general")
    priority: str = Field(description="The priority: low, medium, high, or urgent")
    sentiment: str = Field(description="Customer sentiment: happy, neutral, frustrated, or angry")
    confidence: float = Field(description="Confidence score between 0.0 and 1.0 that the RAG context fully answers the question", default=0.0)

def triage_ticket_text(subject: str, description: str) -> TicketTriageResult:
    # Keep the app usable until a Gemini API key has been configured.
    if not settings.GOOGLE_API_KEY or settings.GOOGLE_API_KEY == "your-api-key-here":
        print("No Google API key found. Skipping AI Triage.")
        return TicketTriageResult(category="general", priority="medium", sentiment="neutral")

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert customer support triage system. Analyze the ticket and extract the category, priority, and sentiment."),
        ("human", "Subject: {subject}\n\nDescription: {description}")
    ])

    def invoke(llm):
        structured_llm = llm.with_structured_output(
            TicketTriageResult.model_json_schema(), method="json_schema"
        )
        return (prompt | structured_llm).invoke(
            {"subject": subject, "description": description}
        )

    result = _invoke_with_fallback(invoke, temperature=0)

    return TicketTriageResult.model_validate(result)

def generate_draft_reply(subject: str, description: str) -> str:
    """Generates a draft reply using RAG context."""
    from app.ai.rag.vector_db import similarity_search
    from app.ai.prompts.draft_reply_prompt import DRAFT_REPLY_PROMPT
    from langchain_core.output_parsers import StrOutputParser

    if not settings.GOOGLE_API_KEY or settings.GOOGLE_API_KEY == "your-api-key-here":
        return "This is a fallback draft reply since no Google API key was found."

    # 1. Get relevant context from RAG
    relevant_docs = similarity_search(description, k=2)
    context_text = "\n\n".join([doc["content"] for doc in relevant_docs])

    payload = {
        "context": context_text,
        "subject": subject,
        "description": description,
    }
    result = _invoke_with_fallback(
        lambda llm: (DRAFT_REPLY_PROMPT | llm | StrOutputParser()).invoke(payload),
        temperature=0.7,
    )
    return result

def generate_thread_summary(thread_history: str) -> str:
    """Condenses the entire ticket history into a 3-bullet-point summary."""
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser

    if not settings.GOOGLE_API_KEY or settings.GOOGLE_API_KEY == "your-api-key-here":
        return "- Simulated Summary Point 1\n- Simulated Summary Point 2\n- Simulated Summary Point 3"

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an AI assistant helping customer support agents. Summarize the following email thread into exactly 3 concise bullet points focusing on the core issue and what has been done so far."),
        ("human", "{thread}")
    ])
    
    return _invoke_with_fallback(
        lambda llm: (prompt | llm | StrOutputParser()).invoke({"thread": thread_history}),
        temperature=0.3,
    )
