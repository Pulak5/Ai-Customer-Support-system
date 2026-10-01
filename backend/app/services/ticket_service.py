from sqlalchemy.orm import Session
from app.db.models.ticket_model import Ticket
from app.schemas.ticket_schema import TicketCreate, TicketReplyCreate

# NEW IMPORT: Bring in our AI engine
from app.ai.engine import triage_ticket_text

def create_ticket(db: Session, ticket_in: TicketCreate) -> Ticket:
    
    # ---  THE AI MAGIC HAPPENS HERE ---
    triage_result = triage_ticket_text(subject=ticket_in.subject, description=ticket_in.description)
    
    # Routing Logic
    assigned_group = "General Support"
    category_lower = triage_result.category.lower() if triage_result.category else ""
    if "billing" in category_lower or "finance" in category_lower:
        assigned_group = "Billing Team"
    elif "technical" in category_lower or "bug" in category_lower or "tech" in category_lower:
        assigned_group = "Tech Support"
    elif "sales" in category_lower or "pricing" in category_lower:
        assigned_group = "Sales Team"

    # Auto-Reply Guardrails
    status = "open"
    if triage_result.priority.lower() == "low" and triage_result.confidence > 0.95:
        from app.ai.engine import generate_draft_reply
        auto_reply = generate_draft_reply(ticket_in.subject, ticket_in.description)
        print(f"Auto-reply sent to {ticket_in.customer_email}: {auto_reply}")
        status = "resolved"

    # Convert incoming schema to database model, and inject AI findings
    db_ticket = Ticket(
        customer_email=ticket_in.customer_email,
        subject=ticket_in.subject,
        description=ticket_in.description,
        status=status,
        
        # Save AI generated fields to the DB
        category=triage_result.category,
        priority=triage_result.priority,
        sentiment=triage_result.sentiment,
        assigned_group=assigned_group
    )
    
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

    ticket.agent_reply = reply_in.message.strip()
    ticket.status = "resolved"
    ticket.email_delivery_status = "pending"
    db.commit()
    db.refresh(ticket)

    from app.services.email_service import send_resolution_email
    delivery = send_resolution_email(
        recipient=ticket.customer_email,
        subject=ticket.subject,
        reply=ticket.agent_reply,
    )
    ticket.email_delivery_status = delivery.status
    db.commit()
    db.refresh(ticket)
    return ticket
