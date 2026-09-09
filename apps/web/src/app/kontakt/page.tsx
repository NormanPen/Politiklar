import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Kontakt – Politiklar",
  description: "Kontaktieren Sie das Team hinter Politiklar bei Fragen oder Feedback.",
};

export default function KontaktPage() {
  return (
    <div className="max-w-[1024px] mx-auto px-4 sm:px-6 py-12">
      <h1 className="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
        Kontakt
      </h1>
      <p className="mt-4 text-base text-gray-600">
        Haben Sie Fragen, Anregungen oder Feedback zu unserer Plattform? Treten Sie gerne mit uns in Kontakt.
      </p>
    </div>
  );
}
