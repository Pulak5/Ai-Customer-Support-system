import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.ai.engine import TicketTriageResult
from app.db.database import Base
from app.db.models.ticket_model import Ticket
from app.schemas.ticket_schema import TicketCreate, TicketReplyCreate
from app.services import ticket_service
from app.services.email_service import EmailDeliveryResult


def make_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine)()


def knowledge_match():
    return [{
        "content": "Use the password reset link from the sign-in screen.",
        "metadata": {"source": "password_reset", "title": "Password Reset Instructions"},
        "relevance": 0.91,
    }]


def test_normal_ticket_is_assigned_with_retrieved_knowledge(monkeypatch):
    db = make_session()
    monkeypatch.setattr(ticket_service, "similarity_search", lambda query, k: knowledge_match())
    monkeypatch.setattr(ticket_service, "triage_ticket_text", lambda subject, description: TicketTriageResult(
        category="account", priority="medium", sentiment="neutral", assigned_group="Account Team",
        requires_escalation=False, escalation_reason="", confidence=0.9,
    ))

    ticket = ticket_service.create_ticket(db, TicketCreate(
        customer_email="customer@example.com", subject="Password reset", description="I cannot sign in.",
    ))

    assert ticket.status == "assigned"
    assert ticket.requires_escalation is False
    assert ticket.knowledge_sources[0]["title"] == "Password Reset Instructions"
    assert "Customer reports" in ticket.ai_summary


def test_fraud_ticket_is_escalated_and_stays_escalated(monkeypatch):
    db = make_session()
    monkeypatch.setattr(ticket_service, "similarity_search", lambda query, k: knowledge_match())
    monkeypatch.setattr(ticket_service, "triage_ticket_text", lambda subject, description: TicketTriageResult(
        category="security_fraud", priority="urgent", sentiment="angry", assigned_group="Security Team",
        requires_escalation=True, escalation_reason="Potential unauthorized transaction", confidence=0.2,
    ))
    monkeypatch.setattr("app.services.email_service.send_resolution_email", lambda **kwargs: EmailDeliveryResult("sent"))

    ticket = ticket_service.create_ticket(db, TicketCreate(
        customer_email="customer@example.com", subject="Unauthorized charge", description="Someone charged my account.",
    ))
    updated = ticket_service.resolve_ticket(db, ticket.id, TicketReplyCreate(
        message="A specialist will review this.", action="send",
    ))

    assert ticket.status == "escalated"
    assert updated.status == "escalated"
    assert updated.agent_reply == "A specialist will review this."
    assert updated.email_delivery_status == "sent"

    resolved = ticket_service.explicitly_resolve_ticket(db, ticket.id)
    assert resolved.status == "resolved"


def test_escalated_ticket_cannot_be_auto_resolved(monkeypatch):
    db = make_session()
    monkeypatch.setattr(ticket_service, "similarity_search", lambda query, k: knowledge_match())
    monkeypatch.setattr(ticket_service, "triage_ticket_text", lambda subject, description: TicketTriageResult(
        category="security_fraud", priority="urgent", sentiment="angry", assigned_group="Security Team",
        requires_escalation=True, escalation_reason="Potential unauthorized transaction", confidence=0.2,
    ))
    ticket = ticket_service.create_ticket(db, TicketCreate(
        customer_email="customer@example.com", subject="Unauthorized charge", description="Someone charged my account.",
    ))

    with pytest.raises(ValueError, match="require Send response"):
        ticket_service.resolve_ticket(db, ticket.id, TicketReplyCreate(
            message="This should not resolve the case.", action="resolve",
        ))


def test_resolved_ticket_cannot_be_reopened_with_another_reply(monkeypatch):
    db = make_session()
    monkeypatch.setattr(ticket_service, "similarity_search", lambda query, k: knowledge_match())
    monkeypatch.setattr(ticket_service, "triage_ticket_text", lambda subject, description: TicketTriageResult(
        category="account", priority="medium", sentiment="neutral", assigned_group="Account Team",
        requires_escalation=False, escalation_reason="", confidence=0.9,
    ))
    monkeypatch.setattr("app.services.email_service.send_resolution_email", lambda **kwargs: EmailDeliveryResult("sent"))
    ticket = ticket_service.create_ticket(db, TicketCreate(
        customer_email="customer@example.com", subject="Password reset", description="I cannot sign in.",
    ))
    ticket_service.resolve_ticket(db, ticket.id, TicketReplyCreate(message="Your reset link is ready.", action="resolve"))

    with pytest.raises(ValueError, match="Resolved tickets cannot"):
        ticket_service.resolve_ticket(db, ticket.id, TicketReplyCreate(message="Another reply.", action="resolve"))


def test_low_knowledge_ticket_is_escalated(monkeypatch):
    db = make_session()
    monkeypatch.setattr(ticket_service, "similarity_search", lambda query, k: [])
    monkeypatch.setattr(ticket_service, "triage_ticket_text", lambda subject, description: TicketTriageResult(
        category="technical", priority="medium", sentiment="neutral", assigned_group="Technical Support",
        requires_escalation=False, escalation_reason="", confidence=0.3,
    ))

    ticket = ticket_service.create_ticket(db, TicketCreate(
        customer_email="customer@example.com", subject="Unusual setup", description="My custom integration is failing.",
    ))

    assert ticket.status == "escalated"
    assert ticket.requires_escalation is True
    assert ticket.escalation_reason == "No sufficiently relevant company knowledge was found"
