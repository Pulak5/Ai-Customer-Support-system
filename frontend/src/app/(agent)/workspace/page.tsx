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
  const [analyzing, setAnalyzing] = useState(false);
  const [retryingEmail, setRetryingEmail] = useState(false);
  const [filter, setFilter] = useState("all");
  const [category, setCategory] = useState("all");
  const [team, setTeam] = useState("all");
  const [sentiment, setSentiment] = useState("all");
  const orderedTickets = useMemo(() => sortTicketsByPriority(tickets.filter((ticket) => {
    if (filter === "urgent" && ticket.priority?.toLowerCase() !== "urgent") return false;
    if (filter !== "all" && filter !== "urgent" && ticket.status !== filter) return false;
    if (category !== "all" && ticket.category !== category) return false;
    if (team !== "all" && ticket.assigned_group !== team) return false;
    if (sentiment !== "all" && ticket.sentiment !== sentiment) return false;
    return true;
  })), [tickets, filter, category, team, sentiment]);

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
      setSelected({ ...selected, knowledge_sources: response.knowledge_sources });
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
      const updatedTicket = await api.respondToTicket(selected.id, reply, selected.requires_escalation ? "send" : "resolve");
      setSelected(updatedTicket);
      setReply(updatedTicket.agent_reply ?? "");
      await refresh();
    } catch (reason) {
      setDraftError(reason instanceof Error ? reason.message : "Could not send the reply.");
    } finally {
      setSending(false);
    }
  }

  async function explicitlyResolveTicket() {
    if (!selected) return;
    setSending(true);
    setDraftError("");
    try {
      const updatedTicket = await api.explicitlyResolveTicket(selected.id);
      setSelected(updatedTicket);
      await refresh();
    } catch (reason) {
      setDraftError(reason instanceof Error ? reason.message : "Could not resolve the ticket.");
    } finally {
      setSending(false);
    }
  }

  async function retryAnalysis() {
    if (!selected) return;
    setAnalyzing(true);
    setDraftError("");
    try {
      const updatedTicket = await api.reanalyzeTicket(selected.id);
      setSelected(updatedTicket);
      setReply(updatedTicket.agent_reply ?? "");
      await refresh();
    } catch (reason) {
      setDraftError(reason instanceof Error ? reason.message : "Could not retry AI analysis.");
    } finally {
      setAnalyzing(false);
    }
  }

  async function retryEmail() {
    if (!selected) return;
    setRetryingEmail(true);
    setDraftError("");
    try {
      const updatedTicket = await api.retryEmail(selected.id);
      setSelected(updatedTicket);
      await refresh();
    } catch (reason) {
      setDraftError(reason instanceof Error ? reason.message : "Could not retry email delivery.");
    } finally {
      setRetryingEmail(false);
    }
  }

  return (
    <main className="workspace-shell">
      <nav className="top-nav"><Link href="/">Support Desk</Link><Link href="/dashboard">Customer portal</Link></nav>
      <header className="workspace-header"><div><p className="eyebrow">Agent workspace</p><h1>Ticket queue</h1><p className="muted">Review AI decisions, evidence, and customer-ready replies in one place.</p></div><button className="button secondary" onClick={() => void refresh()}>Refresh queue</button></header>
      {error && <p className="form-error">{error}</p>}
      <div className="workspace-grid">
        <aside className="queue-panel"><h2>Priority queue</h2><div className="filter-pills">{["all", "assigned", "urgent", "escalated", "resolved"].map((item) => <button key={item} className={filter === item ? "active" : ""} onClick={() => setFilter(item)}>{item}</button>)}</div><div className="filter-selects"><select aria-label="Filter by category" value={category} onChange={(event) => setCategory(event.target.value)}><option value="all">All categories</option>{[...new Set(tickets.map((ticket) => ticket.category).filter(Boolean))].map((value) => <option key={value} value={value ?? ""}>{value}</option>)}</select><select aria-label="Filter by team" value={team} onChange={(event) => setTeam(event.target.value)}><option value="all">All teams</option>{[...new Set(tickets.map((ticket) => ticket.assigned_group).filter(Boolean))].map((value) => <option key={value} value={value ?? ""}>{value}</option>)}</select><select aria-label="Filter by sentiment" value={sentiment} onChange={(event) => setSentiment(event.target.value)}><option value="all">All sentiment</option>{[...new Set(tickets.map((ticket) => ticket.sentiment).filter(Boolean))].map((value) => <option key={value} value={value ?? ""}>{value}</option>)}</select></div>{loading ? <p className="muted">Loading tickets…</p> : <TicketList tickets={orderedTickets} selectedId={selected?.id} onSelect={selectTicket} />}</aside>
        <section className="workspace-content">
          {selected ? <><TicketDetail ticket={selected} analyzing={analyzing} retryingEmail={retryingEmail} onRetryAnalysis={() => void retryAnalysis()} onRetryEmail={() => void retryEmail()} /><AiDraftViewer reply={reply} generating={draftLoading} sending={sending} escalationRequired={selected.requires_escalation} canExplicitlyResolve={selected.requires_escalation && Boolean(selected.agent_reply) && selected.status !== "resolved"} isResolved={selected.status === "resolved"} error={draftError} onGenerate={() => void generateDraft()} onReplyChange={setReply} onSend={() => void sendReply()} onResolve={() => void explicitlyResolveTicket()} /></> : <div className="empty-workspace"><h2>Select a ticket</h2><p>Choose a ticket in the queue to view its AI decision, source evidence, and suggested reply.</p></div>}
        </section>
      </div>
    </main>
  );
}
