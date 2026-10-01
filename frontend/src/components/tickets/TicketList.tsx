"use client";

import type { Ticket } from "@/types";

type TicketListProps = {
  tickets: Ticket[];
  selectedId?: number;
  onSelect: (ticket: Ticket) => void;
};

export function TicketList({ tickets, selectedId, onSelect }: TicketListProps) {
  if (!tickets.length) return <p className="empty-state">No tickets yet.</p>;

  return (
    <div className="ticket-list">
      {tickets.map((ticket) => (
        <button
          className={`ticket-row ${ticket.id === selectedId ? "selected" : ""}`}
          key={ticket.id}
          onClick={() => onSelect(ticket)}
        >
          <span className="ticket-row-title">{ticket.subject}</span>
          <span className="ticket-row-meta">#{ticket.id} · {ticket.priority ?? "unassigned"}</span>
        </button>
      ))}
    </div>
  );
}
