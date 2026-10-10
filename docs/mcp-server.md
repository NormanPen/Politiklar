# Politiklar MCP-Server (Model Context Protocol)

Der Politiklar MCP-Server stellt offizielle Bundestagsdaten und die semantische RAG-Pipeline über den offenen Standard **Model Context Protocol (MCP)** für KI-Modelle und -Agenten bereit.

Damit können sowohl der **Web-Chatbot** auf Politiklar als auch **externe KI-Clients** (Claude Desktop, Cursor, Antigravity, Terminal-Agenten) zielgerichtet und autonom zwischen relationalen SQL-Daten und semantischer pgvector-Vektorsuche wählen.

---

## 1. Architektur & Komponenten

```text
                  ┌──────────────────────────────────────────────┐
                  │              Konsumenten / Clients           │
                  │  (Web-Chatbot, Claude Desktop, Cursor, etc.) │
                  └──────────────────────┬───────────────────────┘
                                         │
                                         ▼
                  ┌──────────────────────────────────────────────┐
                  │       Politiklar MCP-Server (FastMCP)        │
                  │           apps/backend/src/mcp_server        │
                  └──────────────┬────────────────┬──────────────┘
                                 │                │
            ┌────────────────────┘                └────────────────────┐
            ▼                                                          ▼
  [SQL-Tools: sql_tools.py]                                  [RAG-Tools: rag_tools.py]
  - get_member_profile                                       - ask_bundestag_rag
  - get_named_vote                                           - search_speeches
  - list_named_votes                                                   │
            │                                                          ▼
            ▼                                                 [RagService + AIProvider]
  [PostgreSQL Relational DB]                                  [PostgreSQL pgvector DB]
  (Abgeordnete, Mandate, Abstimmungen)                       (Protokoll- & Rede-Chunks)
```

---

## 2. Verfügbare MCP-Tools

| Tool-Name | Typ | Beschreibung | Parameter |
| :--- | :--- | :--- | :--- |
| **`get_member_profile`** | SQL | Liefert das offizielle Profil eines Abgeordneten: Name, Fraktion, Wahlkreis, Biografie und Nebentätigkeiten. | `name_or_mdb_id` (str, z. B. `"12345"` oder `"Scholz"`) |
| **`get_named_vote`** | SQL | Liefert das amtliche Gesamtergebnis einer namentlichen Abstimmung inkl. Stimmenverteilung nach Fraktionen. | `title_or_id` (str, z. B. `"Rentenpaket"` oder Vote-Nummer) |
| **`list_named_votes`** | SQL | Listet kürzlich durchgeführte namentliche Abstimmungen des Bundestages auf. | `limit` (int, Standard: 10), `electoral_term` (int, Standard: 21) |
| **`ask_bundestag_rag`** | Vektor / RAG | Beantwortet Bürger- und Sachfragen evidenzbasiert anhand von Plenarprotokollen mit konkreten Belegstellen. | `question` (str) |
| **`search_speeches`** | Vektor | Reine semantische Vektorsuche nach Reden im Bundestag (liefert Zitate mit Ähnlichkeitsscores). | `query` (str), `limit` (int, Standard: 5) |

---

## 3. Server starten & Transports

Das Backend stellt das CLI-Kommando `politiklar-mcp` bereit:

### A. Lokaler Modus (`stdio`)
Ideal für lokale Desktop-Apps (Claude Desktop, Cursor, Terminal-Agenten):
```bash
apps/backend/.venv/bin/politiklar-mcp stdio
```

### B. Netzwerk- & Web-Modus (`sse`)
Ideal für Web-Chatbots und Remote-Zugriffe über HTTP/Server-Sent Events:
```bash
apps/backend/.venv/bin/politiklar-mcp sse --host 127.0.0.1 --port 8001
```

---

## 4. Einbindung in Claude Desktop

Füge in deiner Konfigurationsdatei (`~/.config/Claude/claude_desktop_config.json` unter Linux bzw. `~/Library/Application Support/Claude/claude_desktop_config.json` unter macOS) folgenden Block hinzu:

```json
{
  "mcpServers": {
    "politiklar": {
      "command": "/ABSOLUTER/PFAD/ZU/Politiklar/apps/backend/.venv/bin/politiklar-mcp",
      "args": ["stdio"],
      "env": {
        "DATABASE_URL": "postgresql+psycopg://politiklar:change-me-for-local-development@127.0.0.1:5432/politiklar",
        "GEMINI_API_KEY": "DEIN_GEMINI_API_SCHLUESSEL",
        "AI_PROVIDER": "gemini"
      }
    }
  }
}
```

Nach einem Neustart von Claude Desktop stehen alle 5 Politiklar-Tools automatisch im Chat zur Verfügung.
