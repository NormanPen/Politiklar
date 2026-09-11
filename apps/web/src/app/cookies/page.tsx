import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Cookie-Richtlinie – Politiklar",
  description:
    "Erfahren Sie, warum Politiklar ohne lästige Cookie-Banner auskommt und welche technisch notwendigen Cookies wir einsetzen.",
};

export default function CookiesPage() {
  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12 sm:py-16">
      {/* Header */}
      <div className="text-center max-w-2xl mx-auto mb-12 sm:mb-16">
        <span className="inline-block px-3 py-1 rounded-full text-xs font-medium tracking-wide uppercase bg-emerald-50 text-emerald-800 border border-emerald-200 mb-3">
          Bannerfrei &amp; Trackingfrei
        </span>
        <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-gray-900">
          Cookie-Richtlinie
        </h1>
        <p className="mt-3 text-base sm:text-lg text-gray-600">
          Warum Sie auf Politiklar kein nerviges Cookie-Banner wegklicken müssen.
        </p>
      </div>

      {/* Main Feature Box */}
      <div className="bg-gradient-to-br from-emerald-50/60 to-cyan-50/40 border border-emerald-200 rounded-2xl p-6 sm:p-8 mb-10 shadow-sm">
        <div className="flex items-start gap-4">
          <span className="text-3xl sm:text-4xl">🍪</span>
          <div>
            <h2 className="text-xl font-bold text-gray-900 mb-2">
              Kein Tracking. Keine Werbung. Kein Banner.
            </h2>
            <p className="text-sm sm:text-base text-gray-700 leading-relaxed">
              Auf Politiklar verzichten wir bewusst auf Google Analytics, Werbe-Tracker, Social-Media-Pixel und Profiling. Deshalb sind wir rechtlich nicht verpflichtet (und halten es auch nutzerfreundlich für falsch), Sie mit einem Cookie-Zustimmungsbanner zu belästigen.
            </p>
          </div>
        </div>
      </div>

      <div className="space-y-8 text-gray-700 leading-relaxed text-base">
        <section className="bg-white border border-gray-200 rounded-2xl p-6 sm:p-8 shadow-sm">
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            Welche Cookies verwenden wir überhaupt?
          </h2>
          <p className="text-sm mb-4">
            Wir verwenden ausschließlich <strong>technisch zwingend erforderliche Cookies</strong> (§ 25 Abs. 2 Nr. 2 TDDDG). Diese werden nur dann aktiv, wenn Sie sich aktiv auf der Plattform anmelden oder Sicherheitsfunktionen nutzen:
          </p>

          <div className="overflow-x-auto">
            <table className="min-w-full text-left text-sm border-collapse">
              <thead>
                <tr className="border-b border-gray-200 bg-gray-50 text-gray-900 font-semibold">
                  <th className="py-3 px-4">Cookie-Name</th>
                  <th className="py-3 px-4">Zweck</th>
                  <th className="py-3 px-4">Gültigkeitsdauer</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 text-gray-600 text-xs sm:text-sm">
                <tr>
                  <td className="py-3 px-4 font-mono font-medium text-gray-900">authjs.session-token</td>
                  <td className="py-3 px-4">Speichert den sicheren Authentifizierungsstatus Ihrer aktiven Anmeldung.</td>
                  <td className="py-3 px-4">Sitzungsdauer / bis zum Logout</td>
                </tr>
                <tr>
                  <td className="py-3 px-4 font-mono font-medium text-gray-900">authjs.csrf-token</td>
                  <td className="py-3 px-4">Schützt vor Cross-Site-Request-Forgery (CSRF) bei Formularen und Login.</td>
                  <td className="py-3 px-4">Sitzungsdauer</td>
                </tr>
                <tr>
                  <td className="py-3 px-4 font-mono font-medium text-gray-900">authjs.callback-url</td>
                  <td className="py-3 px-4">Merkt sich die Zielseite nach erfolgreichem Login.</td>
                  <td className="py-3 px-4">Sitzungsdauer</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <section className="bg-white border border-gray-200 rounded-2xl p-6 sm:p-8 shadow-sm">
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            Wie können Sie Cookies steuern oder löschen?
          </h2>
          <p className="text-sm mb-3">
            Sie haben jederzeit über Ihren Webbrowser die volle Kontrolle über gespeicherte Cookies:
          </p>
          <ul className="list-disc pl-6 space-y-2 text-sm text-gray-600 mb-4">
            <li>Sie können alle Cookies in den Sicherheitseinstellungen Ihres Browsers löschen.</li>
            <li>Sie können einstellen, dass Ihr Browser Cookies beim Schließen des Fensters automatisch verwirft.</li>
            <li>Sie können Drittanbieter-Cookies oder alle Cookies blockieren (Hinweis: Ohne Session-Cookies ist ein Login nicht möglich).</li>
          </ul>
          <p className="text-sm text-gray-600">
            Detaillierte Informationen zum Schutz Ihrer Daten finden Sie in unserer vollständigen{" "}
            <Link href="/datenschutz" className="text-cyan-800 font-medium underline underline-offset-2">
              Datenschutzerklärung
            </Link>
            .
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
