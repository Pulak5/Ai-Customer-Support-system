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
    category: str = Field(description="One of billing, account, technical, shipping, subscription, security_fraud, or general")
    priority: str = Field(description="The priority: low, medium, high, or urgent")
    sentiment: str = Field(description="Customer sentiment: positive, neutral, negative, or angry")
    assigned_group: str = Field(description="The team: Billing Team, Account Team, Technical Support, Shipping Team, Subscription Team, Security Team, or General Support")
    requires_escalation: bool = Field(description="True when a human agent must review or act on the ticket")
    escalation_reason: str = Field(description="Brief reason for escalation, or an empty string if none is needed")
    confidence: float = Field(description="Confidence score between 0.0 and 1.0 that the ticket can be answered from company knowledge", default=0.0)


def fallback_triage(subject: str, description: str) -> TicketTriageResult:
    text = f"{subject} {description}".lower()
    if any(term in text for term in ("fraud", "unauthorized", "scam", "stolen", "kyc", "transaction")):
        return TicketTriageResult(category="security_fraud", priority="urgent", sentiment="angry", assigned_group="Security Team", requires_escalation=True, escalation_reason="Potential unauthorized financial or security activity", confidence=0.2)
    if any(term in text for term in ("charged", "payment", "refund", "billing", "invoice", "deducted")):
        return TicketTriageResult(category="billing", priority="high", sentiment="negative", assigned_group="Billing Team", requires_escalation=True, escalation_reason="Payment or billing review may be required", confidence=0.35)
    if any(term in text for term in ("password", "login", "account", "sign in")):
        return TicketTriageResult(category="account", priority="medium", sentiment="neutral", assigned_group="Account Team", requires_escalation=False, escalation_reason="", confidence=0.6)
    if any(term in text for term in ("shipping", "delivery", "order", "arrive")):
        return TicketTriageResult(category="shipping", priority="medium", sentiment="neutral", assigned_group="Shipping Team", requires_escalation=False, escalation_reason="", confidence=0.6)
    return TicketTriageResult(category="general", priority="medium", sentiment="neutral", assigned_group="General Support", requires_escalation=False, escalation_reason="", confidence=0.3)

def triage_ticket_text(subject: str, description: str) -> TicketTriageResult:
    # Keep the app usable until a Gemini API key has been configured.
    if not settings.GOOGLE_API_KEY or settings.GOOGLE_API_KEY == "your-api-key-here":
        print("No Google API key found. Skipping AI Triage.")
        return fallback_triage(subject, description)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert customer support triage system. Return a structured classification. Escalation is required for fraud, account-specific actions, payment disputes, credible security concerns, very angry customers, complex technical incidents, or when company knowledge is unlikely to be enough. Do not claim a ticket is resolved."),
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

def generate_draft_reply(subject: str, description: str, triage: TicketTriageResult, context: str) -> str:
    """Generates a draft reply using RAG context."""
    from app.ai.prompts.draft_reply_prompt import DRAFT_REPLY_PROMPT
    from langchain_core.output_parsers import StrOutputParser

    if not settings.GOOGLE_API_KEY or settings.GOOGLE_API_KEY == "your-api-key-here":
        return "This is a fallback draft reply since no Google API key was found."

    payload = {
        "context": context or "No relevant company knowledge was found.",
        "subject": subject,
        "description": description,
        "category": triage.category,
        "priority": triage.priority,
        "sentiment": triage.sentiment,
        "requires_escalation": triage.requires_escalation,
        "escalation_reason": triage.escalation_reason or "No escalation is required.",
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


def build_summary(description: str, triage: TicketTriageResult) -> str:
    """Create a concise, dependable agent-facing summary without inventing facts."""
    issue = " ".join(description.split())
    if len(issue) > 280:
        issue = f"{issue[:277].rstrip()}…"
    action = (
        f"Escalate to {triage.assigned_group}: {triage.escalation_reason}"
        if triage.requires_escalation
        else f"Recommended action: review and respond using {triage.assigned_group} guidance."
    )
    return f"Customer reports: {issue}\n\n{action}"
