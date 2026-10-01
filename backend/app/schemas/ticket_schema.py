# TODO: Implement module logic
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# Schema for when a customer Submits a ticket (they only provide these 3 things)
class TicketCreate(BaseModel):
    customer_email: EmailStr
    subject: str
    description: str

class TicketReplyCreate(BaseModel):
    message: str

# Schema for returning ticket data back to the frontend
class TicketResponse(BaseModel):
    id: int
    customer_email: str
    subject: str
    description: str
    status: str
    
    category: Optional[str] = None
    priority: Optional[str] = None
    sentiment: Optional[str] = None
    assigned_group: Optional[str] = None
    agent_reply: Optional[str] = None
    email_delivery_status: Optional[str] = None
    
    created_at: datetime
    updated_at: Optional[datetime] = None

    # This tells Pydantic it's okay to read data directly from a SQLAlchemy model
    class Config:
        from_attributes = True
