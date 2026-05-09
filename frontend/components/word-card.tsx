"use client";

import { useState } from "react";
import { explainWord, type Explanation } from "@/lib/api";

interface Props {
  word: string;
  definition: string;
  reversed?: boolean;
}

export default function WordCard({ word, definition, reversed = false }: Props) {
  const [explanation, setExplanation] = useState<Explanation | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);
  const [open, setOpen] = useState(false);

  const primary = reversed ? definition : word;
  const secondary = reversed ? word : definition;

  async function handleExplain() {
    setOpen(true);
    if (explanation || loading) return;
    setLoading(true);
    setError(false);
    try {
      const res = await explainWord(word, definition);
      setExplanation(res.explanation);
    } catch {
      setError(true);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="border border-gray-200 dark:border-slate-700 rounded-xl p-4 hover:border-gray-300 dark:hover:border-slate-600 transition-colors bg-white dark:bg-slate-800/50">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          <p className="font-semibold text-gray-900 dark:text-slate-100">{primary}</p>
          <p className="text-sm text-gray-500 dark:text-slate-400 mt-0.5">{secondary}</p>
        </div>
        <button
          onClick={handleExplain}
          className="shrink-0 px-3 py-1.5 bg-[#ce1126] text-white text-xs font-medium rounded-lg hover:bg-[#a50e1f] transition-colors"
        >
          Assistant IA
        </button>
      </div>

      {open && (
        <div className="mt-4 pt-4 border-t border-gray-100 dark:border-slate-700">
          {loading ? (
            <p className="text-sm text-gray-400 dark:text-slate-500 animate-pulse">Génération en cours…</p>
          ) : error ? (
            <div className="flex items-center gap-3">
              <p className="text-sm text-red-500">Erreur lors de la génération.</p>
              <button
                onClick={() => { setError(false); handleExplain(); }}
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

              {explanation.examples.length > 0 && (
                <div className="space-y-1.5">
                  {explanation.examples.map((ex, i) => (
                    <div key={i} className="bg-gray-50 dark:bg-slate-800 rounded-lg px-3 py-2">
                      <p className="text-gray-700 dark:text-slate-300">{ex.fr}</p>
                      <p className="text-[#ce1126] font-medium">{ex.monegasque}</p>
                    </div>
                  ))}
                </div>
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
