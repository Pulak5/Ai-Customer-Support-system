# TODO: Implement module logic
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from typing import Literal, Optional
from datetime import datetime

# Schema for when a customer Submits a ticket (they only provide these 3 things)
class TicketCreate(BaseModel):
    customer_email: EmailStr
    subject: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=5000)

    @field_validator("subject", "description")
    @classmethod
    def require_meaningful_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field cannot be empty")
        return value

class TicketReplyCreate(BaseModel):
    message: str = Field(min_length=1, max_length=5000)
    action: Literal["send", "resolve"] = "resolve"

    @field_validator("message")
    @classmethod
    def require_reply_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Reply message cannot be empty")
        return value

class KnowledgeSource(BaseModel):
    title: str
    source: str
    relevance: float
    excerpt: str

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
    email_delivery_detail: Optional[str] = None
    requires_escalation: bool = False
    escalation_reason: Optional[str] = None
    ai_summary: Optional[str] = None
    knowledge_sources: Optional[list[KnowledgeSource]] = None
    
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
