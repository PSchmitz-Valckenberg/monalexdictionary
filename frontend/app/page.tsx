import Link from "next/link";
import { getWordOfDay, type WordOfDay } from "@/lib/api";

async function WordOfDaySection() {
  let wotd: WordOfDay | null = null;
  try {
    wotd = await getWordOfDay();
  } catch {
    return null;
  }

  return (
    <section className="max-w-3xl mx-auto px-4 py-12">
      <div className="mb-3 text-xs font-semibold uppercase tracking-widest text-[#ce1126]">
        Mot du jour — {wotd.date}
      </div>
      <div className="border border-gray-200 rounded-2xl p-6 shadow-sm">
        <p className="text-xl font-bold text-gray-900">{wotd.word}</p>
        <p className="text-gray-500 mt-1 mb-5">{wotd.definition}</p>

        <div className="space-y-4 text-sm">
          <p className="text-gray-700">{wotd.explanation.summary_fr}</p>

          {wotd.explanation.examples.length > 0 && (
            <div className="space-y-2">
              {wotd.explanation.examples.map((ex, i) => (
                <div key={i} className="bg-gray-50 rounded-xl px-4 py-3">
                  <p className="text-gray-600">{ex.fr}</p>
                  <p className="text-[#ce1126] font-medium mt-0.5">{ex.monegasque}</p>
                </div>
              ))}
            </div>
          )}

          {wotd.explanation.memory_tip && (
            <p className="text-amber-700 bg-amber-50 rounded-xl px-4 py-3">
              {wotd.explanation.memory_tip}
            </p>
          )}
        </div>
      </div>
    </section>
  );
}

export default function HomePage() {
  return (
    <>
      {/* Hero with Monaco background */}
      <section
        className="relative text-white"
        style={{
          backgroundImage: "url('/monaco-bg.jpeg')",
          backgroundSize: "cover",
          backgroundPosition: "center",
        }}
      >
        <div className="absolute inset-0 bg-black/55" />
        <div className="relative max-w-3xl mx-auto px-4 py-24">
          <p className="text-xs font-semibold uppercase tracking-widest text-[#ce1126] mb-4">
            Monaco linguistique
          </p>
          <h1 className="text-5xl font-bold mb-5">Monalex</h1>
          <p className="text-lg text-gray-200 mb-4 max-w-xl leading-relaxed">
            Le premier dictionnaire numérique ouvert du monégasque — avec plus
            de 14 000 entrées, des tableaux de conjugaison et un assistant IA
            pour apprendre la langue de Monaco.
          </p>
          <p className="text-sm text-gray-400 mb-10 max-w-lg">
            Le monégasque (u munegascu) est une langue ligure parlée en
            Principauté de Monaco. Explorez son vocabulaire, ses structures et
            son histoire.
          </p>
          <div className="flex gap-3">
            <Link
              href="/search"
              className="px-6 py-3 bg-[#ce1126] text-white font-semibold rounded-xl hover:bg-[#a50e1f] transition-colors"
            >
              Rechercher
            </Link>
            <Link
              href="/conjugaison"
              className="px-6 py-3 border border-white/30 text-white font-semibold rounded-xl hover:bg-white/10 transition-colors"
            >
              Conjugaison
            </Link>
          </div>
        </div>
      </section>

      {/* Word of day */}
      <WordOfDaySection />

      {/* About */}
      <section className="max-w-3xl mx-auto px-4 py-12 border-t border-gray-100">
        <h2 className="text-xl font-bold text-gray-900 mb-6">
          Histoire de la langue
        </h2>
        <div className="space-y-4 text-sm text-gray-600 leading-relaxed">
          <p>
            Le monégasque (u munegascu) est un dialecte ligure, parlé en
            Principauté de Monaco. Les premières traces écrites apparaissent
            entre 1721 et 1729 dans la correspondance du prince Antoine avec sa
            fille Louise-Hippolyte, ainsi que dans quelques actes notariés —
            mais la langue demeure avant tout orale.
          </p>
          <p>
            À partir de 1860, la population du Rocher passe de 1 200 habitants
            à 22 000 en 1880. Le monégasque se retrouve menacé par l&apos;afflux
            massif de travailleurs étrangers et par le développement d&apos;un
            pidgin mélangeant le provençal, le piémontais, le corse et le
            ligure. À cette époque, le monégasque est banni de l&apos;école et
            les parents encouragent leurs enfants à parler français.
          </p>
          <p>
            En 1927, Louis Notari entreprend la codification écrite de la langue
            en s&apos;inspirant de l&apos;écriture du français et de
            l&apos;italien. Aujourd&apos;hui, le monégasque est enseigné dans
            toutes les écoles de la Principauté et bénéficie d&apos;un
            renouveau actif porté par le Conseil National de la Langue
            Monégasque.
          </p>
        </div>
      </section>
    </>
  );
}
