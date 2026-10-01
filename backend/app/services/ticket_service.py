from sqlalchemy.orm import Session
from app.db.models.ticket_model import Ticket
from app.schemas.ticket_schema import TicketCreate

# NEW IMPORT: Bring in our AI engine
from app.ai.engine import triage_ticket_text

def create_ticket(db: Session, ticket_in: TicketCreate) -> Ticket:
    
    # ---  THE AI MAGIC HAPPENS HERE ---
    triage_result = triage_ticket_text(subject=ticket_in.subject, description=ticket_in.description)
    
    # Convert incoming schema to database model, and inject AI findings
    db_ticket = Ticket(
        customer_email=ticket_in.customer_email,
        subject=ticket_in.subject,
        description=ticket_in.description,
        
        # Save AI generated fields to the DB
        category=triage_result.category,
        priority=triage_result.priority,
        sentiment=triage_result.sentiment
    )
    
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    
    return db_ticket

def get_all_tickets(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Ticket).offset(skip).limit(limit).all()