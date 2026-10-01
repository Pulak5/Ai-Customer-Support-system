import type { Ticket } from "@/types";

export function TicketDetail({ ticket }: { ticket: Ticket }) {
  return (
    <section className="ticket-detail">
      <div className="detail-header">
        <div>
          <p className="eyebrow">Ticket #{ticket.id}</p>
          <h2>{ticket.subject}</h2>
          <p className="muted">{ticket.customer_email}</p>
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
      {ticket.agent_reply && <div className="saved-reply"><p className="eyebrow">Saved agent reply</p><p className="draft-copy">{ticket.agent_reply}</p></div>}
    </section>
  );
}
