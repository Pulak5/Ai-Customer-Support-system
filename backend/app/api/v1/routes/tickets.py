# TODO: Implement module logic
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.schemas.ticket_schema import TicketCreate, TicketResponse
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