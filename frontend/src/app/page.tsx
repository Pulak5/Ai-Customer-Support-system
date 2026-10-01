import Link from "next/link";

export default function HomePage() {
  return (
    <main className="landing-shell">
      <section className="hero">
        <p className="eyebrow">AI Ticket System</p>
        <h1>Helpful support, from first message to resolution.</h1>
        <p className="lead">Submit a request, check its progress, or open the agent workspace.</p>
        <div className="action-row">
          <Link className="button primary" href="/dashboard">Customer portal</Link>
          <Link className="button secondary" href="/workspace">Agent workspace</Link>
        </div>
      </section>
    </main>
  );
}
