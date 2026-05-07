import Image from "next/image";
import Link from "next/link";

export default function PremierGroupePage() {
  return (
    <div className="max-w-3xl mx-auto px-4 py-10">
      <Link href="/conjugaison" className="text-sm text-gray-400 hover:text-gray-600 mb-6 inline-flex items-center gap-1">
        ← Conjugaison
      </Link>
      <h1 className="text-3xl font-bold text-gray-900 mt-4 mb-2">1er groupe</h1>
      <p className="text-gray-500 mb-8">Verbes réguliers en -er (ex: parler, chanter, aimer)</p>
      <div className="rounded-2xl overflow-hidden border border-gray-200">
        <Image
          src="/conjugaison-1er.png"
          alt="Conjugaison 1er groupe"
          width={900}
          height={1200}
          className="w-full h-auto"
        />
      </div>
    </div>
  );
}
