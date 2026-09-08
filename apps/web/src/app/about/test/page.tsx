export default async function TestPage({
  searchParams,
}: {
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
}) {
  const params = await searchParams;
  const name = params.name;
  const thema = params.thema;

  return (
    <div style={{ padding: "2rem" }}>
      <h1>Testseite mit URL-Parametern</h1>
      
      <div style={{ marginTop: "1rem", padding: "1rem", background: "#f4f4f4", borderRadius: "8px" }}>
        <p className="text-black"><strong>Name:</strong> {name ? String(name) : "(kein Name-Parameter übergeben)"}</p>
        <p><strong>Thema:</strong> {thema ? String(thema) : "(kein Thema-Parameter übergeben)"}</p>
      </div>

      <div style={{ marginTop: "1.5rem" }}>
        <p>Probier mal diese Links (auch mit Umlauten/UTF-8):</p>
        <ul>
          <li>
            <a href="/about/test?name=Müller&thema=Klimaschutz">
              /about/test?name=Müller&thema=Klimaschutz
            </a>
          </li>
          <li>
            <a href="/about/test?name=Bärbel Bas&thema=Bundestagspräsidentin">
              /about/test?name=Bärbel Bas&thema=Bundestagspräsidentin
            </a>
          </li>
        </ul>
      </div>
    </div>
  );
}

