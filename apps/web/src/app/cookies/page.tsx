import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Cookies – Politiklar",
  description: "Informationen zur Verwendung von Cookies und Technologien auf Politiklar.",
};

export default function CookiesPage() {
  return (
    <div className="max-w-[1024px] mx-auto px-4 sm:px-6 py-12">
      <h1 className="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
        Cookies
      </h1>
      <p className="mt-4 text-base text-gray-600">
        Politiklar setzt auf minimale Datenspeicherung. Erfahren Sie hier mehr über unsere Cookie-Richtlinien und technische Einstellungen.
      </p>
    </div>
  );
}
