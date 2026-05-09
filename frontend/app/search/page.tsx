"use client";

import { useState, useCallback, useRef, useEffect } from "react";
import { searchDictionary, type SearchResult } from "@/lib/api";
import WordCard from "@/components/word-card";

const HISTORY_KEY = "monalex-search-history";
const HISTORY_MAX = 8;

function useDebouncedCallback(fn: (q: string) => void, delay: number) {
  const fnRef = useRef(fn);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => { fnRef.current = fn; });
  useEffect(() => () => { if (timerRef.current) clearTimeout(timerRef.current); }, []);

  return useCallback((q: string) => {
    if (timerRef.current) clearTimeout(timerRef.current);
    timerRef.current = setTimeout(() => fnRef.current(q), delay);
  }, [delay]);
}

function loadHistory(): string[] {
  try {
    const parsed = JSON.parse(localStorage.getItem(HISTORY_KEY) ?? "[]");
    if (!Array.isArray(parsed)) return [];
    return parsed.filter((h): h is string => typeof h === "string");
  } catch {
    return [];
  }
}

function saveToHistory(term: string) {
  const prev = loadHistory().filter((h) => h !== term);
  const next = [term, ...prev].slice(0, HISTORY_MAX);
  localStorage.setItem(HISTORY_KEY, JSON.stringify(next));
}

type Direction = "fr-mon" | "mon-fr";

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [count, setCount] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [history, setHistory] = useState<string[]>([]);
  const [direction, setDirection] = useState<Direction>("fr-mon");

  useEffect(() => {
    setHistory(loadHistory());
  }, []);

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
      saveToHistory(q.trim());
      setHistory(loadHistory());
    } catch {
      setResults([]);
      setCount(0);
    } finally {
      setLoading(false);
    }
  }, []);

  const debouncedSearch = useDebouncedCallback(doSearch, 300);

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    const val = e.target.value;
    setQuery(val);
    debouncedSearch(val);
  }

  function handleHistoryClick(term: string) {
    setQuery(term);
    doSearch(term);
  }

  function clearHistory() {
    localStorage.removeItem(HISTORY_KEY);
    setHistory([]);
  }

  function toggleDirection() {
    setDirection((d) => (d === "fr-mon" ? "mon-fr" : "fr-mon"));
  }

  const isFrMon = direction === "fr-mon";
  const placeholder = isFrMon ? "Ex: bonjour, maison…" : "Ex: bon giurnu, cà…";
  const dirLabel = isFrMon ? "Français → Monégasque" : "Monégasque → Français";

  return (
    <div className="max-w-3xl mx-auto px-4 py-10">
      <div className="mb-2 text-xs font-semibold uppercase tracking-widest text-[#ce1126]">
        Dictionnaire
      </div>
      <h1 className="text-3xl font-bold text-gray-900 dark:text-slate-100 mb-2">Recherche</h1>
      <p className="text-gray-500 dark:text-slate-400 mb-8">
        Cherchez un mot français ou monégasque dans les 14 000 entrées.
      </p>

      <div className="bg-white dark:bg-slate-800 border border-gray-200 dark:border-slate-700 rounded-2xl p-6 mb-6 shadow-sm">
        {/* Direction toggle */}
        <div className="flex items-center justify-between mb-3">
          <label className="text-xs font-semibold uppercase tracking-widest text-gray-400 dark:text-slate-500">
            Mot ou traduction
          </label>
          <button
            onClick={toggleDirection}
            className="flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-medium text-gray-500 dark:text-slate-400 hover:text-gray-900 dark:hover:text-slate-100 hover:bg-gray-100 dark:hover:bg-slate-700 transition-colors border border-gray-200 dark:border-slate-600"
            title="Inverser la direction de recherche"
          >
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16V4m0 0L3 8m4-4l4 4M17 8v12m0 0l4-4m-4 4l-4-4" />
            </svg>
            {dirLabel}
          </button>
        </div>

        <input
          type="text"
          value={query}
          onChange={handleChange}
          placeholder={placeholder}
          className="w-full border border-gray-200 dark:border-slate-600 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-[#ce1126]/30 focus:border-[#ce1126] bg-white dark:bg-slate-700 text-gray-900 dark:text-slate-100 placeholder-gray-400 dark:placeholder-slate-500 transition-colors"
          autoFocus
        />

        {/* Search history — shown when input is empty */}
        {!query && history.length > 0 && (
          <div className="mt-4 pt-4 border-t border-gray-100 dark:border-slate-700">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-semibold uppercase tracking-widest text-gray-400 dark:text-slate-500">
                Recherches récentes
              </span>
              <button
                onClick={clearHistory}
                className="text-xs text-gray-400 dark:text-slate-500 hover:text-gray-600 dark:hover:text-slate-300 transition-colors"
              >
                Effacer
              </button>
            </div>
            <div className="flex flex-wrap gap-2">
              {history.map((term) => (
                <button
                  key={term}
                  onClick={() => handleHistoryClick(term)}
                  className="px-3 py-1 rounded-lg text-sm text-gray-700 dark:text-slate-300 bg-gray-100 dark:bg-slate-700 hover:bg-gray-200 dark:hover:bg-slate-600 transition-colors"
                >
                  {term}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {searched && (
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-slate-100">Résultats</h2>
            {count !== null && (
              <span className="text-sm text-gray-400 dark:text-slate-500">{count} affichés</span>
            )}
          </div>

          {loading ? (
            <div className="space-y-3">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="border border-gray-100 dark:border-slate-700 rounded-xl p-4 animate-pulse">
                  <div className="h-4 bg-gray-100 dark:bg-slate-700 rounded w-1/3 mb-2" />
                  <div className="h-3 bg-gray-100 dark:bg-slate-700 rounded w-2/3" />
                </div>
              ))}
            </div>
          ) : results.length === 0 ? (
            <p className="text-gray-400 dark:text-slate-500 text-sm">
              Aucun résultat pour «&nbsp;{query}&nbsp;».
            </p>
          ) : (
            <div className="space-y-3">
              {results.map((r) => (
                <WordCard
                  key={r.word}
                  word={r.word}
                  definition={r.definition}
                  reversed={direction === "mon-fr"}
                />
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
