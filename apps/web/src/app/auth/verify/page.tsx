import Link from "next/link";
import { Metadata } from "next";
import { verifyToken, VerificationStatus } from "@/app/actions/verify";

export const metadata: Metadata = {
  title: "E-Mail-Bestätigung – Politiklar",
  description: "Bestätige deine E-Mail-Adresse für deinen Politiklar-Account.",
};

interface VerifyPageProps {
  searchParams: Promise<{ token?: string; status?: string }>;
}

export default async function VerifyPage({ searchParams }: VerifyPageProps) {
  const params = await searchParams;
  const token = params.token;

  let currentStatus: VerificationStatus = "missing_token";

  if (params.status) {
    currentStatus = params.status as VerificationStatus;
  } else if (token) {
    const result = await verifyToken(token);
    currentStatus = result.status;
  }

  const statusConfigs: Record<
    VerificationStatus,
    { title: string; desc: string; type: "success" | "error" }
  > = {
    success: {
      title: "E-Mail erfolgreich bestätigt!",
      desc: "Dein Politiklar-Konto ist jetzt aktiv. Du kannst dich ab sofort anmelden und alle Funktionen uneingeschränkt nutzen.",
      type: "success",
    },
    expired: {
      title: "Bestätigungslink abgelaufen",
      desc: "Dieser Bestätigungslink ist älter als 24 Stunden und nicht mehr gültig. Bitte registriere dich erneut, um einen neuen Link anzufordern.",
      type: "error",
    },
    invalid: {
      title: "Ungültiger Bestätigungslink",
      desc: "Dieser Link existiert nicht oder wurde bereits verwendet. Jeder Bestätigungslink kann aus Sicherheitsgründen nur einmal verwendet werden.",
      type: "error",
    },
    missing_token: {
      title: "Kein Bestätigungstoken gefunden",
      desc: "In der Aufruf-URL wurde kein Token übergeben. Bitte verwende den vollständigen Link aus deiner Bestätigungs-E-Mail.",
      type: "error",
    },
    server_error: {
      title: "Technischer Verifizierungsfehler",
      desc: "Beim Verarbeiten der Bestätigung ist ein technischer Fehler aufgetreten. Bitte versuche es in wenigen Minuten erneut.",
      type: "error",
    },
  };

  const config = statusConfigs[currentStatus] || statusConfigs.missing_token;

  return (
    <main className="min-h-screen flex items-center justify-center bg-slate-950 px-4 py-16 text-slate-100">
      <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-2xl p-8 shadow-2xl text-center">
        {/* Status Icon */}
        <div
          className={`mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-full text-2xl font-bold transition-transform ${
            config.type === "success"
              ? "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30"
              : "bg-rose-500/15 text-rose-400 border border-rose-500/30"
          }`}
        >
          {config.type === "success" ? "✓" : "!"}
        </div>

        {/* Brand & Heading */}
        <p className="text-xs font-bold uppercase tracking-widest text-sky-400 mb-2">
          Politiklar Authentifizierung
        </p>
        <h1 className="text-2xl font-bold text-white mb-3">
          {config.title}
        </h1>
        <p className="text-sm text-slate-400 leading-relaxed mb-8">
          {config.desc}
        </p>

        {/* Action Button */}
        {config.type === "success" ? (
          <Link
            href="/konto"
            className="inline-flex items-center justify-center w-full py-3 px-6 bg-sky-600 hover:bg-sky-500 text-white font-semibold rounded-xl shadow-lg shadow-sky-600/20 transition duration-150 text-sm"
          >
            Jetzt zum Konto / Login
          </Link>
        ) : (
          <Link
            href="/konto"
            className="inline-flex items-center justify-center w-full py-3 px-6 bg-slate-800 hover:bg-slate-700 text-slate-200 font-medium rounded-xl border border-slate-700 transition duration-150 text-sm"
          >
            Zurück zur Konto-Seite
          </Link>
        )}
      </div>
    </main>
  );
}
