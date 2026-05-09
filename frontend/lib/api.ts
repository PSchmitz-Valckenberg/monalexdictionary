const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export interface SearchResult {
  word: string;
  definition: string;
}

export interface SearchResponse {
  query: string;
  count: number;
  results: SearchResult[];
}

export interface Explanation {
  summary_fr: string;
  usage_notes: string[];
  memory_tip: string;
  practice_question: string;
}

export interface RelatedEntry {
  word: string;
  definition: string;
}

export interface ExplainResponse {
  word: string;
  definition: string;
  model: string;
  explanation: Explanation;
}

export interface WordOfDay {
  date: string;
  word: string;
  definition: string;
  explanation: Explanation;
}

export async function searchDictionary(q: string): Promise<SearchResponse> {
  const res = await fetch(`${API_BASE}/api/search?q=${encodeURIComponent(q)}`);
  if (!res.ok) throw new Error("Search failed");
  return res.json();
}

export async function explainWord(
  word: string,
  definition: string
): Promise<ExplainResponse> {
  const res = await fetch(`${API_BASE}/api/ai/explain`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ word, definition }),
  });
  if (!res.ok) throw new Error("Explain failed");
  return res.json();
}

export async function getRelatedWords(
  word: string,
  definition: string
): Promise<RelatedEntry[]> {
  const res = await fetch(`${API_BASE}/api/ai/related`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ word, definition }),
  });
  if (!res.ok) throw new Error("Related failed");
  const data = await res.json();
  return data.related;
}

export async function getWordOfDay(): Promise<WordOfDay> {
  const res = await fetch(`${API_BASE}/api/ai/word-of-day`, {
    next: { revalidate: 3600 },
  });
  if (!res.ok) throw new Error("Word of day failed");
  return res.json();
}
