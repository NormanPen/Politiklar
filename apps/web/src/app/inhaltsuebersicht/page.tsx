import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Inhaltsübersicht – Politiklar",
  description: "Übersicht über alle Bereiche, Themen und Datenangebote von Politiklar.",
};

export default function InhaltsuebersichtPage() {
  return (
    <div className="max-w-[1024px] mx-auto px-4 sm:px-6 py-12">
      <h1 className="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
        Inhaltsübersicht
      </h1>
      <p className="mt-4 text-base text-gray-600">
        Strukturierte Übersicht aller Inhalte, Dossiers, Gesetzesdokumentationen und statistischen Auswertungen auf Politiklar.
      </p>
    </div>
  );
}
