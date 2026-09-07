# Politiklar – Workspace-Regeln für KI-Agenten

Politiklar ist eine Civic-Tech-Plattform für transparente und lückenlos nachvollziehbare Informationen aus offiziellen deutschen politischen Quellen (insbesondere Deutscher Bundestag). Für dieses Repository gelten verbindliche Qualitäts-, Integritäts- und Entwicklungskriterien.

---

## 1. Projektstruktur und Grenzen

- `apps/backend`: Enthält Python-Dienste (Python 3.11+), Daten-Crawler, Importer, SQLAlchemy-2.0-Modelle, Alembic-Migrationen und geplante APIs.
- `apps/web`: Enthält die geplante Next.js/TypeScript-Webanwendung (aktuell vorbereitet, noch nicht aktiv implementiert).
- `docs/`: Autoritative Dokumentation zu Architektur, Datenbankschema, Crawlern und Workflows.
- **Keine Scheininnovationen**: Der tatsächliche Dateibaum ist maßgeblich. Verwende keine Bibliotheken, Module oder Befehle, die nicht im Repository definiert oder installiert sind.

---

## 2. Daten- und Faktenintegrität (Nicht verhandelbar)

1. **Lückenlose Quellenprovenienz**:
   - Jeder erfasste, transformierte oder dargestellte politische Fakt muss auf eine offizielle Primärquelle zurückgeführt werden.
   - Zu jedem Quellabruf werden `resolved_url`, `content_sha256`, `retrieved_at` und die unberührte Antwort in `var/source-archive/` erfasst und in `source_documents` referenziert.
2. **Keine Namensratereien / Strenge ID-Prüfung**:
   - Namen sind in der Politik nicht eindeutig und ändern sich.
   - Namentliche Abstimmungen (`named_vote_rows`) oder Reden (`parliamentary_speeches`) dürfen **niemals** allein anhand von Vor-/Nachnamen mit einer `member_id` verknüpft werden.
   - Verknüpfungen erfolgen ausschließlich über verifizierte amtliche Kennungen (`member_source_identifiers`) mit nachgewiesenen Belegen (`member_source_identifier_evidence`).
   - Ein Ergebnis wie `nichtabgegeben` bei Abstimmungen ist eine offizielle Protokollkategorie und keine Aussage über den Grund einer Abwesenheit.
3. **Politische Neutralität und Sachlichkeit**:
   - Verwende ausschließlich neutrale, sachliche und beschreibende Sprache.
   - Keine politischen Wertungen, Rankings, Unterstellungen zu Motivationen oder Partei-Präferenzen.
   - Trenne Quellenzitate strikt von abgeleiteten Auswertungen.
4. **Idempotenz und Reproduzierbarkeit**:
   - Alle Importer und Transformationen müssen idempotent sein (fachliche Content-Hashes, `ON CONFLICT` bzw. Merge-Logik).
   - Wiederholte Importläufe mit denselben Quelldaten dürfen keine Duplikate erzeugen.
5. **Umgang mit unvollständigen Daten / Insufficient Evidence**:
   - Wenn Quelldaten unvollständig, fehlerhaft oder widersprüchlich sind, muss der Prozess explizit fehlschlagen oder die Unvollständigkeit festhalten. Niemals Werte erfinden ("Halluzinieren").
   - Antworten generativer Modelle müssen sich auf belegte Zitate stützen und ablehnen, wenn keine ausreichende Evidenz vorliegt.

---

## 3. Entwicklungs- und Betriebsworkflow

### Python-Umgebung
- Verwende für Python-Aufrufe, Tests und Skripte **stets** die projektinterne virtuelle Umgebung:
  - Python-Interpreter: `apps/backend/.venv/bin/python`
  - Test-Runner: `apps/backend/.venv/bin/pytest apps/backend/tests`
  - Crawler-CLI: `apps/backend/.venv/bin/politiklar-crawl` oder über `make`
- Führe kein globales `pip install` aus. Abhängigkeiten werden in `apps/backend/pyproject.toml` gepflegt.

### Tests und Verifikation
- Vor und nach Änderungen an Crawlern, Parsern, Modellen oder Hilfsskripten muss die Testsuite ausgeführt werden:
  ```bash
  apps/backend/.venv/bin/pytest apps/backend/tests
  ```
- Ergänze für jede Verhaltensänderung oder jeden neuen Parser fokussierte Tests mit deterministischen Fixtures.

### Datenbank und Migrationen
- Lokale PostgreSQL-Datenbank läuft via Docker Compose (`make db`, `make db-down`, `make db-ps`).
- Migrationen laufen mit Alembic (`cd apps/backend && .venv/bin/alembic ...` bzw. `make db-migrate`).
- Migrationen werden **niemals** automatisch beim Containerstart ausgeführt.
- Jede Schema-Änderung erfordert:
  1. Eine neue Alembic-Revisionsdatei in `apps/backend/migrations/versions/`.
  2. Test des Migrationszyklus: `make db-migrate` -> `make db-migrate-down` -> `make db-migrate`.
  3. Synchrone Aktualisierung von [docs/database-schema.md](docs/database-schema.md) inklusive der Mermaid-ER-Diagramme.

### Konfiguration und Sicherheit
- Niemals echte Secrets, API-Keys oder lokale `.env`-Dateien (`.env.development`, `.env.production`) committen.
- Neue Konfigurationsoptionen müssen in `apps/backend/src/core/settings.py` und in den Beispieldateien (`.env.example`, `.env.development.example`) dokumentiert werden.

