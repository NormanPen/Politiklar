import Link from "next/link";

export default function Home() {
  return (
    <div className="max-w-4xl mx-auto px-6 py-16 space-y-8 text-center">
      <div className="space-y-4">
        <h1 className="text-4xl sm:text-5xl font-extrabold text-gray-900 tracking-tight">
          Willkommen bei <span className="text-indigo-600">Politiklar</span>
        </h1>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          Civic-Tech-Plattform für transparente und lückenlos nachvollziehbare Informationen aus offiziellen politischen Primärquellen des Deutschen Bundestages.
        </p>
      </div>

      {/* Schnellzugriff auf Test-Routen */}
      <div className="pt-4 flex flex-wrap justify-center gap-4">
        <Link
          href="/politicians"
          className="px-5 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-sm shadow-sm transition"
        >
          Politiker-Demo (Jan van Aken) →
        </Link>
        <Link
          href="/state-test"
          className="px-5 py-3 rounded-xl bg-white hover:bg-gray-100 text-gray-800 font-semibold text-sm border border-gray-200 shadow-sm transition"
        >
          State-Management Test
        </Link>
        <Link
          href="/about"
          className="px-5 py-3 rounded-xl bg-white hover:bg-gray-100 text-gray-800 font-semibold text-sm border border-gray-200 shadow-sm transition"
        >
          Über uns
        </Link>
      </div>
    </div>
  );
}
