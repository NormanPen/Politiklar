.PHONY: help setup-dev setup-prod up down ps logs test crawler-install crawler-fetch member-import member-image member-images vote-import speeches-import speaker-verify bundestag-import bundestag-refresh db db-down db-logs db-ps db-shell db-dump db-dump-prod db-restore db-restore-prod db-migrate db-migrate-down db-migrate-prod db-migrate-down-prod db-prod db-prod-down api-dev api-serve docker-build api-docker api-docker-down api-docker-logs crawler-docker web-build web-docker web-docker-down web-docker-logs web-docker-shell web-sync-deps
.PHONY: help setup-dev setup-prod deploy-prod up down ps logs test crawler-install crawler-fetch member-import member-image member-images vote-import speeches-import speaker-verify bundestag-import bundestag-refresh db db-down db-logs db-ps db-shell db-dump db-dump-prod db-restore db-restore-prod db-migrate db-migrate-down db-migrate-prod db-migrate-down-prod db-prod db-prod-down api-dev api-serve docker-build api-docker api-docker-down api-docker-logs crawler-docker web-build web-docker web-docker-down web-docker-logs web-docker-shell web-sync-deps

COMPOSE_DEV = docker compose --env-file .env.development -f docker-compose.yml -f docker-compose.dev.yml
COMPOSE_PROD = docker compose --env-file .env.production -f docker-compose.yml
COMPOSE ?= $(COMPOSE_DEV)
DUMP_FILE ?= var/dumps/politiklar_backup.dump
FILE ?= $(DUMP_FILE)

help:
	@printf '%s\n' \
		'Setup & Initialization (Zero-Host-Dependencies):' \
		'  setup-dev          Complete setup for local development (starts DB, restores dump/migrates, starts API & Web)' \
		'  setup-prod         Complete setup for production (starts prod DB, restores dump/migrates, starts API & Web)' \
		'  deploy-prod        Deploy/update production server (git pull, build, migrate, restart, cleanup)' \
		'' \
		'All Services (Docker):' \
		'  up                 Start all services in Docker (Postgres + API + Web)' \
		'  down               Stop all Docker services' \
		'  ps                 Show status of all Docker containers' \
		'  logs               Follow logs of all Docker containers' \
		'  test               Run backend testsuite (in Docker or local venv)' \
		'' \
		'Environment (Database):' \
		'  db                 Start local PostgreSQL only' \
		'  db-down            Stop local PostgreSQL' \
		'  db-ps              Show local PostgreSQL status' \
		'  db-shell           Open a local PostgreSQL shell' \
		'  db-dump [FILE=]    Export database dump (default: var/dumps/politiklar_backup.dump)' \
		'  db-dump-prod       Export production database dump' \
		'  db-restore [FILE=] Restore database dump (default: var/dumps/politiklar_backup.dump)' \
		'  db-restore-prod    Restore database dump into production PostgreSQL' \
		'  db-migrate         Apply database migrations (dev)' \
		'  db-migrate-down    Roll back the latest migration (dev)' \
		'  db-migrate-prod    Apply database migrations (prod)' \
		'  db-migrate-down-prod Roll back latest migration (prod)' \
		'  db-prod            Start PostgreSQL with production settings' \
		'  db-prod-down       Stop production PostgreSQL' \
		'' \
		'Docker Services:' \
		'  docker-build       Build all Docker images (API + Web)' \
		'  api-docker         Start API container with Docker Compose' \
		'  api-docker-down    Stop API container' \
		'  api-docker-logs    Show API container logs' \
		'  web-build          Build Web Docker image' \
		'  web-docker         Start Web container with Docker Compose' \
		'  web-docker-down    Stop Web container' \
		'  web-docker-logs    Show Web container logs' \
		'  web-docker-shell   Open a shell in Web container' \
		'  web-sync-deps      Sync node_modules from Web container to host (for IDE)' \
		'  crawler-docker CMD= Run crawler command in Docker container' \
		'' \
		'API:' \
		'  api-dev            Start local development API server with auto-reload (requires local venv)' \
		'  api-serve          Start production API server (requires local venv)' \
		'' \
		'Crawler & Importer:' \
		'  crawler-install    Create the virtual environment and install dependencies on host' \
		'  crawler-fetch URL= Retrieve source metadata and archive the response' \
		'  member-import URL= Import one official Bundestag biography' \
		'  member-image URL=  Import/update Wikimedia portrait for one Bundestag biography' \
		'  vote-import URL=   Import one official named-vote XLSX list' \
		'  speeches-import URL= Import one official plenary-protocol XML file' \
		'  speaker-verify MDB_ID= SPEAKER_ID= BIOGRAPHY_URL= PROTOCOL_URL= VERIFIED_BY= Verify and link a protocol speaker ID' \
		'  bundestag-import [LIMIT=] [FAMILY=members|votes|protocols] [DRY_RUN=1] Import official Bundestag source families' \
		'  bundestag-refresh [LIMIT=] [FAMILY=members|votes|protocols] [DRY_RUN=1] Efficient incremental update (skips already imported unchanged sources)'

setup-dev:
	@echo "==> [Politiklar Setup-Dev] Prüfe .env.development..."
	@test -f .env.development || { echo "Fehler: .env.development existiert nicht! Bitte anlegen (z. B. aus .env.development.example)."; exit 1; }
	@echo "==> [Politiklar Setup-Dev] Starte PostgreSQL..."
	@$(COMPOSE_DEV) up -d postgres
	@echo "==> [Politiklar Setup-Dev] Warte auf PostgreSQL..."
	@until $(COMPOSE_DEV) exec -T postgres sh -c 'pg_isready -U "$$POSTGRES_USER" -d "$$POSTGRES_DB"' >/dev/null 2>&1; do sleep 1; done
	@if [ -f "$(FILE)" ]; then \
		echo "==> [Politiklar Setup-Dev] Backup-Datei '$(FILE)' gefunden. Stelle Datenbank wieder her..."; \
		$(MAKE) db-restore FILE="$(FILE)"; \
	else \
		echo "==> [Politiklar Setup-Dev] Keine Backup-Datei unter '$(FILE)'. Wende Alembic-Migrationen an..."; \
		$(MAKE) db-migrate; \
	fi
	@echo "==> [Politiklar Setup-Dev] Baue und starte Container (API & Web)..."
	@$(COMPOSE_DEV) up -d --build
	@echo "==> [Politiklar Setup-Dev] Synchronisiere node_modules für IDE..."
	@sleep 3
	@$(MAKE) web-sync-deps 2>/dev/null || true
	@printf '\n%s\n%s\n%s\n%s\n%s\n' \
		'==========================================================' \
		'  Politiklar Entwicklungsumgebung ist einsatzbereit!' \
		'  Web Frontend:  http://localhost:3000' \
		'  Backend API:   http://localhost:8000' \
		'  API Docs:      http://localhost:8000/docs' \
		'=========================================================='

setup-prod:
	@echo "==> [Politiklar Setup-Prod] Prüfe .env.production..."
	@test -f .env.production || { echo "Fehler: .env.production existiert nicht! Bitte anlegen (z. B. aus .env.production.example)."; exit 1; }
	@echo "==> [Politiklar Setup-Prod] Starte PostgreSQL (Prod)..."
	@$(COMPOSE_PROD) up -d postgres
	@echo "==> [Politiklar Setup-Prod] Warte auf PostgreSQL..."
	@until $(COMPOSE_PROD) exec -T postgres sh -c 'pg_isready -U "$$POSTGRES_USER" -d "$$POSTGRES_DB"' >/dev/null 2>&1; do sleep 1; done
	@if [ -f "$(FILE)" ]; then \
		echo "==> [Politiklar Setup-Prod] Backup-Datei '$(FILE)' gefunden. Stelle Datenbank wieder her..."; \
		$(MAKE) db-restore-prod FILE="$(FILE)"; \
		echo "==> [Politiklar Setup-Prod] Wende anschliessende Alembic-Migrationen an..."; \
		$(MAKE) db-migrate-prod; \
	else \
		echo "==> [Politiklar Setup-Prod] Keine Backup-Datei unter '$(FILE)'. Wende Alembic-Migrationen an..."; \
		$(MAKE) db-migrate-prod; \
	fi
	@echo "==> [Politiklar Setup-Prod] Baue und starte Produktions-Container (Postgres, API, Web, Proxy)..."
	@$(COMPOSE_PROD) up -d --build
	@printf '\n%s\n%s\n%s\n%s\n%s\n%s\n' \
		'==========================================================' \
		'  Politiklar Produktionsumgebung ist einsatzbereit!' \
		'  Web Frontend:  http://194.59.206.22 (oder https://politiklar.de)' \
		'  Backend API:   http://194.59.206.22/api/v1' \
		'  API Docs:      http://194.59.206.22/docs' \
		'=========================================================='

deploy-prod:
	@echo "==> [Politiklar Deploy] Prüfe .env.production..."
	@test -f .env.production || { echo "Fehler: .env.production existiert nicht!"; exit 1; }
	@echo "==> [Politiklar Deploy] Hole neuesten Stand von origin/main..."
	git fetch origin main
	git reset --hard origin/main
	@echo "==> [Politiklar Deploy] Baue Produktions-Container (API & Web)..."
	$(COMPOSE_PROD) build
	@echo "==> [Politiklar Deploy] Wende Datenbank-Migrationen an..."
	$(COMPOSE_PROD) run --rm api alembic upgrade head
	@echo "==> [Politiklar Deploy] Starte Container neu (unterbrechungsarm)..."
	$(COMPOSE_PROD) up -d --remove-orphans
	@echo "==> [Politiklar Deploy] Bereinige ungenutzte Docker-Images..."
	docker image prune -f
	@echo "==> [Politiklar Deploy] Führe Healthcheck durch..."
	@sleep 5
	@curl -sf http://localhost/healthz >/dev/null || { echo "Fehler: Healthcheck fehlgeschlagen!"; exit 1; }
	@printf '\n%s\n%s\n%s\n' \
		'==========================================================' \
		'  Politiklar Deployment erfolgreich abgeschlossen!' \
		'=========================================================='

test:
	@if [ -x apps/backend/.venv/bin/pytest ]; then \
		apps/backend/.venv/bin/pytest apps/backend/tests; \
	else \
		$(COMPOSE_DEV) run --rm api pytest tests; \
	fi

crawler-install:
	python3 -m venv apps/backend/.venv
	apps/backend/.venv/bin/python -m pip install --upgrade pip
	apps/backend/.venv/bin/python -m pip install -e 'apps/backend[dev]'

crawler-fetch:
	@test -n "$(URL)" || (echo "Usage: make crawler-fetch URL=https://example.org" && exit 1)
	@if [ -x apps/backend/.venv/bin/politiklar-crawl ]; then \
		apps/backend/.venv/bin/politiklar-crawl fetch "$(URL)"; \
	else \
		$(COMPOSE_DEV) run --rm api politiklar-crawl fetch "$(URL)"; \
	fi

# Einzelnen Abgeordneten per Biografie-URL importieren (inkl. automatischem Wikimedia-Profilbildabruf)
member-import:
	@test -n "$(URL)" || (echo "Usage: make member-import URL=https://www.bundestag.de/abgeordnete/biografien/..." && exit 1)
	@if [ -x apps/backend/.venv/bin/politiklar-crawl ]; then \
		set -a && . ./.env.development && set +a && apps/backend/.venv/bin/politiklar-crawl import-biography "$(URL)"; \
	else \
		$(COMPOSE_DEV) run --rm api politiklar-crawl import-biography "$(URL)"; \
	fi

# Gezielt das Profilbild für einen Abgeordneten über Wikidata & Wikimedia Commons nachladen/aktualisieren
member-image:
	@test -n "$(URL)" || (echo "Usage: make member-image URL=https://www.bundestag.de/abgeordnete/biografien/..." && exit 1)
	@if [ -x apps/backend/.venv/bin/politiklar-crawl ]; then \
		set -a && . ./.env.development && set +a && apps/backend/.venv/bin/politiklar-crawl import-member-image "$(URL)"; \
	else \
		$(COMPOSE_DEV) run --rm api politiklar-crawl import-member-image "$(URL)"; \
	fi

# Fehlende Profilbilder für bereits in der Datenbank gespeicherte Abgeordnete nachziehen (z. B. LIMIT=20)
member-images:
	@if [ -x apps/backend/.venv/bin/politiklar-crawl ]; then \
		set -a && . ./.env.development && set +a && apps/backend/.venv/bin/politiklar-crawl sync-member-images $(if $(LIMIT),--limit $(LIMIT)); \
	else \
		$(COMPOSE_DEV) run --rm api politiklar-crawl sync-member-images $(if $(LIMIT),--limit $(LIMIT)); \
	fi

# Namentliche Abstimmung aus offizieller Excel-Tabelle (XLSX) importieren
vote-import:
	@test -n "$(URL)" || (echo "Usage: make vote-import URL=https://www.bundestag.de/resource/blob/...xlsx" && exit 1)
	@if [ -x apps/backend/.venv/bin/politiklar-crawl ]; then \
		set -a && . ./.env.development && set +a && apps/backend/.venv/bin/politiklar-crawl import-named-vote "$(URL)"; \
	else \
		$(COMPOSE_DEV) run --rm api politiklar-crawl import-named-vote "$(URL)"; \
	fi

# Plenarprotokoll (XML) mit allen Reden importieren
speeches-import:
	@test -n "$(URL)" || (echo "Usage: make speeches-import URL=https://www.bundestag.de/resource/blob/...xml" && exit 1)
	@if [ -x apps/backend/.venv/bin/politiklar-crawl ]; then \
		set -a && . ./.env.development && set +a && apps/backend/.venv/bin/politiklar-crawl import-protocol "$(URL)"; \
	else \
		$(COMPOSE_DEV) run --rm api politiklar-crawl import-protocol "$(URL)"; \
	fi

# Protokoll-Sprecher-ID anhand zweier Belege verbindlich mit einer MDB-ID verknüpfen
speaker-verify:
	@test -n "$(MDB_ID)" -a -n "$(SPEAKER_ID)" -a -n "$(BIOGRAPHY_URL)" -a -n "$(PROTOCOL_URL)" -a -n "$(VERIFIED_BY)" || (echo "Usage: make speaker-verify MDB_ID=... SPEAKER_ID=... BIOGRAPHY_URL=https://www.bundestag.de/... PROTOCOL_URL=https://www.bundestag.de/... VERIFIED_BY=name" && exit 1)
	@if [ -x apps/backend/.venv/bin/politiklar-crawl ]; then \
		set -a && . ./.env.development && set +a && apps/backend/.venv/bin/politiklar-crawl verify-plenary-speaker --mdb-id "$(MDB_ID)" --speaker-id "$(SPEAKER_ID)" --biography-evidence-url "$(BIOGRAPHY_URL)" --protocol-evidence-url "$(PROTOCOL_URL)" --verified-by "$(VERIFIED_BY)"; \
	else \
		$(COMPOSE_DEV) run --rm api politiklar-crawl verify-plenary-speaker --mdb-id "$(MDB_ID)" --speaker-id "$(SPEAKER_ID)" --biography-evidence-url "$(BIOGRAPHY_URL)" --protocol-evidence-url "$(PROTOCOL_URL)" --verified-by "$(VERIFIED_BY)"; \
	fi

# Vollständiger Import aller Quellen der aktuellen Wahlperiode
# Optionen:
#   LIMIT=10                      Maximale Anzahl Quellen pro Kategorie
#   FAMILY=members|votes|protocols Auf eine Quellfamilie beschränken
#   DRY_RUN=1                     Nur Quellen entdecken, ohne DB-Schreibzugriff
bundestag-import:
	@if [ -x apps/backend/.venv/bin/politiklar-crawl ]; then \
		set -a && . ./.env.development && set +a && apps/backend/.venv/bin/politiklar-crawl import-all $(if $(LIMIT),--limit $(LIMIT)) $(if $(FAMILY),--family $(FAMILY)) $(if $(DRY_RUN),--dry-run); \
	else \
		$(COMPOSE_DEV) run --rm api politiklar-crawl import-all $(if $(LIMIT),--limit $(LIMIT)) $(if $(FAMILY),--family $(FAMILY)) $(if $(DRY_RUN),--dry-run); \
	fi

# Inkrementelles Update: Überspringt bereits vorhandene Quellen sekundenschnell
# und zieht nur neue Dokumente sowie fehlende Abgeordneten-Profilbilder nach.
# Optionen:
#   LIMIT=10                      Maximale Anzahl Quellen pro Kategorie
#   FAMILY=members|votes|protocols Auf eine Quellfamilie beschränken
#   DRY_RUN=1                     Nur Quellen entdecken, ohne DB-Schreibzugriff
bundestag-refresh:
	@if [ -x apps/backend/.venv/bin/politiklar-crawl ]; then \
		set -a && . ./.env.development && set +a && apps/backend/.venv/bin/politiklar-crawl import-all --refresh $(if $(LIMIT),--limit $(LIMIT)) $(if $(FAMILY),--family $(FAMILY)) $(if $(DRY_RUN),--dry-run); \
	else \
		$(COMPOSE_DEV) run --rm api politiklar-crawl import-all --refresh $(if $(LIMIT),--limit $(LIMIT)) $(if $(FAMILY),--family $(FAMILY)) $(if $(DRY_RUN),--dry-run); \
	fi

db-migrate:
	@if [ -x apps/backend/.venv/bin/alembic ]; then \
		cd apps/backend && set -a && . ../../.env.development && set +a && .venv/bin/alembic upgrade head; \
	else \
		$(COMPOSE_DEV) run --rm api alembic upgrade head; \
	fi

db-migrate-down:
	@if [ -x apps/backend/.venv/bin/alembic ]; then \
		cd apps/backend && set -a && . ../../.env.development && set +a && .venv/bin/alembic downgrade -1; \
	else \
		$(COMPOSE_DEV) run --rm api alembic downgrade -1; \
	fi

db-migrate-prod:
	$(COMPOSE_PROD) run --rm api alembic upgrade head

db-migrate-down-prod:
	$(COMPOSE_PROD) run --rm api alembic downgrade -1

up:
	$(COMPOSE_DEV) up -d

down:
	$(COMPOSE_DEV) stop

ps:
	$(COMPOSE_DEV) ps

logs:
	$(COMPOSE_DEV) logs -f

db:
	$(COMPOSE_DEV) up -d postgres

db-down:
	$(COMPOSE_DEV) stop postgres

db-logs:
	$(COMPOSE_DEV) logs -f postgres

db-ps:
	$(COMPOSE_DEV) ps postgres

db-shell:
	$(COMPOSE_DEV) exec postgres sh -c 'psql -U "$$POSTGRES_USER" -d "$$POSTGRES_DB"'

db-dump:
	@$(COMPOSE) ps --status running -q postgres | grep -q . || { echo "Fehler: PostgreSQL läuft nicht. Bitte zuerst 'make db' oder 'make db-prod' ausführen."; exit 1; }
	@mkdir -p $$(dirname "$(FILE)")
	@echo "Erstelle Datenbank-Dump in $(FILE)..."
	@if echo "$(FILE)" | grep -q '\.sql$$'; then \
		$(COMPOSE) exec -T postgres sh -c 'pg_dump -U "$$POSTGRES_USER" -d "$$POSTGRES_DB" --clean --if-exists --no-owner --no-privileges' > "$(FILE)"; \
	else \
		$(COMPOSE) exec -T postgres sh -c 'pg_dump -U "$$POSTGRES_USER" -d "$$POSTGRES_DB" -Fc --no-owner --no-privileges' > "$(FILE)"; \
	fi
	@echo "Dump erfolgreich erstellt: $(FILE) ($$(du -h "$(FILE)" | cut -f1))"

db-dump-prod:
	@$(MAKE) db-dump COMPOSE="$(COMPOSE_PROD)" FILE="$(FILE)"

db-restore:
	@test -f "$(FILE)" || { echo "Fehler: Dump-Datei '$(FILE)' existiert nicht!"; exit 1; }
	@$(COMPOSE) ps --status running -q postgres | grep -q . || { echo "Fehler: PostgreSQL läuft nicht. Bitte zuerst 'make db' oder 'make db-prod' ausführen."; exit 1; }
	@echo "Stelle Datenbank aus $(FILE) wieder her..."
	@if head -c 5 "$(FILE)" | grep -q 'PGDMP'; then \
		$(COMPOSE) exec -T postgres sh -c 'pg_restore -U "$$POSTGRES_USER" -d "$$POSTGRES_DB" --clean --if-exists --no-owner --no-privileges || test $$? -le 1' < "$(FILE)"; \
	else \
		$(COMPOSE) exec -T postgres sh -c 'psql -v ON_ERROR_STOP=1 -U "$$POSTGRES_USER" -d "$$POSTGRES_DB"' < "$(FILE)"; \
	fi
	@echo "Datenbank erfolgreich wiederhergestellt aus $(FILE)."

db-restore-prod:
	@$(MAKE) db-restore COMPOSE="$(COMPOSE_PROD)" FILE="$(FILE)"

db-prod:
	$(COMPOSE_PROD) up -d postgres

db-prod-down:
	$(COMPOSE_PROD) stop postgres

api-dev:
	set -a && . ./.env.development && set +a && apps/backend/.venv/bin/uvicorn api.main:app --reload --host 0.0.0.0 --port $${PORT:-8000}

api-serve:
	set -a && . ./.env.development && set +a && apps/backend/.venv/bin/uvicorn api.main:app --host 0.0.0.0 --port $${PORT:-8000}

docker-build:
	$(COMPOSE_DEV) build api web

api-docker:
	$(COMPOSE_DEV) up -d api

api-docker-down:
	$(COMPOSE_DEV) stop api

api-docker-logs:
	$(COMPOSE_DEV) logs -f api

web-build:
	$(COMPOSE_DEV) build web

web-docker:
	$(COMPOSE_DEV) up -d web

web-docker-down:
	$(COMPOSE_DEV) stop web

web-docker-logs:
	$(COMPOSE_DEV) logs -f web

web-docker-shell:
	$(COMPOSE_DEV) exec web sh

web-sync-deps:
	@mkdir -p apps/web/node_modules
	docker cp politiklar-web:/app/node_modules/. apps/web/node_modules/

crawler-docker:
	@test -n "$(CMD)" || (echo "Usage: make crawler-docker CMD=\"import-all --help\"" && exit 1)
	$(COMPOSE_DEV) run --rm api politiklar-crawl $(CMD)