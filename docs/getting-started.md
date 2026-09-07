# Lokale Entwicklung und Betrieb

## Voraussetzungen

- Docker mit Docker Compose
- Python 3.11 oder neuer
- GNU Make

## Entwicklungsumgebung

```bash
cp .env.development.example .env.development
make db
make crawler-install
make db-migrate
```

Die lokale PostgreSQL-Datenbank ist unter `127.0.0.1:5432` erreichbar. `make db-shell` startet `psql`; `make db-ps` zeigt den Dienststatus.

`postgres_data` ist ein benanntes Docker-Volume. Daten bleiben bei `docker compose stop`, `docker compose down` und Container-Neuerstellung erhalten. `docker compose down -v` entfernt das Volume und damit die Daten.

## Umgebungen

`.env.development` enthaelt lokale Werte und wird nicht versioniert. `.env.production` enthaelt ausschliesslich die Werte des Zielservers und wird ebenfalls nicht versioniert. Die zugehoerigen `.example`-Dateien sind commitbare Vorlagen ohne echte Geheimnisse.

In Produktion bleibt PostgreSQL im Compose-Netzwerk: Der Produktionsaufruf verwendet kein Port-Mapping fuer die Datenbank. Erst spaetere App-Container verbinden sich mit `postgres:5432`.

## Backend-API

### Lokal auf dem Host (Entwicklungsmodus mit Hot-Reload)
```bash
make api-dev
# oder
apps/backend/.venv/bin/politiklar-api --reload --port 8000
```

### Als Docker-Container (Docker Compose)
```bash
make docker-build       # Baut das einheitliche politiklar-backend Image
make api-docker         # Startet den API-Container im Hintergrund
make api-docker-logs    # Zeigt Container-Logs an
make api-docker-down    # Stoppt den API-Container
```

Crawler-Kommandos im Container ausführen:
```bash
make crawler-docker CMD="import-biography https://www.bundestag.de/..."
```

- Interaktive OpenAPI-Dokumentation (Swagger UI): `http://localhost:8000/docs`
- ReDoc-Dokumentation: `http://localhost:8000/redoc`
- Liveness- & Readiness-Probes: `http://localhost:8000/healthz` und `http://localhost:8000/api/v1/health`

## Web-Frontend (Next.js)

### Als Docker-Container (Entwicklung mit Hot-Reload)
```bash
make web-build          # Baut das Web-Docker-Image
make web-docker         # Startet den Web-Container (Port 3000)
make web-docker-logs    # Zeigt Web-Logs im Livestream
make web-docker-down    # Stoppt den Web-Container
make web-docker-shell   # Öffnet Shell im Web-Container
```
Der lokale Quellcode in `apps/web` ist direkt per Volume im Entwicklungs-Container eingebunden. Änderungen an Seiten und Komponenten werden sofort via Hot-Reloading/Fast Refresh im Browser aktualisiert (`http://localhost:3000`).

## Alle Dienste gemeinsam starten

```bash
make up    # Startet PostgreSQL, Backend-API und Web-Frontend im Hintergrund
make ps    # Zeigt Status aller Container
make logs  # Zeigt kombinierte Logs aller Container
make down  # Stoppt alle Container
```



## Migrationen

```bash
make db-migrate
make db-migrate-down
make db-migrate
```

Migrationen laufen mit Alembic und werden niemals beim Containerstart automatisch angewendet. Vor Updates gehoeren Datenbank-Backups und ein pruefbarer Migrationslauf zum Betriebsablauf.

Zurueck zur [Dokumentationsuebersicht](README.md).