# Projektstruktur

```text
Politiklar/
|- apps/
|  |- backend/                 Python-Backend (Crawler, DB & API)
|  |  |- migrations/           Alembic-Migrationen
|  |  |- src/
|  |  |  |- api/               FastAPI REST-API & OpenAPI-Docs (/docs)
|  |  |  |- core/              Settings & Basiskonfiguration
|  |  |  |- crawler/           Quellenabruf, Ingestion & Parser
|  |  |  `- db/                Persistenzschicht (PostgreSQL / pgvector)
|  |  |     |- relational/     SQLAlchemy 2.0 Modelle und Sessions
|  |  |     `- vector/         Vektor-Embeddings (vorbereitet)
|  |  |- tests/                Parser-, Modell- und API-Tests
|  |  `- README.md             Backend-Entwicklerdokumentation
|  `- web/                     Next.js / TypeScript Webanwendung
|     |- src/app/              App Router, Pages & UI-Komponenten
|     `- README.md             Frontend-Entwicklerdokumentation
|- docs/                       Projektweite Dokumentation (Architektur, DB, Crawler)
|- var/
|  |- dumps/                   Datenbank-Backups (.dump)
|  `- source-archive/          Unberührte Primärquell-Dateien (SHA-256)
|- .agents/skills/             Workspace-Skills für KI-Agenten & Reviews
|- docker-compose.yml          Gemeinsamer PostgreSQL-Service
|- docker-compose.dev.yml      Lokales Port-Mapping & Dev-Setup
|- Makefile                    Zentraler Einstiegspunkt für Entwicklung & Betrieb
`- README.md                   Projekteinstieg & Schnellstart
```

- Eine detaillierte Modulübersicht zum Backend findest du in [apps/backend/README.md](../apps/backend/README.md).
- Die interaktive API-Dokumentation erreichst du bei laufendem Server unter `http://localhost:8000/docs`.

Zurueck zur [Dokumentationsuebersicht](README.md).