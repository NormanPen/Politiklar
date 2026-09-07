# Aktuelle Architektur

```mermaid
flowchart TB
    Bundestag[Bundestag.de und Open Data] --> Crawler[Python-Crawler]
    Crawler --> Archive[Lokales Quellenarchiv]
    Crawler --> Database[(PostgreSQL)]
    Database --> FutureAPI[Geplante Backend-API]
    FutureAPI --> FutureWeb[Geplante Web-Anwendung]
    Docker[Docker Compose] --> Database
    Volume[(postgres_data Volume)] --> Database
```

## Implementiert

- PostgreSQL 17 in Docker Compose
- Persistentes `postgres_data`-Volume
- Python-Crawler mit HTTP-Provenienz und Quellenarchiv
- Alembic-Migrationen
- Importer fuer einzelne Bundestag-Biografien, namentliche Abstimmungen und Plenarprotokolle

## Noch geplant

- Vollstaendige Mitgliederdiscovery
- Drucksachenimport mit konfiguriertem DIP-API-Key
- Verifizierte Zuordnung von Abstimmungs- und Redezeilen zur MDB-ID
- Backend-API, Web-Anwendung, RAG und MCP-Server

Zurueck zur [Dokumentationsuebersicht](README.md).