# Aktuelle Architektur

```mermaid
flowchart TB
    Bundestag[Bundestag.de und Open Data] --> Crawler[Python-Crawler]
    Crawler --> Archive[Lokales Quellenarchiv]
    Crawler --> Database[(PostgreSQL)]
    Database --> API[FastAPI Backend-API]
    API --> FutureWeb[Geplante Web-Anwendung]
    Docker[Docker Compose] --> Database
    Volume[(postgres_data Volume)] --> Database
```

## Implementiert

- PostgreSQL 17 in Docker Compose
- Persistentes `postgres_data`-Volume
- Python-Crawler mit HTTP-Provenienz und Quellenarchiv
- Alembic-Migrationen
- Importer fuer einzelne Bundestag-Biografien, namentliche Abstimmungen und Plenarprotokolle
- FastAPI Backend-API (`apps/backend/src/api/`) mit OpenAPI-Dokumentation (`/docs`), Healthchecks, Quellenprovenienz, Abgeordneten-, Abstimmungs- und Reden-Endpunkten

## Noch geplant

- Vollstaendige Mitgliederdiscovery
- Drucksachenimport mit konfiguriertem DIP-API-Key
- Verifizierte Zuordnung von Abstimmungs- und Redezeilen zur MDB-ID
- Web-Anwendung, RAG und MCP-Server

Zurueck zur [Dokumentationsuebersicht](README.md).