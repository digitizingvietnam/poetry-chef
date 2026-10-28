import type { AskRequest, AskResponse } from "./types";

const API_BASE =
  (import.meta.env.VITE_API_BASE as string | undefined) ??
  "http://localhost:8000";
const NORMALISED_BASE = API_BASE.endsWith("/") ? API_BASE : `${API_BASE}/`;
const ASK_ENDPOINT = new URL("ask", NORMALISED_BASE).toString();

export async function askQuestion(payload: AskRequest): Promise<AskResponse> {
  const response = await fetch(ASK_ENDPOINT, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || "Backend responded with an error");
  }

  return response.json() as Promise<AskResponse>;
}

