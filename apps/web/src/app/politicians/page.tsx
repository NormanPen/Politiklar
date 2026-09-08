interface MemberImage {
  media_url: string;
  commons_file_page_url: string;
  author: string | null;
  attribution_text: string | null;
  license_name: string | null;
  license_url: string | null;
}

interface MemberDetail {
  id: string;
  mdb_id: number;
  first_name: string;
  last_name: string;
  name_prefix: string | null;
  occupation: string | null;
  parliamentary_group: string | null;
  image: MemberImage | null;
  terms: Array<{ electoral_term: number; active: boolean }>;
  offices: Array<{ office_type: string; label: string | null; raw_address: string }>;
  affiliations: Array<{ category: string; organization_name: string; role_name: string }>;
  external_profiles: Array<{ platform: string; raw_label: string; url: string }>;
}

async function getMember(mdbId: number): Promise<MemberDetail | null> {
  // INTERNAL_API_URL ist im Docker-Container http://api:8000
  const baseUrl = process.env.INTERNAL_API_URL || process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

  try {
    const res = await fetch(`${baseUrl}/api/v1/members/${mdbId}`, {
      cache: "no-store", // Immer frische Daten für Entwicklung
    });

    if (!res.ok) {
      console.error(`API Error: ${res.status} ${res.statusText}`);
      return null;
    }

    return await res.json();
  } catch (error) {
    console.error("Fehler beim Abrufen der Abgeordneten-Daten:", error);
    return null;
  }
}

export default async function PoliticiansPage() {
  // Jan van Aken hat die offizielle MdB-ID 1043380
  const member = await getMember(1043380);

  if (!member) {
    return (
      <div className="max-w-2xl mx-auto my-12 p-6 bg-red-50 border border-red-200 rounded-xl text-red-700">
        <h1 className="text-xl font-bold">Fehler beim Laden</h1>
        <p className="mt-2 text-sm">
          Der Abgeordnete konnte nicht aus dem FastAPI-Backend geladen werden. Läuft das Backend unter <code className="bg-red-100 px-1 py-0.5 rounded">api:8000</code>?
        </p>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto my-10 p-6 space-y-6">
      <div className="border-b border-gray-200 pb-4">
        <h1 className="text-3xl font-extrabold text-gray-900 tracking-tight">
          Politiker-Profil (Live aus FastAPI)
        </h1>
        <p className="text-sm text-gray-500 mt-1">
          Server-Side Rendering direkt über <code className="text-indigo-600 bg-indigo-50 px-1.5 py-0.5 rounded font-mono text-xs">GET /api/v1/members/1043380</code>
        </p>
      </div>

      {/* Profil-Karte */}
      <div className="bg-white border border-gray-200 rounded-2xl shadow-sm p-6 space-y-6">
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-center gap-4">
            {/* Foto oder Initialen-Fallback */}
            {member.image ? (
              <div className="relative">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={member.image.media_url}
                  alt={`${member.first_name} ${member.last_name}`}
                  className="w-20 h-20 rounded-full object-cover border-2 border-purple-200 shadow-inner"
                />
              </div>
            ) : (
              <div className="w-20 h-20 rounded-full bg-purple-100 border-2 border-purple-200 flex items-center justify-center text-purple-700 font-bold text-xl shadow-inner shrink-0">
                {member.first_name[0]}{member.last_name[0]}
              </div>
            )}

            <div>
              <span className="inline-block px-2.5 py-1 text-xs font-semibold rounded-full bg-purple-100 text-purple-800 mb-1">
                {member.parliamentary_group || "Fraktionslos"}
              </span>
              <h2 className="text-2xl font-bold text-gray-900">
                {member.first_name} {member.last_name}
              </h2>
              <p className="text-gray-600 text-sm mt-0.5">{member.occupation}</p>
            </div>
          </div>

          <div className="text-right shrink-0">
            <span className="text-xs text-gray-400 font-mono block">MdB-ID</span>
            <span className="text-sm font-semibold text-gray-700 font-mono">{member.mdb_id}</span>
          </div>
        </div>

        {/* Bildnachweis falls Bild vorhanden */}
        {member.image && (
          <div className="text-[11px] text-gray-400 bg-gray-50 px-3 py-1.5 rounded-md">
            Foto: {member.image.author || "Unbekannt"} | Lizenz:{" "}
            {member.image.license_url ? (
              <a href={member.image.license_url} target="_blank" rel="noopener noreferrer" className="underline">
                {member.image.license_name || "Lizenz"}
              </a>
            ) : (
              member.image.license_name || "Gemeinfrei"
            )}
          </div>
        )}

        {/* Wahlperioden */}
        <div>
          <h3 className="text-xs font-bold uppercase tracking-wider text-gray-400 mb-2">
            Wahlperiode(n)
          </h3>
          <div className="flex gap-2">
            {member.terms.map((t) => (
              <span
                key={t.electoral_term}
                className="px-2.5 py-1 bg-gray-100 text-gray-800 text-xs font-medium rounded-md"
              >
                {t.electoral_term}. Wahlperiode {t.active && "(aktiv)"}
              </span>
            ))}
          </div>
        </div>

        {/* Ämter & Ausschüsse */}
        {member.affiliations.length > 0 && (
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-gray-400 mb-2">
              Funktionen & Gremien
            </h3>
            <ul className="space-y-1 text-sm text-gray-700">
              {member.affiliations.map((aff, index) => (
                <li key={index} className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-indigo-500"></span>
                  <span>
                    <strong>{aff.role_name}</strong> – {aff.organization_name}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Externe Links */}
        {member.external_profiles.length > 0 && (
          <div className="pt-2 border-t border-gray-100">
            <h3 className="text-xs font-bold uppercase tracking-wider text-gray-400 mb-2">
              Web & Social Media
            </h3>
            <div className="flex flex-wrap gap-2">
              {member.external_profiles.map((prof) => (
                <a
                  key={prof.platform}
                  href={prof.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 bg-gray-50 hover:bg-gray-100 text-gray-700 border border-gray-200 rounded-lg transition"
                >
                  <span>↗</span> {prof.raw_label}
                </a>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

