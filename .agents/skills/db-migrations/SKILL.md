---
name: db-migrations
description: >-
  Leitfaden für Datenbank-Schemaänderungen, Alembic-Migrationen und SQLAlchemy-2.0-Modelle in Politiklar.
  Nutze diesen Skill, wenn neue Tabellen oder Spalten angelegt, Indizes hinzugefügt, Migrationen erstellt
  oder zurückgerollt oder das Datenbankschema und dessen Dokumentation gepflegt werden müssen.
---

# Datenbank-Schema & Migrations-Leitfaden

Politiklar verwendet PostgreSQL 17 mit SQLAlchemy 2.0 und Alembic zur Schemaverwaltung. Die relationale Datenbank trennt fachliche Fakten strikt von ihren Belegdokumenten (`source_documents`).

## Modellierungsprinzipien

1. **Primärschlüssel**:
   - Verwende `UUID` als Primärschlüssel (`uuid.uuid4()`) für alle Entitäten.
2. **Quellenfremdschlüssel**:
   - Jede Entität, die aus einer externen Quelle stammt, muss einen Fremdschlüssel auf `source_documents.id` (`ondelete="RESTRICT"`) besitzen.
3. **Idempotenz durch Content-Hashes**:
   - Für veränderliche Fakten (z. B. Büros, Profile, Mandate) wird ein SHA-256-Hash der fachlichen Attribute (`content_hash`) gespeichert und über `UniqueConstraint` abgesichert, um Duplikate bei wiederholten Importen zu verhindern.
4. **Verifizierte Identifikatoren**:
   - Externe Kennungen werden über `member_source_identifiers` und `member_source_identifier_evidence` erfasst. Keine losen Fremdschlüssel ohne Belegkette!

---

## Ablauf für Schema-Änderungen

### Schritt 1: SQLAlchemy-Modelle anpassen
Passe die Modelle in `apps/backend/src/db/relational/models.py` an.

### Schritt 2: Neue Alembic-Migration anlegen
Erstelle eine neue Revisionsdatei in `apps/backend/migrations/versions/`.
- Dateinamenskonvention: `YYYYMMDD_NN_kurzbeschreibung.py` (z. B. `20260907_08_add_parliamentary_committees.py`).
- Implementiere sowohl `upgrade()` als auch `downgrade()` vollständig und symmetrisch.

```python
"""Kurze Beschreibung der Änderung.

Revision ID: 20260907_08
Revises: 20260907_07
Create Date: 2026-09-07
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260907_08"
down_revision = "20260907_07"
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Schemaänderungen anwenden
    ...

def downgrade() -> None:
    # Schemaänderungen sauber rückgängig machen
    ...
```

### Schritt 3: Migrationszyklus testen
Vor dem Commit muss der Migrationszyklus zwingend lokal gegen die PostgreSQL-Datenbank getestet werden:

```bash
# 1. Datenbank starten (falls nicht aktiv)
make db

# 2. Migration anwenden
make db-migrate

# 3. Rollback testen
make db-migrate-down

# 4. Erneut anwenden
make db-migrate
```

### Schritt 4: Dokumentation und Mermaid-Diagramme aktualisieren
Jede Schemaänderung verpflichtet zur synchronen Aktualisierung von:
- [docs/database-schema.md](file:///home/nope/Github/Politiklar/docs/database-schema.md):
  - Mermaid-ER-Diagramme (`erDiagram`) aktualisieren.
  - Tabellenübersicht in der Markdown-Tabelle ergänzen.
  - Besondere Constraints und Semantiken dokumentieren.

### Schritt 5: Modell- und Migrationstests prüfen
```bash
apps/backend/.venv/bin/pytest apps/backend/tests/test_models.py
```

