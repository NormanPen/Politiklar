import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Kompass – Politiklar",
  description: "Orientierung und Einordnung politischer Positionen und Sachverhalte.",
};

export default function KompassPage() {
  return (
    <div className="max-w-[1024px] mx-auto px-4 sm:px-6 py-12">
      <h1 className="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
        Kompass
      </h1>
      <p className="mt-4 text-base text-gray-600">
        Der Politiklar-Kompass bietet Orientierung zu Abstimmungsverhalten, Fraktionslinien und politischen Schwerpunkten.
      </p>
    </div>
  );
}
