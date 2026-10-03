export type KnowledgeSource = {
  title: string;
  source: string;
  relevance: number;
  excerpt: string;
};

export type Ticket = {
  id: number;
  customer_email: string;
  subject: string;
  description: string;
  status: string;
  category: string | null;
  priority: string | null;
  sentiment: string | null;
  assigned_group: string | null;
  agent_reply: string | null;
  email_delivery_status: string | null;
  email_delivery_detail: string | null;
  requires_escalation: boolean;
  escalation_reason: string | null;
  ai_summary: string | null;
  knowledge_sources: KnowledgeSource[] | null;
  created_at: string;
  updated_at: string | null;
};

export type TicketSubmission = Pick<Ticket, "customer_email" | "subject" | "description">;
