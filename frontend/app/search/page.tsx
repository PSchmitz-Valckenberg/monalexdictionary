"use client";

import { useState, useCallback } from "react";
import { searchDictionary, type SearchResult } from "@/lib/api";
import WordCard from "@/components/word-card";

function useDebounce<T extends (...args: never[]) => void>(fn: T, delay: number): T {
  let timer: ReturnType<typeof setTimeout>;
  return ((...args: Parameters<T>) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  }) as T;
}

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [count, setCount] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  const doSearch = useCallback(async (q: string) => {
    if (!q.trim()) {
      setResults([]);
      setCount(null);
      setSearched(false);
      return;
    }
    setLoading(true);
    setSearched(true);
    try {
      const data = await searchDictionary(q.trim());
      setResults(data.results);
      setCount(data.count);
    } catch {
      setResults([]);
      setCount(0);
    } finally {
      setLoading(false);
    }
  }, []);

  const debouncedSearch = useDebounce(doSearch, 300);

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    const val = e.target.value;
    setQuery(val);
    debouncedSearch(val);
  }

  return (
    <div className="max-w-3xl mx-auto px-4 py-10">
      <div className="mb-2 text-xs font-semibold uppercase tracking-widest text-[#ce1126]">
        Dictionnaire
      </div>
      <h1 className="text-3xl font-bold text-gray-900 mb-2">Recherche</h1>
      <p className="text-gray-500 mb-8">
        Cherchez un mot français ou monégasque dans le dictionnaire.
      </p>

      <div className="bg-white border border-gray-200 rounded-2xl p-6 mb-8 shadow-sm">
        <label className="block text-xs font-semibold uppercase tracking-widest text-gray-400 mb-3">
          Mot ou traduction
        </label>
        <div className="flex gap-3">
          <input
            type="text"
            value={query}
            onChange={handleChange}
            placeholder="Ex: bonjour, maison…"
            className="flex-1 border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-[#ce1126]/30 focus:border-[#ce1126]"
            autoFocus
          />
        </div>
      </div>

      {searched && (
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Résultats</h2>
            {count !== null && (
              <span className="text-sm text-gray-400">{count} affichés</span>
            )}
          </div>

          {loading ? (
            <div className="space-y-3">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="border border-gray-100 rounded-xl p-4 animate-pulse">
                  <div className="h-4 bg-gray-100 rounded w-1/3 mb-2" />
                  <div className="h-3 bg-gray-100 rounded w-2/3" />
                </div>
              ))}
            </div>
          ) : results.length === 0 ? (
            <p className="text-gray-400 text-sm">
              Aucun résultat pour «&nbsp;{query}&nbsp;».
            </p>
          ) : (
            <div className="space-y-3">
              {results.map((r, i) => (
                <WordCard key={i} word={r.word} definition={r.definition} />
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
