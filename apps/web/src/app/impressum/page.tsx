import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Impressum – Politiklar",
  description: "Rechtliche Angaben und Anbieterkennzeichnung gemäß § 5 DDG für Politiklar.",
};

export default function ImpressumPage() {
  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12 sm:py-16">
      {/* Header */}
      <div className="text-center max-w-2xl mx-auto mb-12 sm:mb-16">
        <span className="inline-block px-3 py-1 rounded-full text-xs font-medium tracking-wide uppercase bg-brand-cyan/20 text-brand-navy border border-brand-cyan/40 mb-3">
          Rechtliche Angaben
        </span>
        <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-gray-900">
          Impressum
        </h1>
        <p className="mt-3 text-base sm:text-lg text-gray-600">
          Angaben gemäß § 5 Digitale-Dienste-Gesetz (DDG) und § 18 Abs. 2 Medienstaatsvertrag (MStV).
        </p>
      </div>

      <div className="space-y-10 text-gray-700 leading-relaxed text-base">
        {/* Angaben gemäß § 5 DDG */}
        <section className="bg-white border border-gray-200 rounded-2xl p-6 sm:p-8 shadow-sm">
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            Diensteanbieter / Betreiber der Plattform
          </h2>
          <div className="text-sm sm:text-base space-y-1.5 text-gray-800">
            <p className="font-semibold text-lg text-gray-900">Norman Pendzich</p>
            <p>Maybachstraße 1</p>
            <p>40470 Düsseldorf</p>
            <p>Nordrhein-Westfalen, Deutschland</p>
          </div>
        </section>

        {/* Kontakt */}
        <section className="bg-white border border-gray-200 rounded-2xl p-6 sm:p-8 shadow-sm">
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            Kontakt
          </h2>
          <div className="text-sm sm:text-base space-y-2 text-gray-800">
            <p>
              <span className="font-medium text-gray-600">Telefon:</span> +49 (0) 151 61449132
            </p>
            <p>
              <span className="font-medium text-gray-600">E-Mail:</span>{" "}
              <a href="mailto:normanpendzich@gmail.com" className="text-cyan-800 hover:text-cyan-950 underline underline-offset-2">
                normanpendzich@gmail.com
              </a>
            </p>
            <p>
              <span className="font-medium text-gray-600">Kontaktformular:</span>{" "}
              <Link href="/kontakt" className="text-cyan-800 hover:text-cyan-950 underline underline-offset-2">
                politiklar.de/kontakt
              </Link>
            </p>
          </div>
        </section>

        {/* Redaktionell Verantwortlicher */}
        <section className="bg-white border border-gray-200 rounded-2xl p-6 sm:p-8 shadow-sm">
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            Verantwortlich für den Inhalt nach § 18 Abs. 2 MStV
          </h2>
          <div className="text-sm sm:text-base space-y-1 text-gray-800">
            <p className="font-semibold text-gray-900">Norman Pendzich</p>
            <p>Maybachstraße 1</p>
            <p>40470 Düsseldorf</p>
            <p>Deutschland</p>
          </div>
        </section>

        {/* Gemeinwohl & Neutralität */}
        <section className="bg-slate-50 border border-slate-200 rounded-2xl p-6 sm:p-8">
          <h2 className="text-lg font-bold text-gray-900 mb-2">
            Hinweis zur Plattform und Primärquellen
          </h2>
          <p className="text-sm text-gray-600 leading-relaxed mb-3">
            Politiklar ist ein unabhängiges, nicht-kommerzielles Civic-Tech-Projekt zur Förderung demokratischer Transparenz. Alle parlamentarischen Daten (Plenarprotokolle, namentliche Abstimmungen, Drucksachen und Abgeordnetenprofile) stammen aus offiziellen Primärquellen (unter anderem Deutscher Bundestag und DIP-Schnittstelle) und werden automatisiert aufbereitet.
          </p>
          <p className="text-sm text-gray-600 leading-relaxed">
            Trotz größter Sorgfalt bei der Datenverarbeitung und lückenlosen kryptografischen Hash-Prüfungen der Primärdokumente kann keine Gewähr für die absolute Vollständigkeit oder Aktualität der amtlichen Daten übernommen werden.
          </p>
        </section>

        {/* EU-Streitschlichtung */}
        <section className="bg-white border border-gray-200 rounded-2xl p-6 sm:p-8 shadow-sm">
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            Verbraucherstreitbeilegung / Universalschlichtungsstelle
          </h2>
          <p className="text-sm text-gray-600 leading-relaxed">
            Wir sind nicht bereit oder verpflichtet, an Streitbeilegungsverfahren vor einer Verbraucherschlichtungsstelle teilzunehmen.
          </p>
        </section>
      </div>

      {/* Footer Navigation */}
      <div className="mt-12 pt-8 border-t border-gray-200 flex flex-wrap items-center justify-between gap-4 text-sm text-gray-600">
        <Link href="/" className="font-semibold text-cyan-800 hover:text-cyan-950">
          ← Zurück zur Startseite
        </Link>
        <Link href="/datenschutz" className="font-semibold text-cyan-800 hover:text-cyan-950">
          Zur Datenschutzerklärung →
        </Link>
      </div>
    </div>
  );
}
