---
name: bundestag-crawler
description: >-
  Anleitung und Betriebshandbuch für die Entwicklung, Ausführung, Fehlerbehebung und Erweiterung
  des Politiklar-Bundestag-Crawlers und Datenimporters. Nutze diesen Skill, wenn Crawler-Befehle
  ausgeführt werden sollen, neue Quellen importiert werden, Importer debuggt werden oder neue Parser
  (z. B. für Drucksachen oder Gremien) implementiert werden.
---

# Bundestag Crawler & Ingestion Runbook

Dieses Dokument beschreibt die Funktionsweise, Ausführung und Erweiterung des Crawlers und Datenimporters in `apps/backend/src/crawler/`.

## Architektur der Ingestion

```text
HTTP-Anfrage (httpx)
       │
       ▼
Fetcher (fetcher.py) ──► Speichert Raw-Response in var/source-archive/<prefix>/<sha256>
       │              ──► Erzeugt SourceDocumentSnapshot mit content_sha256 & resolved_url
       ▼
Parser (HTML/XML/XLSX)
  ├── bundestag_biography.py (Selectolax)  ──► MDB-Stammdaten, Mandate, Büros, Rollen
  ├── named_votes.py (openpyxl)            ──► Namentliche Abstimmungen (Zeilen ohne geratene MDB-ID)
  └── plenary_speeches.py (XML)            ──► Plenarreden (Sprecher-ID unbestätigt)
       │
       ▼
Persistenz (SQLAlchemy)
  ├── Speichert/aktualisiert source_documents
  └── Fügt Entitäten mit Fremdschlüssel auf source_documents ein (idempotent via Content-Hashes)
```

## Lokale Ausführung über Make

Vor der ersten Ausführung muss die PostgreSQL-Datenbank laufen und migriert sein:
```bash
make db
make db-migrate
```

### 1. Einzelne Quelle abrufen und archivieren
Ruft eine beliebige URL ab und legt sie content-addressiert im Archiv ab:
```bash
make crawler-fetch URL=https://www.bundestag.de/
```

### 2. Abgeordnetenbiografie importieren
Importiert Stammdaten, Büros, Mandate, Rollen und externe Profile:
```bash
make member-import URL=https://www.bundestag.de/abgeordnete/biografien/A/abdi_sanae-1043330
```

### 3. Namentliche Abstimmung importieren (Excel/XLSX)
Liest offizielle XLSX-Listen ein. Die MDB-ID bleibt dabei bewusst leer, bis eine verifizierte Identifikatorquelle existiert:
```bash
make vote-import URL=https://www.bundestag.de/resource/blob/1194616/20260710_8-xls.xlsx
```

### 4. Plenarprotokoll importieren (XML)
Importiert Reden mit amtlicher Rede-ID, Sprecher-ID und Volltext:
```bash
make speeches-import URL=https://www.bundestag.de/resource/blob/1194732/21090.xml
```

### 5. Plenarsprecher manuell mit MDB-ID verifizieren
Verknüpft eine Protokoll-Sprecher-ID verbindlich mit einer MDB-ID anhand zweier überprüfter Beleg-URLs:
```bash
make speaker-verify \
  MDB_ID=1043330 \
  SPEAKER_ID=11004011 \
  BIOGRAPHY_URL=https://www.bundestag.de/abgeordnete/biografien/... \
  PROTOCOL_URL=https://www.bundestag.de/resource/blob/...xml \
  VERIFIED_BY=name
```

### 6. Vollimport und Refresh aller Quellen der 21. Wahlperiode
Vor einem vollständigen Durchlauf empfiehlt sich ein begrenzter Trockenlauf (ohne DB-Schreibzugriffe):
```bash
# Trockenlauf mit Limit:
make bundestag-import DRY_RUN=1 LIMIT=5

# Echter Vollimport:
make bundestag-import

# Inkrementeller Refresh (nur neue oder geänderte Quellen):
make bundestag-refresh
```

---

## Entwicklung und Erweiterung von Parsern

### Neue Parser implementieren
1. **Bibliotheken**:
   - HTML: `selectolax` (schnell, speichereffizient).
   - Excel: `openpyxl`.
   - XML: `xml.etree.ElementTree` bzw. `defusedxml`.
   - HTTP: `httpx` via `SourceFetcher`.
2. **Quellenbeleg**:
   - Immer den `SourceDocumentSnapshot` an die Importfunktion übergeben.
   - Fremdschlüssel auf `source_documents.id` in allen erzeugten Entitäten setzen.
3. **Idempotenz**:
   - Erzeuge fachliche Prüfsummen oder nutze eindeutige Constraints (z. B. `(named_vote_id, row_index)` oder `(member_id, office_type, content_hash)`).
4. **Fehlerbehandlung**:
   - Unbekannte Felder oder Strukturbrüche niemals verschweigen. Entweder als unvollständig protokollieren oder gezielt eine Exception werfen.

### Tests schreiben und ausführen
Jeder Parser muss durch Pytest mit statischen Fixtures abgesichert sein. Keine Live-Netzwerkaufrufe in Tests!
```bash
apps/backend/.venv/bin/pytest apps/backend/tests
```

