# TODO: Implement module logic
from sqlalchemy import Boolean, Column, DateTime, Integer, JSON, String, Text, func
from app.db.database import Base

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    customer_email = Column(String, index=True, nullable=False)
    subject = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    
    # Standard Ticket Metadata
    status = Column(String, default="open")
    
    # AI Generated Fields (These will be populated by our AI Engine)
    category = Column(String, nullable=True)     # e.g., billing, technical
    priority = Column(String, nullable=True)     # e.g., low, high, urgent
    sentiment = Column(String, nullable=True)    # e.g., angry, neutral
    assigned_group = Column(String, nullable=True) # e.g., Billing Team, Tech Support
    agent_reply = Column(Text, nullable=True)
    email_delivery_status = Column(String, nullable=True)
    email_delivery_detail = Column(Text, nullable=True)
    requires_escalation = Column(Boolean, default=False, nullable=False)
    escalation_reason = Column(Text, nullable=True)
    ai_summary = Column(Text, nullable=True)
    knowledge_sources = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
