#!/usr/bin/env bash
set -e

# ==============================================================================
# Politiklar - Zero-Host-Dependency Setup Script
#
# Usage:
#   ./setup.sh              # Standard: Development setup
#   ./setup.sh dev          # Development setup
#   ./setup.sh prod         # Production setup
#   ./setup.sh dev /path/to/backup.dump  # Mit benutzerdefinierter Dump-Datei
# ==============================================================================

MODE="${1:-dev}"
DUMP_FILE="${2:-var/dumps/politiklar_backup.dump}"

# Falls 'make' installiert ist, nutzen wir die standardisierten Makefile-Targets
if command -v make >/dev/null 2>&1; then
  echo "==> 'make' gefunden. Führe 'make setup-${MODE}' aus..."
  if [ "$MODE" = "prod" ]; then
    exec make setup-prod FILE="$DUMP_FILE"
  else
    exec make setup-dev FILE="$DUMP_FILE"
  fi
fi

# Fallback: Reine Docker Compose Ausführung (kein make, node oder python nötig)
echo "==> Kein 'make' installiert. Führe Setup direkt über Docker Compose aus..."

if [ "$MODE" = "prod" ]; then
  ENV_FILE=".env.production"
  COMPOSE="docker compose --env-file .env.production -f docker-compose.yml"
else
  ENV_FILE=".env.development"
  COMPOSE="docker compose --env-file .env.development -f docker-compose.yml -f docker-compose.dev.yml"
fi

if [ ! -f "$ENV_FILE" ]; then
  echo "Fehler: $ENV_FILE existiert nicht! Bitte anlegen (z. B. aus ${ENV_FILE}.example)."
  exit 1
fi

echo "==> Starte PostgreSQL..."
$COMPOSE up -d postgres

echo "==> Warte auf PostgreSQL (healthcheck)..."
until $COMPOSE exec -T postgres sh -c 'pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"' >/dev/null 2>&1; do
  sleep 1
done

if [ -f "$DUMP_FILE" ]; then
  echo "==> Backup-Datei '$DUMP_FILE' gefunden. Stelle Datenbank wieder her..."
  if head -c 5 "$DUMP_FILE" | grep -q 'PGDMP'; then
    $COMPOSE exec -T postgres sh -c 'pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" --clean --if-exists --no-owner --no-privileges || test $$? -le 1' < "$DUMP_FILE"
  else
    $COMPOSE exec -T postgres sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < "$DUMP_FILE"
  fi
  echo "==> Datenbank erfolgreich wiederhergestellt. Wende anschliessende Alembic-Migrationen an..."
  $COMPOSE run --rm api alembic upgrade head
else
  echo "==> Keine Backup-Datei unter '$DUMP_FILE' gefunden. Führe Alembic-Migrationen aus..."
  $COMPOSE run --rm api alembic upgrade head
fi

echo "==> Baue und starte alle Dienste (Postgres, API, Web, Proxy)..."
$COMPOSE up -d --build

if [ "$MODE" = "dev" ]; then
  echo "==> Synchronisiere node_modules für die IDE..."
  sleep 3
  mkdir -p apps/web/node_modules
  docker cp politiklar-web:/app/node_modules/. apps/web/node_modules/ 2>/dev/null || true
fi

echo ""
echo "=========================================================="
echo "  Politiklar ($MODE) ist einsatzbereit!"
if [ "$MODE" = "prod" ]; then
  echo "  Web Frontend:  http://194.59.206.22 (oder https://politiklar.de)"
  echo "  Backend API:   http://194.59.206.22/api/v1"
  echo "  API Docs:      http://194.59.206.22/docs"
else
  echo "  Web Frontend:  http://localhost:3000"
  echo "  Backend API:   http://localhost:8000"
  echo "  API Docs:      http://localhost:8000/docs"
fi
echo "=========================================================="
