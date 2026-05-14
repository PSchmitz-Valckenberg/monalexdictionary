const API_BASE = (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000").replace(
  /\/+$/,
  ""
);

function apiUrl(path: string): string {
  return `${API_BASE}${path}`;
}

type FetchInit = RequestInit & {
  next?: {
    revalidate?: number;
  };
};

async function fetchJson<T>(url: string, init?: FetchInit): Promise<T> {
  const res = await fetch(url, init);
  if (!res.ok) {
    throw new Error(`Request failed with status ${res.status}`);
  }
  return res.json() as Promise<T>;
}

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
  return fetchJson<SearchResponse>(
    apiUrl(`/api/search?q=${encodeURIComponent(q)}`)
  );
}

export async function explainWord(
  word: string,
  definition: string
): Promise<ExplainResponse> {
  return fetchJson<ExplainResponse>(apiUrl("/api/ai/explain"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ word, definition }),
  });
}

export async function getRelatedWords(
  word: string,
  definition: string
): Promise<RelatedEntry[]> {
  const data = await fetchJson<{ related: RelatedEntry[] }>(
    apiUrl("/api/ai/related"),
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ word, definition }),
    }
  );
  return data.related;
}

export async function getWordOfDay(): Promise<WordOfDay> {
  return fetchJson<WordOfDay>(apiUrl("/api/ai/word-of-day"), {
    next: { revalidate: 3600 },
  });
}
