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
  created_at: string;
  updated_at: string | null;
};

export type TicketSubmission = Pick<Ticket, "customer_email" | "subject" | "description">;
