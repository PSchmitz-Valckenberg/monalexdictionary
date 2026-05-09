"use client";

import { useState } from "react";
import Link from "next/link";
import { explainWord, getRelatedWords, type Explanation, type RelatedEntry } from "@/lib/api";

interface Props {
  word: string;
  definition: string;
  reversed?: boolean;
}

export default function WordCard({ word, definition, reversed = false }: Props) {
  const [explanation, setExplanation] = useState<Explanation | null>(null);
  const [loadingExplain, setLoadingExplain] = useState(false);
  const [errorExplain, setErrorExplain] = useState(false);
  const [open, setOpen] = useState(false);

  const [related, setRelated] = useState<RelatedEntry[] | null>(null);
  const [loadingRelated, setLoadingRelated] = useState(false);
  const [relatedOpen, setRelatedOpen] = useState(false);

  const primary = reversed ? definition : word;
  const secondary = reversed ? word : definition;

  async function handleExplain() {
    setOpen(true);
    if (explanation || loadingExplain) return;
    setLoadingExplain(true);
    setErrorExplain(false);
    try {
      const res = await explainWord(word, definition);
      setExplanation(res.explanation);
    } catch {
      setErrorExplain(true);
    } finally {
      setLoadingExplain(false);
    }
  }

  async function handleRelated() {
    setRelatedOpen((v) => !v);
    if (related !== null || loadingRelated) return;
    setLoadingRelated(true);
    try {
      const entries = await getRelatedWords(word, definition);
      setRelated(entries);
    } catch {
      setRelated([]);
    } finally {
      setLoadingRelated(false);
    }
  }

  return (
    <div className="border border-gray-200 dark:border-slate-700 rounded-xl p-4 hover:border-gray-300 dark:hover:border-slate-600 transition-colors bg-white dark:bg-slate-800/50">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          <p className="font-semibold text-gray-900 dark:text-slate-100">{primary}</p>
          <p className="text-sm text-gray-500 dark:text-slate-400 mt-0.5">{secondary}</p>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <button
            onClick={handleRelated}
            className="px-3 py-1.5 text-xs font-medium rounded-lg border border-gray-200 dark:border-slate-600 text-gray-500 dark:text-slate-400 hover:text-gray-900 dark:hover:text-slate-100 hover:border-gray-300 dark:hover:border-slate-500 transition-colors"
            title="Mots associés"
          >
            ≈ Associés
          </button>
          <button
            onClick={handleExplain}
            className="px-3 py-1.5 bg-[#ce1126] text-white text-xs font-medium rounded-lg hover:bg-[#a50e1f] transition-colors"
          >
            Assistant IA
          </button>
        </div>
      </div>

      {/* Related words */}
      {relatedOpen && (
        <div className="mt-4 pt-4 border-t border-gray-100 dark:border-slate-700">
          <p className="text-xs font-semibold uppercase tracking-widest text-gray-400 dark:text-slate-500 mb-2">
            Mots associés
          </p>
          {loadingRelated ? (
            <div className="flex gap-2 flex-wrap">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="h-7 w-20 bg-gray-100 dark:bg-slate-700 rounded-lg animate-pulse" />
              ))}
            </div>
          ) : related && related.length > 0 ? (
            <div className="flex flex-wrap gap-2">
              {related.map((r) => (
                <Link
                  key={r.word}
                  href={`/search?q=${encodeURIComponent(r.word)}`}
                  className="group px-3 py-1 rounded-lg text-sm bg-gray-50 dark:bg-slate-800 border border-gray-200 dark:border-slate-700 hover:border-[#ce1126] dark:hover:border-[#ce1126] transition-colors"
                >
                  <span className="text-gray-800 dark:text-slate-200 group-hover:text-[#ce1126] font-medium">
                    {r.word}
                  </span>
                  <span className="text-gray-400 dark:text-slate-500 text-xs ml-1.5">
                    {r.definition.length > 30 ? r.definition.slice(0, 30) + "…" : r.definition}
                  </span>
                </Link>
              ))}
            </div>
          ) : related && related.length === 0 ? (
            <p className="text-sm text-gray-400 dark:text-slate-500">Aucun mot associé trouvé.</p>
          ) : null}
        </div>
      )}

      {/* AI explanation */}
      {open && (
        <div className="mt-4 pt-4 border-t border-gray-100 dark:border-slate-700">
          {loadingExplain ? (
            <p className="text-sm text-gray-400 dark:text-slate-500 animate-pulse">Génération en cours…</p>
          ) : errorExplain ? (
            <div className="flex items-center gap-3">
              <p className="text-sm text-red-500">Erreur lors de la génération.</p>
              <button
                onClick={() => { setErrorExplain(false); handleExplain(); }}
                className="text-xs text-gray-400 dark:text-slate-500 underline hover:text-gray-600 dark:hover:text-slate-300"
              >
                Réessayer
              </button>
            </div>
          ) : explanation ? (
            <div className="space-y-3 text-sm">
              <p className="text-gray-700 dark:text-slate-300">{explanation.summary_fr}</p>

              {explanation.usage_notes.length > 0 && (
                <ul className="list-disc list-inside space-y-1 text-gray-600 dark:text-slate-400">
                  {explanation.usage_notes.map((note, i) => (
                    <li key={i}>{note}</li>
                  ))}
                </ul>
              )}

              {explanation.memory_tip && (
                <p className="text-amber-700 dark:text-amber-400 bg-amber-50 dark:bg-amber-900/20 rounded-lg px-3 py-2">
                  {explanation.memory_tip}
                </p>
              )}

              {explanation.practice_question && (
                <p className="text-gray-500 dark:text-slate-400 italic">{explanation.practice_question}</p>
              )}
            </div>
          ) : null}
        </div>
      )}
    </div>
  );
}
