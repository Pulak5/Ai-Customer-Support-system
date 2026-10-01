"use client";

import { useCallback, useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { Ticket } from "@/types";

export function useTickets() {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const refresh = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      setTickets(await api.getTickets());
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Could not load tickets.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { void refresh(); }, [refresh]);
  return { tickets, loading, error, refresh };
}
