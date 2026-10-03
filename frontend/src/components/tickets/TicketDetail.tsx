import { Button } from "@/components/ui/Button";
import { formatTicketDate } from "@/lib/format";
import type { Ticket } from "@/types";

type TicketDetailProps = {
  ticket: Ticket;
  analyzing: boolean;
  retryingEmail: boolean;
  onRetryAnalysis: () => void;
  onRetryEmail: () => void;
};

export function TicketDetail({ ticket, analyzing, retryingEmail, onRetryAnalysis, onRetryEmail }: TicketDetailProps) {
  return (
    <section className="ticket-detail">
      <div className="detail-header">
        <div>
          <p className="eyebrow">Ticket #{ticket.id}</p>
          <h2>{ticket.subject}</h2>
          <p className="muted">{ticket.customer_email} · Created {formatTicketDate(ticket.created_at)}</p>
        </div>
        <span className="status-pill">{ticket.status.replace("_", " ")}</span>
      </div>
      <p className="ticket-description">{ticket.description}</p>
      <div className="tag-list">
        <span>Category: {ticket.category ?? "General"}</span>
        <span>Priority: {ticket.priority ?? "Medium"}</span>
        <span>Sentiment: {ticket.sentiment ?? "Neutral"}</span>
        <span>Team: {ticket.assigned_group ?? "General Support"}</span>
        <span>Email: {ticket.email_delivery_status?.replace("_", " ") ?? "not configured"}</span>
      </div>
      <div className={`decision-card ${ticket.requires_escalation ? "decision-escalated" : ""}`}>
        <div><p className="eyebrow">AI decision</p><h3>{ticket.requires_escalation ? "Human escalation required" : "Ready for agent resolution"}</h3><p>{ticket.requires_escalation ? ticket.escalation_reason : "Relevant company knowledge was found for an agent-reviewed response."}</p></div>
        <Button className="secondary compact" loading={analyzing} onClick={onRetryAnalysis}>Retry analysis</Button>
      </div>
      <section className="insight-card"><p className="eyebrow">AI summary</p><p className="draft-copy">{ticket.ai_summary ?? "No summary is available yet. Retry analysis to create one."}</p></section>
      <section className="insight-card"><p className="eyebrow">AI knowledge</p><h3>Relevant sources</h3>{ticket.knowledge_sources?.length ? <ol className="source-list">{ticket.knowledge_sources.map((source) => <li key={`${source.source}-${source.relevance}`}><div><strong>{source.title}</strong><p>{source.excerpt}</p></div><span>Relevance: {source.relevance.toFixed(2)}</span></li>)}</ol> : <p className="muted">Insufficient knowledge found. Human review is recommended.</p>}</section>
      {ticket.email_delivery_status === "failed" && <div className="email-retry"><p><strong>Email delivery failed.</strong> {ticket.email_delivery_detail ?? "SMTP delivery was unavailable."} The saved reply remains visible in the customer portal.</p><Button className="secondary compact" loading={retryingEmail} onClick={onRetryEmail}>Retry email</Button></div>}
      {ticket.agent_reply && <div className="saved-reply"><p className="eyebrow">Saved agent reply</p><p className="draft-copy">{ticket.agent_reply}</p></div>}
    </section>
  );
}
