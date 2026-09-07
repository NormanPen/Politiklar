# Projektstruktur

```text
Politiklar/
|- apps/
|  `- backend/
|     |- migrations/          Alembic-Migrationen
|     |- src/
|     |  |- core/             Settings
|     |  |- crawler/          Quellenabruf und Importer
|     |  `- db/relational/    SQLAlchemy-Modelle und Sessions
|     `- tests/               Parser- und Modelltests
|- docs/                      Projektdokumentation
|- .github/
|  |- skills/                 On-demand Review-Workflows
|  `- copilot-instructions.md Projektregeln
|- docker-compose.yml         Gemeinsamer PostgreSQL-Service
|- docker-compose.dev.yml     Lokales Port-Mapping
|- Makefile                   Entwicklungs- und Importbefehle
`- README.md                  Projekteinstieg
```

Die Verzeichnisse `apps/web`, `apps/backend/src/db/vector` und `.github/workflows` existieren bereits, enthalten aktuell aber keine produktive Implementierung.

Zurueck zur [Dokumentationsuebersicht](README.md).