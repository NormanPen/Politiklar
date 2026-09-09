import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Dossier – Politiklar",
  description: "Dossiers und Themenschwerpunkte zu politischen Entscheidungen und Debatten.",
};

export default function DossierPage() {
  return (
    <div className="max-w-[1024px] mx-auto px-4 sm:px-6 py-12">
      <h1 className="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
        Dossier
      </h1>
      <p className="mt-4 text-base text-gray-600">
        Hier entstehen strukturierte Themendossiers mit verifizierten Quellen und neutral aufbereiteten Primärdaten.
      </p>
    </div>
  );
}
