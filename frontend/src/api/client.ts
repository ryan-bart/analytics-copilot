import type { QueryResponse, SchemaResponse } from "../types";

export async function queryData(question: string): Promise<QueryResponse> {
  const res = await fetch("/api/query", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
  if (!res.ok) throw new Error(`Query failed: ${res.statusText}`);
  return res.json();
}

export async function getSchema(): Promise<SchemaResponse> {
  const res = await fetch("/api/schema");
  if (!res.ok) throw new Error(`Schema fetch failed: ${res.statusText}`);
  return res.json();
}
