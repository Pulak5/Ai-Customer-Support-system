import type { Ticket } from "@/types";

export function sortTicketsByPriority(tickets: Ticket[]) {
  const priorityOrder: Record<string, number> = { urgent: 0, high: 1, medium: 2, low: 3 };
  return [...tickets].sort(
    (first, second) => (priorityOrder[first.priority?.toLowerCase() ?? "medium"] ?? 2)
      - (priorityOrder[second.priority?.toLowerCase() ?? "medium"] ?? 2),
  );
}
