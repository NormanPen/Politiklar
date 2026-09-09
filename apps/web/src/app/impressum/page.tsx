import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Impressum – Politiklar",
  description: "Impressum und rechtliche Angaben zu Politiklar.",
};

export default function ImpressumPage() {
  return (
    <div className="max-w-[1024px] mx-auto px-4 sm:px-6 py-12">
      <h1 className="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
        Impressum
      </h1>
      <p className="mt-4 text-base text-gray-600">
        Rechtliche Angaben und Kontaktinformationen gemäß § 5 TMG / DDG für die Plattform Politiklar.
      </p>
    </div>
  );
}
