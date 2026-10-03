"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { Button } from "@/components/ui/Button";
import { api } from "@/lib/api";
import { formatTicketDate } from "@/lib/format";
import type { Ticket } from "@/types";

const initialForm = { customer_email: "", subject: "", description: "" };

export default function CustomerDashboardPage() {
  const [form, setForm] = useState(initialForm);
  const [ticket, setTicket] = useState<Ticket | null>(null);
  const [trackingId, setTrackingId] = useState("");
  const [trackingEmail, setTrackingEmail] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [tracking, setTracking] = useState(false);
  const [error, setError] = useState("");

  async function submitTicket(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setError("");
    try {
      const created = await api.createTicket(form);
      setTicket(created);
      setTrackingId(String(created.id));
      setTrackingEmail(created.customer_email);
      setForm(initialForm);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Could not submit your ticket.");
    } finally {
      setSubmitting(false);
    }
  }

  async function trackTicket(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setTracking(true);
    setError("");
    try {
      setTicket(await api.getTicket(Number(trackingId), trackingEmail));
    } catch (reason) {
      setTicket(null);
      setError(reason instanceof Error ? reason.message : "Could not find that ticket.");
    } finally {
      setTracking(false);
    }
  }

  return (
    <main className="portal-shell">
      <nav className="top-nav"><Link href="/">Support Desk</Link><Link href="/workspace">Agent workspace</Link></nav>
      <header className="page-heading"><p className="eyebrow">Customer portal</p><h1>How can we help?</h1><p>Tell us what happened and we will route it to the right team.</p></header>
      <div className="customer-grid">
        <section className="card">
          <h2>Submit a request</h2>
          <form className="form-stack" onSubmit={submitTicket}>
            <label>Email<input required type="email" value={form.customer_email} onChange={(event) => setForm({ ...form, customer_email: event.target.value })} /></label>
            <label>Subject<input required value={form.subject} onChange={(event) => setForm({ ...form, subject: event.target.value })} /></label>
            <label>Describe your issue<textarea required rows={6} value={form.description} onChange={(event) => setForm({ ...form, description: event.target.value })} /></label>
            <Button type="submit" loading={submitting}>Submit ticket</Button>
          </form>
        </section>
        <section className="card">
          <h2>Track a request</h2>
          <form className="form-stack" onSubmit={trackTicket}>
            <label>Ticket ID<input required min="1" type="number" value={trackingId} onChange={(event) => setTrackingId(event.target.value)} /></label>
            <label>Email used to submit<input required type="email" value={trackingEmail} onChange={(event) => setTrackingEmail(event.target.value)} /></label>
            <Button type="submit" loading={tracking}>Check status</Button>
          </form>
          {error && <p className="form-error" role="alert">{error}</p>}
          {ticket && <div className="result-card">
            <p className="eyebrow">Ticket #{ticket.id}</p>
            <h3>Subject: {ticket.subject}</h3>
            <p className="status-line">Status: <strong>{ticket.status.replace("_", " ")}</strong></p>
            <p className="muted">Assigned to: {ticket.assigned_group ?? "General Support"}</p>
            <p className="muted">Created: {formatTicketDate(ticket.created_at)}</p>
            <p className="muted">Last updated: {formatTicketDate(ticket.updated_at)}</p>
            <div className="next-step">
              <p className="eyebrow">Next step</p>
              <p>{ticket.status === "resolved"
                ? "Your ticket has been resolved. Please review the support response below."
                : ticket.requires_escalation
                  ? "A support specialist will review your request and follow up with you."
                  : "Your request is assigned to the support team for review."}</p>
            </div>
            {ticket.agent_reply && <><p className="eyebrow">Support reply</p><p className="draft-copy">{ticket.agent_reply}</p></>}
            {ticket.email_delivery_status === "sent" && <p className="muted">A copy of this reply was sent by email.</p>}
          </div>}
        </section>
      </div>
    </main>
  );
}
