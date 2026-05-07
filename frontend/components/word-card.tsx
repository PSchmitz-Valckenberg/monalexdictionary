"use client";

import { useState } from "react";
import { explainWord, type Explanation } from "@/lib/api";

interface Props {
  word: string;
  definition: string;
}

export default function WordCard({ word, definition }: Props) {
  const [explanation, setExplanation] = useState<Explanation | null>(null);
  const [loading, setLoading] = useState(false);
  const [open, setOpen] = useState(false);

  async function handleExplain() {
    setOpen(true);
    if (explanation) return;
    setLoading(true);
    try {
      const res = await explainWord(word, definition);
      setExplanation(res.explanation);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="border border-gray-200 rounded-xl p-4 hover:border-gray-300 transition-colors">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          <p className="font-semibold text-gray-900">{word}</p>
          <p className="text-sm text-gray-500 mt-0.5">{definition}</p>
        </div>
        <button
          onClick={handleExplain}
          className="shrink-0 px-3 py-1.5 bg-[#ce1126] text-white text-xs font-medium rounded-lg hover:bg-[#a50e1f] transition-colors"
        >
          Assistant IA
        </button>
      </div>

      {open && (
        <div className="mt-4 pt-4 border-t border-gray-100">
          {loading ? (
            <p className="text-sm text-gray-400 animate-pulse">Génération en cours…</p>
          ) : explanation ? (
            <div className="space-y-3 text-sm">
              <p className="text-gray-700">{explanation.summary_fr}</p>

              {explanation.usage_notes.length > 0 && (
                <ul className="list-disc list-inside space-y-1 text-gray-600">
                  {explanation.usage_notes.map((note, i) => (
                    <li key={i}>{note}</li>
                  ))}
                </ul>
              )}

              {explanation.examples.length > 0 && (
                <div className="space-y-1.5">
                  {explanation.examples.map((ex, i) => (
                    <div key={i} className="bg-gray-50 rounded-lg px-3 py-2">
                      <p className="text-gray-700">{ex.fr}</p>
                      <p className="text-[#ce1126] font-medium">{ex.monegasque}</p>
                    </div>
                  ))}
                </div>
              )}

              {explanation.memory_tip && (
                <p className="text-amber-700 bg-amber-50 rounded-lg px-3 py-2">
                  {explanation.memory_tip}
                </p>
              )}

              {explanation.practice_question && (
                <p className="text-gray-500 italic">{explanation.practice_question}</p>
              )}
            </div>
          ) : null}
        </div>
      )}
    </div>
  );
}
