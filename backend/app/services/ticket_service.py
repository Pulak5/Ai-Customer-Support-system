from sqlalchemy.orm import Session
from app.db.models.ticket_model import Ticket
from app.schemas.ticket_schema import TicketCreate, TicketReplyCreate

# NEW IMPORT: Bring in our AI engine
from app.ai.engine import TicketTriageResult, build_summary, fallback_triage, triage_ticket_text
from app.ai.rag.vector_db import similarity_search


def retrieve_knowledge(description: str) -> tuple[list[dict], str]:
    """Retrieve knowledge articles in a form that can be stored and shown to agents."""
    matches = similarity_search(description, k=3)
    sources = []
    for match in matches:
        metadata = match.get("metadata", {})
        content = match.get("content", "")
        sources.append({
            "title": metadata.get("title") or metadata.get("source", "Company knowledge").replace("_", " ").title(),
            "source": metadata.get("source", "knowledge_base"),
            "relevance": match.get("relevance", 0.0),
            "excerpt": content[:220].strip(),
        })
    context = "\n\n".join(match.get("content", "") for match in matches)
    return sources, context


def triage_from_ticket(ticket: Ticket) -> TicketTriageResult:
    return TicketTriageResult(
        category=ticket.category or "general",
        priority=ticket.priority or "medium",
        sentiment=ticket.sentiment or "neutral",
        assigned_group=ticket.assigned_group or "General Support",
        requires_escalation=bool(ticket.requires_escalation),
        escalation_reason=ticket.escalation_reason or "",
        confidence=0.0,
    )


def analyze_ticket(ticket: Ticket) -> Ticket:
    """Apply AI triage and RAG without letting provider errors lose the ticket."""
    try:
        triage_result = triage_ticket_text(ticket.subject, ticket.description)
    except Exception as error:
        print(f"AI triage unavailable; using safe fallback: {error}")
        triage_result = fallback_triage(ticket.subject, ticket.description)

    sources, _ = retrieve_knowledge(ticket.description)
    if not sources and not triage_result.requires_escalation:
        triage_result.requires_escalation = True
        triage_result.escalation_reason = "No sufficiently relevant company knowledge was found"

    ticket.category = triage_result.category
    ticket.priority = triage_result.priority
    ticket.sentiment = triage_result.sentiment
    ticket.assigned_group = triage_result.assigned_group
    ticket.requires_escalation = triage_result.requires_escalation
    ticket.escalation_reason = triage_result.escalation_reason or None
    ticket.ai_summary = build_summary(ticket.description, triage_result)
    ticket.knowledge_sources = sources
    ticket.status = "escalated" if triage_result.requires_escalation else "assigned"
    return ticket

def create_ticket(db: Session, ticket_in: TicketCreate) -> Ticket:
    
    db_ticket = Ticket(
        customer_email=ticket_in.customer_email,
        subject=ticket_in.subject,
        description=ticket_in.description,
        status="open",
    )
    analyze_ticket(db_ticket)
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    
    return db_ticket

def get_all_tickets(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Ticket).offset(skip).limit(limit).all()

def get_ticket(db: Session, ticket_id: int) -> Ticket:
    return db.query(Ticket).filter(Ticket.id == ticket_id).first()

def resolve_ticket(db: Session, ticket_id: int, reply_in: TicketReplyCreate) -> Ticket | None:
    ticket = get_ticket(db=db, ticket_id=ticket_id)
    if not ticket:
        return None
    if ticket.status == "resolved":
        raise ValueError("Resolved tickets cannot receive another response")

    if ticket.requires_escalation and reply_in.action != "send":
        raise ValueError("Escalated tickets require Send response before an agent explicitly resolves them")
    if not ticket.requires_escalation and reply_in.action != "resolve":
        raise ValueError("Assigned tickets must be resolved when their response is sent")

    ticket.agent_reply = reply_in.message.strip()
    ticket.status = "escalated" if ticket.requires_escalation else "resolved"
    ticket.email_delivery_status = "pending"
    ticket.email_delivery_detail = None
    db.commit()
    db.refresh(ticket)

    from app.services.email_service import send_resolution_email
    delivery = send_resolution_email(
        recipient=ticket.customer_email,
        subject=ticket.subject,
        reply=ticket.agent_reply,
    )
    ticket.email_delivery_status = delivery.status
    ticket.email_delivery_detail = delivery.detail or None
    db.commit()
    db.refresh(ticket)
    return ticket


def explicitly_resolve_ticket(db: Session, ticket_id: int) -> Ticket | None:
    """Close an escalated ticket only after an agent response has been saved."""
    ticket = get_ticket(db=db, ticket_id=ticket_id)
    if not ticket:
        return None
    if ticket.status == "resolved":
        raise ValueError("This ticket is already resolved")
    if not ticket.requires_escalation or not ticket.agent_reply:
        raise ValueError("Only escalated tickets with a saved agent response can be explicitly resolved")
    ticket.status = "resolved"
    db.commit()
    db.refresh(ticket)
    return ticket


def retry_resolution_email(db: Session, ticket_id: int) -> Ticket | None:
    ticket = get_ticket(db=db, ticket_id=ticket_id)
    if not ticket or not ticket.agent_reply:
        return None

    from app.services.email_service import send_resolution_email
    delivery = send_resolution_email(ticket.customer_email, ticket.subject, ticket.agent_reply)
    ticket.email_delivery_status = delivery.status
    ticket.email_delivery_detail = delivery.detail or None
    db.commit()
    db.refresh(ticket)
    return ticket


def reanalyze_ticket(db: Session, ticket_id: int) -> Ticket | None:
    ticket = get_ticket(db=db, ticket_id=ticket_id)
    if not ticket:
        return None
    analyze_ticket(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket
