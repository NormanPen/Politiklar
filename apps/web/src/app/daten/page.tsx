import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Daten – Politiklar",
  description: "Offene Daten, Statistiken und Primärquellen zur parlamentarischen Arbeit.",
};

export default function DatenPage() {
  return (
    <div className="max-w-[1024px] mx-auto px-4 sm:px-6 py-12">
      <h1 className="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
        Daten
      </h1>
      <p className="mt-4 text-base text-gray-600">
        Umfassende Primärdaten und Auswertungen zu Drucksachen, Plenarprotokollen, namentlichen Abstimmungen und Biografien.
      </p>
    </div>
  );
}
