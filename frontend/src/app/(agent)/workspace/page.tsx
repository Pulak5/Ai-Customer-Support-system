"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { AiDraftViewer } from "@/components/ai/AiDraftViewer";
import { TicketDetail } from "@/components/tickets/TicketDetail";
import { TicketList } from "@/components/tickets/TicketList";
import { useTickets } from "@/hooks/useTickets";
import { api } from "@/lib/api";
import { sortTicketsByPriority } from "@/store/ticketStore";
import type { Ticket } from "@/types";

export default function AgentWorkspacePage() {
  const { tickets, loading, error, refresh } = useTickets();
  const [selected, setSelected] = useState<Ticket | null>(null);
  const [reply, setReply] = useState("");
  const [draftError, setDraftError] = useState("");
  const [draftLoading, setDraftLoading] = useState(false);
  const [sending, setSending] = useState(false);
  const orderedTickets = useMemo(() => sortTicketsByPriority(tickets), [tickets]);

  function selectTicket(ticket: Ticket) {
    setSelected(ticket);
    setReply(ticket.agent_reply ?? "");
    setDraftError("");
  }

  async function generateDraft() {
    if (!selected) return;
    setDraftLoading(true);
    setDraftError("");
    try {
      const response = await api.getDraftReply(selected.id);
      setReply(response.draft_reply);
    } catch (reason) {
      setDraftError(reason instanceof Error ? reason.message : "Could not generate a draft reply.");
    } finally {
      setDraftLoading(false);
    }
  }

  async function sendReply() {
    if (!selected || !reply.trim()) return;
    setSending(true);
    setDraftError("");
    try {
      const updatedTicket = await api.resolveTicket(selected.id, reply);
      setSelected(updatedTicket);
      setReply(updatedTicket.agent_reply ?? "");
      await refresh();
    } catch (reason) {
      setDraftError(reason instanceof Error ? reason.message : "Could not send the reply.");
    } finally {
      setSending(false);
    }
  }

  return (
    <main className="workspace-shell">
      <nav className="top-nav"><Link href="/">Support Desk</Link><Link href="/dashboard">Customer portal</Link></nav>
      <header className="workspace-header"><div><p className="eyebrow">Agent workspace</p><h1>Ticket queue</h1></div><button className="button secondary" onClick={() => void refresh()}>Refresh queue</button></header>
      {error && <p className="form-error">{error}</p>}
      <div className="workspace-grid">
        <aside className="queue-panel"><h2>Priority queue</h2>{loading ? <p className="muted">Loading tickets…</p> : <TicketList tickets={orderedTickets} selectedId={selected?.id} onSelect={selectTicket} />}</aside>
        <section className="workspace-content">
          {selected ? <><TicketDetail ticket={selected} /><AiDraftViewer reply={reply} generating={draftLoading} sending={sending} error={draftError} onGenerate={() => void generateDraft()} onReplyChange={setReply} onSend={() => void sendReply()} /></> : <div className="empty-workspace"><h2>Select a ticket</h2><p>Choose a ticket in the queue to view its details and create an AI reply.</p></div>}
        </section>
      </div>
    </main>
  );
}
