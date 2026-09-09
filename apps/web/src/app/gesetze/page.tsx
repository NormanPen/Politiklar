import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Gesetze – Politiklar",
  description: "Gesetzesvorhaben, parlamentarische Abläufe und Abstimmungsergebnisse.",
};

export default function GesetzePage() {
  return (
    <div className="max-w-[1024px] mx-auto px-4 sm:px-6 py-12">
      <h1 className="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
        Gesetze
      </h1>
      <p className="mt-4 text-base text-gray-600">
        Übersicht über Gesetzesinitiativen, Beschlussempfehlungen und Abstimmungen des Deutschen Bundestages.
      </p>
    </div>
  );
}
