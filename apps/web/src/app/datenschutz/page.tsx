import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Datenschutzerklärung – Politiklar",
  description:
    "Informationen zur transparenten und datensparsamen Verarbeitung personenbezogener Daten auf der Plattform Politiklar gemäß DSGVO.",
};

export default function DatenschutzPage() {
  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12 sm:py-16">
      {/* Header */}
      <div className="text-center max-w-2xl mx-auto mb-12 sm:mb-16">
        <span className="inline-block px-3 py-1 rounded-full text-xs font-medium tracking-wide uppercase bg-emerald-50 text-emerald-800 border border-emerald-200 mb-3">
          Transparenz & Datensparsamkeit
        </span>
        <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-gray-900">
          Datenschutzerklärung
        </h1>
        <p className="mt-3 text-base sm:text-lg text-gray-600">
          Informationen darüber, wie wir personenbezogene Daten auf Politiklar gemäß der Datenschutz-Grundverordnung (DSGVO) verarbeiten.
        </p>
      </div>

      {/* Key Principles Banner */}
      <div className="bg-gradient-to-br from-slate-50 to-emerald-50/40 border border-emerald-100 rounded-2xl p-6 sm:p-8 mb-12 shadow-sm">
        <h2 className="text-lg font-bold text-gray-900 mb-3 flex items-center gap-2">
          <span>🛡️</span> Unser Grundsatz: Civic Tech ohne Überwachung
        </h2>
        <p className="text-sm text-gray-700 leading-relaxed">
          Politiklar ist eine gemeinwohlorientierte Civic-Tech-Plattform. Alle parlamentarischen Daten (Bundestagsdebatten, Reden, namentliche Abstimmungen und Abgeordnetenprofile) sind <strong>ohne Registrierung frei zugänglich</strong>. Wir verzichten vollständig auf Werbetracking, Marketing-Cookies und Analyse-Spionage.
        </p>
      </div>

      {/* Inhaltsverzeichnis */}
      <div className="bg-white border border-gray-200 rounded-2xl p-6 mb-12 shadow-sm">
        <h2 className="text-sm font-bold uppercase tracking-wider text-gray-900 mb-4">
          Übersicht
        </h2>
        <ul className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-sm text-gray-600">
          <li><a href="#verantwortlicher" className="hover:text-cyan-800 underline-offset-2 hover:underline">§ 1 Verantwortliche Stelle</a></li>
          <li><a href="#server-logs" className="hover:text-cyan-800 underline-offset-2 hover:underline">§ 2 Server-Logfiles</a></li>
          <li><a href="#cookies" className="hover:text-cyan-800 underline-offset-2 hover:underline">§ 3 Cookies & Bannerfreiheit</a></li>
          <li><a href="#kontakt" className="hover:text-cyan-800 underline-offset-2 hover:underline">§ 4 Kontaktformular & Kommunikation</a></li>
          <li><a href="#nutzerkonto" className="hover:text-cyan-800 underline-offset-2 hover:underline">§ 5 Nutzerkonto & Google-Login (OAuth)</a></li>
          <li><a href="#api" className="hover:text-cyan-800 underline-offset-2 hover:underline">§ 6 API- & MCP-Schnittstellen</a></li>
          <li><a href="#weitergabe" className="hover:text-cyan-800 underline-offset-2 hover:underline">§ 7 Keine Weitergabe an Dritte</a></li>
          <li><a href="#sicherheit" className="hover:text-cyan-800 underline-offset-2 hover:underline">§ 8 Sicherheit & SSL/TLS-Verschlüsselung</a></li>
          <li><a href="#speicherdauer" className="hover:text-cyan-800 underline-offset-2 hover:underline">§ 9 Speicherdauer & Löschung</a></li>
          <li><a href="#rechte" className="hover:text-cyan-800 underline-offset-2 hover:underline">§ 10 Ihre Rechte nach der DSGVO</a></li>
          <li><a href="#aufsichtsbehoerde" className="hover:text-cyan-800 underline-offset-2 hover:underline">§ 11 Beschwerderecht (Aufsichtsbehörde)</a></li>
          <li><a href="#aenderungen" className="hover:text-cyan-800 underline-offset-2 hover:underline">§ 12 Aktualität und Änderungen</a></li>
        </ul>
      </div>

      <div className="space-y-12 text-gray-700 text-base leading-relaxed">
        {/* § 1 Verantwortlicher */}
        <section id="verantwortlicher" className="scroll-mt-24 border-b border-gray-200 pb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            § 1 Verantwortliche Stelle
          </h2>
          <p className="mb-4">
            Verantwortlicher im Sinne der Datenschutz-Grundverordnung (DSGVO) sowie sonstiger datenschutzrechtlicher Bestimmungen für diese Website ist:
          </p>
          <div className="bg-gray-50 border border-gray-200 rounded-xl p-5 text-sm space-y-1.5">
            <p className="font-semibold text-gray-900">Norman Pendzich</p>
            <p>Maybachstraße 1</p>
            <p>40470 Düsseldorf</p>
            <p>Nordrhein-Westfalen, Deutschland</p>
            <p className="pt-2">
              <span className="font-medium text-gray-800">E-Mail:</span>{" "}
              <a href="mailto:normanpendzich@gmail.com" className="text-cyan-800 underline">
                normanpendzich@gmail.com
              </a>
            </p>
            <p>
              <span className="font-medium text-gray-800">Telefon:</span> +49 (0) 151 61449132
            </p>
          </div>
          <p className="mt-4 text-sm text-gray-600">
            Da in unserem Projekt weniger als 20 Personen ständig mit der Datenverarbeitung beschäftigt sind und keine Verarbeitungstätigkeiten nach Art. 35 bzw. 37 DSGVO vorliegen, besteht keine gesetzliche Pflicht zur Benennung eines betrieblichen Datenschutzbeauftragten (§ 38 Abs. 1 BDSG).
          </p>
        </section>

        {/* § 2 Server-Logfiles */}
        <section id="server-logs" className="scroll-mt-24 border-b border-gray-200 pb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            § 2 Server-Logfiles (Zugriffsdaten)
          </h2>
          <p className="mb-4">
            Beim Aufrufen von Politiklar erhebt und speichert der Webserver automatisch Informationen, die Ihr Browser an uns übermittelt. Diese Daten werden in sogenannten Server-Logdateien protokolliert:
          </p>
          <ul className="list-disc pl-6 space-y-1.5 mb-4 text-sm">
            <li>Browsertyp und Version des zugreifenden Geräts</li>
            <li>Verwendetes Betriebssystem</li>
            <li>Referrer-URL (die zuvor besuchte Website, von der aus Sie zu uns gelangten)</li>
            <li>Hostname des zugreifenden Rechners / IP-Adresse</li>
            <li>Datum und Uhrzeit der Serveranfrage</li>
            <li>Übertragene Datenmenge und HTTP-Statuscode</li>
          </ul>
          <p className="text-sm">
            <strong>Rechtsgrundlage:</strong> Art. 6 Abs. 1 lit. f DSGVO. Unser berechtigtes Interesse liegt in der Gewährleistung eines störungsfreien Verbindungsaufbaus, der Systemsicherheit und der Erkennung sowie Abwehr von böswilligen Angriffen (z. B. DDoS-Attacken). Eine Zusammenführung dieser Daten mit anderen Datenquellen oder eine Zuordnung zu bestimmten Personen findet nicht statt.
          </p>
        </section>

        {/* § 3 Cookies */}
        <section id="cookies" className="scroll-mt-24 border-b border-gray-200 pb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            § 3 Cookies &amp; Warum wir kein Cookie-Banner benötigen
          </h2>
          <p className="mb-4">
            Cookies sind kleine Textdateien, die Ihr Webbrowser auf Ihrem Endgerät speichert. Sie richten keinen Schaden an und enthalten keine Viren.
          </p>
          <div className="bg-emerald-50/50 border border-emerald-200 rounded-xl p-5 mb-4 text-sm">
            <h3 className="font-bold text-emerald-900 mb-2">
              Kein Cookie-Consent-Banner erforderlich
            </h3>
            <p className="text-emerald-950">
              Wir verwenden <strong>ausschließlich technisch notwendige Cookies</strong>. Wir setzen keine Werbe-, Tracking-, Profiling- oder Analyse-Cookies ein. Gemäß § 25 Abs. 2 Nr. 2 TDDDG (vormals TTDSG) und Art. 6 Abs. 1 lit. f DSGVO bedarf es für technisch zwingend erforderliche Cookies keiner vorherigen Einwilligung.
            </p>
          </div>
          <p className="text-sm mb-3">
            Konkret kommen folgende essenzielle Cookies zum Einsatz, wenn Sie den Login nutzen:
          </p>
          <ul className="list-disc pl-6 space-y-1.5 text-sm mb-4">
            <li>
              <code className="bg-gray-100 px-1 py-0.5 rounded text-xs">authjs.session-token</code> (bzw. <code className="bg-gray-100 px-1 py-0.5 rounded text-xs">__Secure-authjs.session-token</code>): Hält Ihre sichere Anmeldung während der aktiven Sitzung aufrecht.
            </li>
            <li>
              <code className="bg-gray-100 px-1 py-0.5 rounded text-xs">authjs.csrf-token</code>: Schützt Ihr Benutzerkonto vor Angriffen durch gefälschte Anfragen Dritter (Cross-Site Request Forgery).
            </li>
          </ul>
          <p className="text-sm text-gray-600">
            Sie können Ihren Browser so einstellen, dass Sie über das Setzen von Cookies informiert werden oder Cookies generell blockieren. Bei Deaktivierung technisch notwendiger Cookies kann die Login-Funktion jedoch nicht mehr genutzt werden.
          </p>
        </section>

        {/* § 4 Kontaktformular */}
        <section id="kontakt" className="scroll-mt-24 border-b border-gray-200 pb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            § 4 Kontaktformular und Kontaktaufnahme
          </h2>
          <p className="mb-4">
            Wenn Sie uns über unser <Link href="/kontakt" className="text-cyan-800 underline">Kontaktformular</Link> oder per E-Mail kontaktieren, werden die von Ihnen eingegebenen Formulardaten (Name, E-Mail-Adresse und Inhalt der Nachricht) bei uns verarbeitet, um Ihre Anfrage zu beantworten und für eventuelle Anschlussfragen zur Verfügung zu stehen.
          </p>
          <p className="mb-4 text-sm">
            <strong>Rechtsgrundlage:</strong> Art. 6 Abs. 1 lit. b DSGVO (sofern Ihre Anfrage der Vorbereitung oder Durchführung eines Vertragsverhältnisses dient) bzw. Art. 6 Abs. 1 lit. f DSGVO (unser berechtigtes Interesse an einer effizienten und nutzerfreundlichen Bearbeitung an uns gerichteter Mitteilungen).
          </p>
          <div className="bg-gray-50 border border-gray-200 rounded-xl p-4 text-sm">
            <h3 className="font-semibold text-gray-900 mb-1">
              Datenschutzfreundlicher Spamschutz (Honeypot-Verfahren)
            </h3>
            <p className="text-gray-600">
              Zum Schutz vor Spam und Bots verwenden wir ein unsichtbares, rein technisch umgesetztes Honeypot-Feld. Wir binden <strong>keine</strong> externen Tracking-Dienste wie Google reCAPTCHA oder hCaptcha ein. Ihre Eingaben verbleiben direkt bei uns.
            </p>
          </div>
        </section>

        {/* § 5 Nutzerkonto & Google OAuth */}
        <section id="nutzerkonto" className="scroll-mt-24 border-b border-gray-200 pb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            § 5 Nutzerkonto und Anmeldung via Google (Single Sign-On / OAuth)
          </h2>
          <p className="mb-4">
            Für die allgemeine Recherche im Parlamentsarchiv und das Einsehen von Abstimmungen ist keine Anmeldung erforderlich. Wenn Sie jedoch persönliche Dossier-Favoriten speichern oder API-Schlüssel generieren möchten, können Sie sich auf Politiklar ein Benutzerkonto anlegen.
          </p>
          
          <h3 className="text-lg font-bold text-gray-900 mt-6 mb-3">
            Anmeldung mit Google Sign-In
          </h3>
          <p className="mb-3 text-sm">
            Wir bieten Ihnen die Möglichkeit, sich schnell und sicher über Ihr bestehendes Google-Konto anzumelden (OAuth 2.0 / OpenID Connect). Dienstanbieter ist die <strong>Google Ireland Limited</strong>, Gordon House, Barrow Street, Dublin 4, Irland (Muttergesellschaft: Google LLC, 1600 Amphitheatre Parkway, Mountain View, CA 94043, USA).
          </p>
          <p className="mb-3 text-sm">
            Beim Klick auf den Google-Login-Button werden Sie direkt zu Google weitergeleitet. Nach Ihrer dortigen Bestätigung übermittelt Google uns zur Einrichtung Ihres Kontos folgende Profildaten:
          </p>
          <ul className="list-disc pl-6 space-y-1 mb-4 text-sm">
            <li>Ihre E-Mail-Adresse</li>
            <li>Ihren Vor- und Nachnamen (Profilname)</li>
            <li>Ihre Google-Benutzerkennung (eindeutige ID zur Zuordnung)</li>
            <li>Ihr Profilbild (optional, zur Anzeige im Navigationsmenü)</li>
          </ul>
          <p className="mb-4 text-sm">
            Wir erhalten <strong>keinen Zugriff</strong> auf Ihr Google-Passwort, Ihre E-Mails, Google-Drive-Dateien oder sonstige private Google-Dienste.
          </p>
          <p className="text-sm">
            <strong>Rechtsgrundlage:</strong> Art. 6 Abs. 1 lit. b DSGVO (Durchführung des Nutzungsverhältnisses für registrierte Konten).<br />
            <strong>Datenübermittlung in Drittstaaten:</strong> Google LLC ist nach dem <em>EU-U.S. Data Privacy Framework (DPF)</em> zertifiziert. Für Datenübermittlungen an zertifizierte US-Unternehmen besteht ein Angemessenheitsbeschluss der Europäischen Kommission gemäß Art. 45 DSGVO.
          </p>
        </section>

        {/* § 6 API & MCP */}
        <section id="api" className="scroll-mt-24 border-b border-gray-200 pb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            § 6 API- und MCP-Schnittstellen
          </h2>
          <p className="mb-4 text-sm">
            Registrierte Nutzer können persönliche API-Tokens generieren, um Daten programmatisch abzurufen oder Politiklar mit KI-Assistenten über das Model Context Protocol (MCP) zu verbinden.
          </p>
          <p className="text-sm">
            API-Tokens werden in unserer Datenbank ausschließlich als kryptografischer Einweg-Hash (SHA-256) gespeichert; das Klartext-Token ist für niemanden (auch nicht für uns Administratoren) einsehbar. Bei Aufrufen der API werden Anfragemengen (Rate Limiting) protokolliert, um eine Überlastung der Serverinfrastruktur zu verhindern (Art. 6 Abs. 1 lit. f DSGVO).
          </p>
        </section>

        {/* § 7 Keine Weitergabe */}
        <section id="weitergabe" className="scroll-mt-24 border-b border-gray-200 pb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            § 7 Weitergabe von Daten an Dritte
          </h2>
          <p className="text-sm leading-relaxed">
            Ihre personenbezogenen Daten werden von uns <strong>niemals verkauft, vermietet oder zu kommerziellen Werbezwecken</strong> an Dritte weitergegeben. Eine Übermittlung an Dritte erfolgt ausschließlich dann, wenn:
          </p>
          <ul className="list-disc pl-6 space-y-1.5 my-3 text-sm">
            <li>Sie Ihre ausdrückliche Einwilligung dazu erteilt haben (Art. 6 Abs. 1 lit. a DSGVO),</li>
            <li>die Weitergabe zur Erfüllung unseres Dienstes erforderlich ist (Art. 6 Abs. 1 lit. b DSGVO), oder</li>
            <li>eine gesetzliche Verpflichtung zur Weitergabe besteht (Art. 6 Abs. 1 lit. c DSGVO).</li>
          </ul>
        </section>

        {/* § 8 Sicherheit */}
        <section id="sicherheit" className="scroll-mt-24 border-b border-gray-200 pb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            § 8 Datensicherheit und SSL/TLS-Verschlüsselung
          </h2>
          <p className="text-sm leading-relaxed">
            Diese Plattform nutzt aus Sicherheitsgründen und zum Schutz der Übertragung vertraulicher Inhalte eine lückenlose SSL- bzw. TLS-Verschlüsselung. Eine verschlüsselte Verbindung erkennen Sie daran, dass die Adresszeile des Browsers von <code className="bg-gray-100 px-1 py-0.5 rounded text-xs">http://</code> auf <code className="bg-gray-100 px-1 py-0.5 rounded text-xs">https://</code> wechselt und an dem Schloss-Symbol in Ihrer Browserzeile. Wenn die Verschlüsselung aktiviert ist, können übermittelte Daten nicht von Dritten mitgelesen werden.
          </p>
        </section>

        {/* § 9 Speicherdauer */}
        <section id="speicherdauer" className="scroll-mt-24 border-b border-gray-200 pb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            § 9 Speicherdauer und Kontolöschung
          </h2>
          <p className="text-sm leading-relaxed mb-3">
            Wir verarbeiten und speichern personenbezogene Daten nur so lange, wie es zur Erreichung des jeweiligen Verarbeitungszwecks erforderlich ist. 
          </p>
          <p className="text-sm leading-relaxed">
            Nutzerdaten eines angelegten Accounts bleiben gespeichert, solange das Konto besteht. Sie können Ihr Konto und die damit verknüpften Favoriten oder API-Schlüssel jederzeit löschen lassen. Gesetzliche Aufbewahrungsfristen (z. B. nach Handels- oder Steuerrecht bei geschäftlicher Korrespondenz) bleiben unberührt.
          </p>
        </section>

        {/* § 10 Ihre Rechte */}
        <section id="rechte" className="scroll-mt-24 border-b border-gray-200 pb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            § 10 Ihre Datenschutzrechte als betroffene Person
          </h2>
          <p className="mb-4 text-sm">
            Nach der Datenschutz-Grundverordnung stehen Ihnen als betroffener Person umfassende Rechte zu:
          </p>
          <div className="space-y-4 text-sm">
            <div className="bg-white border border-gray-200 rounded-xl p-4">
              <h3 className="font-bold text-gray-900 mb-1">Auskunftsrecht (Art. 15 DSGVO)</h3>
              <p className="text-gray-600">Sie haben das Recht, von uns unentgeltlich Bestätigung darüber zu verlangen, ob wir personenbezogene Daten von Ihnen verarbeiten, und Auskunft über diese Daten zu erhalten.</p>
            </div>
            <div className="bg-white border border-gray-200 rounded-xl p-4">
              <h3 className="font-bold text-gray-900 mb-1">Recht auf Berichtigung (Art. 16 DSGVO)</h3>
              <p className="text-gray-600">Sie können die unverzügliche Berichtigung unrichtiger oder die Vervollständigung Ihrer bei uns gespeicherten Daten verlangen.</p>
            </div>
            <div className="bg-white border border-gray-200 rounded-xl p-4">
              <h3 className="font-bold text-gray-900 mb-1">Recht auf Löschung (Art. 17 DSGVO)</h3>
              <p className="text-gray-600">Sie haben das Recht auf Löschung („Recht auf Vergessenwerden“), sofern der Zweck entfällt, Sie Ihre Einwilligung widerrufen oder keine vorrangigen gesetzlichen Gründe entgegenstehen.</p>
            </div>
            <div className="bg-white border border-gray-200 rounded-xl p-4">
              <h3 className="font-bold text-gray-900 mb-1">Recht auf Einschränkung der Verarbeitung (Art. 18 DSGVO)</h3>
              <p className="text-gray-600">Sie können unter bestimmten Voraussetzungen die Einschränkung der Datenverarbeitung verlangen (z. B. während der Prüfung bestrittener Richtigkeit).</p>
            </div>
            <div className="bg-white border border-gray-200 rounded-xl p-4">
              <h3 className="font-bold text-gray-900 mb-1">Recht auf Datenübertragbarkeit (Art. 20 DSGVO)</h3>
              <p className="text-gray-600">Sie haben das Recht, Daten, die Sie uns bereitgestellt haben, in einem gängigen und maschinenlesbaren Format zu erhalten oder an Dritte zu übertragen.</p>
            </div>
            <div className="bg-white border border-gray-200 rounded-xl p-4">
              <h3 className="font-bold text-gray-900 mb-1">Widerspruchsrecht (Art. 21 DSGVO)</h3>
              <p className="text-gray-600">Sie können aus Gründen, die sich aus Ihrer besonderen Situation ergeben, jederzeit gegen die Verarbeitung Widerspruch einlegen, die auf Art. 6 Abs. 1 lit. f DSGVO beruht.</p>
            </div>
            <div className="bg-white border border-gray-200 rounded-xl p-4">
              <h3 className="font-bold text-gray-900 mb-1">Widerrufsrecht bei Einwilligungen (Art. 7 Abs. 3 DSGVO)</h3>
              <p className="text-gray-600">Erteilte Einwilligungen können Sie jederzeit mit Wirkung für die Zukunft formlos per E-Mail an uns widerrufen.</p>
            </div>
          </div>
        </section>

        {/* § 11 Aufsichtsbehörde */}
        <section id="aufsichtsbehoerde" className="scroll-mt-24 border-b border-gray-200 pb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            § 11 Beschwerderecht bei der zuständigen Aufsichtsbehörde
          </h2>
          <p className="mb-4 text-sm">
            Im Falle von datenschutzrechtlichen Verstößen steht Ihnen gemäß Art. 77 DSGVO ein Beschwerderecht bei einer Datenschutz-Aufsichtsbehörde zu, insbesondere in dem Mitgliedstaat Ihres gewöhnlichen Aufenthaltsorts, Ihres Arbeitsplatzes oder des Orts des mutmaßlichen Verstoßes.
          </p>
          <div className="bg-gray-50 border border-gray-200 rounded-xl p-5 text-sm space-y-1">
            <p className="font-semibold text-gray-900">
              Landesbeauftragte für Datenschutz und Informationsfreiheit Nordrhein-Westfalen (LDI NRW)
            </p>
            <p>Kavalleriestraße 2–4, 40213 Düsseldorf</p>
            <p>Postfach 20 04 44, 40102 Düsseldorf</p>
            <p>Telefon: +49 (0) 211 / 384 24-0</p>
            <p>E-Mail: <a href="mailto:poststelle@ldi.nrw.de" className="text-cyan-800 underline">poststelle@ldi.nrw.de</a></p>
            <p>Website: <a href="https://www.ldi.nrw.de" target="_blank" rel="noopener noreferrer" className="text-cyan-800 underline">https://www.ldi.nrw.de</a></p>
          </div>
        </section>

        {/* § 12 Änderungen */}
        <section id="aenderungen" className="scroll-mt-24 pb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            § 12 Aktualität und Änderung dieser Datenschutzerklärung
          </h2>
          <p className="text-sm leading-relaxed mb-4">
            Diese Datenschutzerklärung ist aktuell gültig und hat den Stand <strong>September 2026</strong>.
          </p>
          <p className="text-sm text-gray-600">
            Durch die Weiterentwicklung unserer Plattform oder aufgrund geänderter gesetzlicher beziehungsweise behördlicher Vorgaben kann es notwendig werden, diese Datenschutzerklärung anzupassen. Die jeweils aktuelle Datenschutzerklärung kann jederzeit auf dieser Seite abgerufen werden.
          </p>
        </section>
      </div>

      {/* Back to top or Home */}
      <div className="mt-12 pt-8 border-t border-gray-200 flex flex-wrap items-center justify-between gap-4 text-sm text-gray-600">
        <Link href="/" className="font-semibold text-cyan-800 hover:text-cyan-950">
          ← Zurück zur Startseite
        </Link>
        <Link href="/impressum" className="font-semibold text-cyan-800 hover:text-cyan-950">
          Zum Impressum →
        </Link>
      </div>
    </div>
  );
}
