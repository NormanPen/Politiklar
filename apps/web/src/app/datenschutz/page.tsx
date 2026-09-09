import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Datenschutz – Politiklar",
  description: "Datenschutzerklärung und Informationen zur Verarbeitung personenbezogener Daten.",
};

export default function DatenschutzPage() {
  return (
    <div className="max-w-[1024px] mx-auto px-4 sm:px-6 py-12">
      <h1 className="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
        Datenschutz
      </h1>
      <p className="mt-4 text-base text-gray-600">
        Informationen zur Erhebung, Verarbeitung und Nutzung von Daten gemäß den Vorgaben der DSGVO auf dieser Plattform.
      </p>
    </div>
  );
}
