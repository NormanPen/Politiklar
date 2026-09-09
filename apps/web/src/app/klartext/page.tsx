import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Klartext – Politiklar",
  description: "Verständliche Zusammenfassungen komplexer parlamentarischer Vorgänge.",
};

export default function KlartextPage() {
  return (
    <div className="max-w-[1024px] mx-auto px-4 sm:px-6 py-12">
      <h1 className="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
        Klartext
      </h1>
      <p className="mt-4 text-base text-gray-600">
        Verständliche und sachliche Zusammenfassungen ohne Fachjargon – direkt verknüpft mit den offiziellen Primärquellen.
      </p>
    </div>
  );
}
