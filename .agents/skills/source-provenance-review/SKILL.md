---
name: source-provenance-review
description: >-
  Überprüft Crawler-, Ingestion-, Transformations-, Datenmodell- und Suchänderungen auf lückenlose
  Quellenprovenienz, Nachvollziehbarkeit, Reproduzierbarkeit, politische Neutralität und evidenzbasierte Ausgabe.
  Nutze diesen Skill beim Erstellen oder Modifizieren von Crawlern, Datenimporten, Parsern oder Schema-Referenzen.
---

# Source Provenance Review für Politiklar

Dieser Skill leitet die Überprüfung von Datenbeschaffungs- und Transformationsprozessen im Politiklar-Projekt an. Das oberste Gebot von Politiklar ist, dass jeder politische Fakt zweifelsfrei und automatisiert auf eine offizielle Primärquelle zurückgeführt werden kann.

## Wann zu verwenden

- Bei der Erstellung oder Änderung von Crawlern, Fetchern und Datenimportern.
- Beim Hinzufügen neuer parlamentarischer Datenquellen oder Parser.
- Bei Änderungen am Datenbankmodell, insbesondere bei Tabellen mit Fremdschlüsseln auf `source_documents`.
- Bei der Überprüfung von Zusammenfassungen, Suchergebnissen, Zitationslogiken oder RAG-Pipelines.
- Bei der Zuordnung von Personen- und Redner-IDs.

## Prüfverfahren

### 1. Nachvollziehbarkeit der Primärquelle
- **Quelle und Abruf**: Wurde für jeden externen Abruf ein Eintrag in `source_documents` angelegt bzw. referenziert?
  - `resolved_url`: Exakte finale URL nach Weiterleitungen.
  - `content_sha256`: Kryptografischer Hash der Rohantwort.
  - `retrieved_at`: Präziser Zeitstempel des Abrufs.
  - `snapshot_location`: Pfad im Rohdatenarchiv (`var/source-archive/<prefix>/<hash>`).
- **Keine sekundären Spekulationen**: Primärquellen (z. B. offizielle Bundestags-Webseiten, XML-Plenarprotokolle, offizielle Abstimmungs-XLSX) haben absoluten Vorrang.

### 2. Idempotenz und Duplikatvermeidung
- Führt ein erneuter Import desselben Dokuments oder derselben URL zu Duplikaten?
- Werden fachliche Content-Hashes für Merkmale (z. B. Biografie-Snapshots, Mandate, Büroadressen) verwendet, um Änderungen versioniert, aber unveränderte Daten idempotent zu erfassen?

### 3. Keine spekulative Identitätszuordnung
- **Namen reichen nicht aus**: Werden PersonenIDs (`member_id`) niemals allein auf Basis von Namensgleichheit oder Ähnlichkeitssuche verknüpft?
- **Verifizierungsstatus**: Erfolgt die Zuordnung von Sprecher-IDs aus Plenarprotokollen (`speaker_source_id`) zu Abgeordneten (`bundestag_members.mdb_id`) ausschließlich über `member_source_identifiers` mit Status `verified` und zwei Belegen (`member_source_identifier_evidence`: Biografie-URL + Protokoll-URL)?
- **Offizielle Kategorien respektieren**: Wurde z. B. `nichtabgegeben` bei namentlichen Abstimmungen als offizielles Votum erfasst, ohne den Grund dafür zu erraten?

### 4. Fehlerbehandlung und Malformed Content
- Schlägt der Parser bei fehlerhaften, geänderten oder widersprüchlichen Daten explizit fehl oder markiert er Unsicherheiten?
- Ein Parser darf fehlende Pflichtfelder **niemals** still durch Standardwerte oder Annahmen ersetzen.

### 5. Politische Neutralität und Faktenabgrenzung
- Sind generierte Zusammenfassungen frei von Wertungen, Partei-Präferenzen, Ironie oder Mutmaßungen über Motivationen?
- Werden Quellenzitate exakt von abgeleiteten Auswertungen getrennt?

### 6. Testabdeckung
- Gibt es für jeden Parser und Importer fokussierte Komponententests mit statischen Testfixtures (HTML/XML/XLSX-Dateien)?
- Tests ausführen mit:
  ```bash
  apps/backend/.venv/bin/pytest apps/backend/tests
  ```

## Checkliste vor Freigabe

- [ ] `source_documents`-Fremdschlüssel vorhanden und belegt.
- [ ] Archivierung der Rohdaten in `var/source-archive/` sichergestellt.
- [ ] Keine unbelegten MDB-ID-Verknüpfungen (nur über verifizierte Belege).
- [ ] Idempotenter Importlauf ohne Duplikate.
- [ ] Pytest-Suite läuft fehlerfrei durch.

