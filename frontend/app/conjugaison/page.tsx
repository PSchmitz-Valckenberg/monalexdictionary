import Link from "next/link";

const groups = [
  {
    title: "1er groupe",
    description: "Verbes en -er (ex: parler, chanter)",
    href: "/conjugaison/premier",
  },
  {
    title: "2ème groupe",
    description: "Verbes en -ir à l'infinitif (ex: finir)",
    href: "/conjugaison/deuxieme",
  },
  {
    title: "3ème groupe",
    description: "Verbes irréguliers (ex: venir, tenir)",
    href: "/conjugaison/troisieme",
  },
  {
    title: "Être",
    description: "Conjugaison complète du verbe être",
    href: "/conjugaison/etre",
  },
  {
    title: "Avoir",
    description: "Conjugaison complète du verbe avoir",
    href: "/conjugaison/avoir",
  },
];

export default function ConjugaisonPage() {
  return (
    <div className="max-w-3xl mx-auto px-4 py-10">
      <div className="mb-2 text-xs font-semibold uppercase tracking-widest text-[#ce1126]">
        Grammaire
      </div>
      <h1 className="text-3xl font-bold text-gray-900 mb-2">Conjugaison</h1>
      <p className="text-gray-500 mb-10">
        Tableaux de conjugaison des verbes en monégasque.
      </p>

      <div className="grid gap-4">
        {groups.map((g) => (
          <Link
            key={g.href}
            href={g.href}
            className="flex items-center justify-between border border-gray-200 rounded-xl p-5 hover:border-[#ce1126] hover:bg-red-50 transition-colors group"
          >
            <div>
              <p className="font-semibold text-gray-900 group-hover:text-[#ce1126]">
                {g.title}
              </p>
              <p className="text-sm text-gray-500 mt-0.5">{g.description}</p>
            </div>
            <svg
              className="w-5 h-5 text-gray-300 group-hover:text-[#ce1126]"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </Link>
        ))}
      </div>
    </div>
  );
}
