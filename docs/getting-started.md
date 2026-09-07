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

## Migrationen

```bash
make db-migrate
make db-migrate-down
make db-migrate
```

Migrationen laufen mit Alembic und werden niemals beim Containerstart automatisch angewendet. Vor Updates gehoeren Datenbank-Backups und ein pruefbarer Migrationslauf zum Betriebsablauf.

Zurueck zur [Dokumentationsuebersicht](README.md).