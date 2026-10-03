# TODO: Implement module logic
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.schemas.ticket_schema import TicketCreate, TicketReplyCreate, TicketResponse
from app.services import ticket_service

router = APIRouter()

@router.post("/", response_model=TicketResponse)
def submit_ticket(ticket: TicketCreate, db: Session = Depends(get_db)):
    """
    Endpoint for customers to submit a new support ticket.
    """
    return ticket_service.create_ticket(db=db, ticket_in=ticket)

@router.get("/", response_model=List[TicketResponse])
def view_tickets(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Endpoint for agents to view all tickets in the queue.
    """
    return ticket_service.get_all_tickets(db=db, skip=skip, limit=limit)

@router.get("/{ticket_id}/draft-reply")
def get_draft_reply(ticket_id: int, db: Session = Depends(get_db)):
    """
    Endpoint for agents to get an AI-generated draft reply for a ticket.
    """
    from app.ai.engine import GeminiUnavailableError, generate_draft_reply
    
    ticket = ticket_service.get_ticket(db=db, ticket_id=ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
        
    try:
        triage = ticket_service.triage_from_ticket(ticket)
        context = "\n\n".join(source.get("excerpt", "") for source in (ticket.knowledge_sources or []))
        draft = generate_draft_reply(ticket.subject, ticket.description, triage, context)
    except GeminiUnavailableError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    return {"draft_reply": draft, "knowledge_sources": ticket.knowledge_sources or []}

@router.post("/{ticket_id}/reply", response_model=TicketResponse)
def send_agent_reply(
    ticket_id: int,
    reply: TicketReplyCreate,
    db: Session = Depends(get_db),
):
    """Save a reviewed reply and resolve or escalate the ticket."""
    if not reply.message.strip():
        raise HTTPException(status_code=422, detail="Reply message cannot be empty")
    try:
        ticket = ticket_service.resolve_ticket(db=db, ticket_id=ticket_id, reply_in=reply)
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

@router.post("/{ticket_id}/resolve", response_model=TicketResponse)
def explicitly_resolve_escalated_ticket(ticket_id: int, db: Session = Depends(get_db)):
    """Explicitly resolve an escalated ticket after the human agent has reviewed it."""
    try:
        ticket = ticket_service.explicitly_resolve_ticket(db=db, ticket_id=ticket_id)
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

@router.post("/{ticket_id}/retry-email", response_model=TicketResponse)
def retry_email_delivery(ticket_id: int, db: Session = Depends(get_db)):
    ticket = ticket_service.retry_resolution_email(db=db, ticket_id=ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket or saved reply not found")
    return ticket

@router.post("/{ticket_id}/reanalyze", response_model=TicketResponse)
def retry_ai_analysis(ticket_id: int, db: Session = Depends(get_db)):
    ticket = ticket_service.reanalyze_ticket(db=db, ticket_id=ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

@router.get("/{ticket_id}", response_model=TicketResponse)
def view_ticket_status(
    ticket_id: int,
    customer_email: str = Query(...),
    db: Session = Depends(get_db),
):
    """Return a customer's ticket when its ID and email address match."""
    ticket = ticket_service.get_ticket(db=db, ticket_id=ticket_id)
    if not ticket or ticket.customer_email.lower() != customer_email.lower():
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket
