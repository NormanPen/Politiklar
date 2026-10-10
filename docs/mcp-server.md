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

## 4. Authentifizierung (API-Schlüssel)

Der Politiklar MCP-Server validiert Zugriffe über sichere SHA-256-gehashte Tokens (`pk_live_...`), die in der PostgreSQL-Tabelle `user_api_keys` hinterlegt sind:

1. **Schlüssel erzeugen**: Jeder registrierte Nutzer kann unter `http://localhost:3000/konto` im Bereich **API- & MCP-Server-Schlüssel** ein persönliches Zugriffstoken erzeugen.
2. **Umgebungsvariable**: Der Client übergibt das Token über die Umgebungsvariable `POLITIKLAR_API_KEY`.
3. **Audit & Expiration**: Bei jedem Tool-Aufruf wird die Gültigkeit geprüft und der Zeitstempel `last_used_at` aktualisiert.
4. **Lokale Entwicklung**: Für automatisierte Tests oder lokale Offline-Entwicklung kann die Authentifizierung optional via `POLITIKLAR_ALLOW_ANONYMOUS_MCP=true` deaktiviert werden.

---

## 5. Client-Einbindung

### A. Google Antigravity (AGY)
In `.agents/mcp_config.json` (im Projekt) oder `~/.gemini/antigravity-ide/mcp_config.json`:
```json
{
  "mcpServers": {
    "politiklar": {
      "command": "/ABSOLUTER/PFAD/apps/backend/.venv/bin/politiklar-mcp",
      "args": ["stdio"],
      "env": {
        "POLITIKLAR_API_KEY": "pk_live_dein_api_schluessel"
      }
    }
  }
}
```

### B. Claude Desktop (Anthropic)
In `claude_desktop_config.json` (macOS: `~/Library/Application Support/Claude/`, Linux: `~/.config/Claude/`, Windows: `%APPDATA%\Claude\`):
```json
{
  "mcpServers": {
    "politiklar": {
      "command": "/ABSOLUTER/PFAD/apps/backend/.venv/bin/politiklar-mcp",
      "args": ["stdio"],
      "env": {
        "POLITIKLAR_API_KEY": "pk_live_dein_api_schluessel"
      }
    }
  }
}
```

### C. Cursor & Windsurf IDE
In Cursor unter **Settings → Features → MCP Servers → Add new MCP server**:
- Name: `politiklar`
- Type: `command`
- Command: `/ABSOLUTER/PFAD/apps/backend/.venv/bin/politiklar-mcp stdio`
- Environment Variables: `POLITIKLAR_API_KEY=pk_live_dein_api_schluessel`

Alternativ als `.cursor/mcp.json` im Projekt-Root.

### D. Python & OpenAI SDK
```python
import os
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    server_params = StdioServerParameters(
        command="apps/backend/.venv/bin/politiklar-mcp",
        args=["stdio"],
        env={"POLITIKLAR_API_KEY": "pk_live_dein_api_schluessel", **os.environ}
    )
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            profile = await session.call_tool("get_member_profile", {"name_or_mdb_id": "Jan van Aken"})
            print(profile)

asyncio.run(main())
```

