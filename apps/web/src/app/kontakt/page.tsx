import type { Metadata } from "next";
import ContactForm from "./ContactForm";

export const metadata: Metadata = {
  title: "Kontakt – Politiklar",
  description: "Kontaktieren Sie das Team hinter Politiklar bei Fragen, Anregungen oder Feedback.",
};

export default function KontaktPage() {
  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-12 sm:py-16">
      {/* Seiten-Header */}
      <div className="text-center max-w-2xl mx-auto mb-12 sm:mb-16">
        <span className="inline-block px-3 py-1 rounded-full text-xs font-medium tracking-wide uppercase bg-brand-cyan/20 text-brand-navy border border-brand-cyan/40 mb-3">
          Austausch & Dialog
        </span>
        <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-gray-900">
          Treten Sie mit uns in Kontakt
        </h1>
        <p className="mt-3 text-base sm:text-lg text-gray-600">
          Haben Sie Fragen zur Plattform, Anmerkungen zu Primärquellen oder Vorschläge für neue Funktionen? Wir freuen uns über Ihre Nachricht.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 lg:gap-12 items-start">
        {/* Formular-Spalte */}
        <div className="lg:col-span-7">
          <ContactForm />
        </div>

        {/* Infobereich-Spalte */}
        <div className="lg:col-span-5 space-y-6">
          <div className="bg-white border border-gray-200 rounded-2xl p-6 sm:p-7 shadow-sm space-y-4">
            <h2 className="text-lg font-bold text-gray-900 flex items-center gap-2">
              <span className="text-xl">💡</span> Über Ihre Nachricht
            </h2>
            <p className="text-sm text-gray-600 leading-relaxed">
              Politiklar ist ein unabhängiges Civic-Tech-Projekt zur transparenten Bereitstellung deutscher Bundestagsdaten.
            </p>
            <div className="border-t border-gray-100 pt-4 space-y-3 text-sm text-gray-600">
              <div className="flex items-start gap-3">
                <span className="font-semibold text-gray-800 shrink-0">Feedback:</span>
                <span>Anregungen zur Bedienung und Verbesserungen sind jederzeit willkommen.</span>
              </div>
              <div className="flex items-start gap-3">
                <span className="font-semibold text-gray-800 shrink-0">Fakten & Daten:</span>
                <span>Hinweise zu offiziellen Primärquellen oder Datenkorrekturen prüfen wir sorgfältig anhand des Quellarchivs.</span>
              </div>
              <div className="flex items-start gap-3">
                <span className="font-semibold text-gray-800 shrink-0">Antwortzeit:</span>
                <span>Wir bemühen uns, Anfragen innerhalb weniger Werktage zu beantworten.</span>
              </div>
            </div>
          </div>

          <div className="bg-gradient-to-br from-cyan-50/70 to-blue-50/40 border border-cyan-100 rounded-2xl p-6 shadow-sm">
            <h3 className="text-sm font-bold text-brand-navy uppercase tracking-wider mb-2">
              Direkter E-Mail-Kontakt
            </h3>
            <p className="text-sm text-gray-600 mb-3">
              Alternativ können Sie uns auch direkt eine E-Mail schreiben:
            </p>
            <a
              href="mailto:kontakt@politiklar.de"
              className="inline-flex items-center text-sm font-semibold text-cyan-800 hover:text-cyan-950 underline underline-offset-4"
            >
              kontakt@politiklar.de →
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
