.PHONY: help crawler-install crawler-fetch member-import vote-import speeches-import speaker-verify bundestag-import bundestag-refresh db db-down db-logs db-ps db-shell db-migrate db-migrate-down db-prod db-prod-down api-dev api-serve

COMPOSE_DEV = docker compose --env-file .env.development -f docker-compose.yml -f docker-compose.dev.yml
COMPOSE_PROD = docker compose --env-file .env.production -f docker-compose.yml

help:
	@printf '%s\n' \
		'Environment:' \
		'  db                 Start local PostgreSQL' \
		'  db-down            Stop local PostgreSQL' \
		'  db-ps              Show local PostgreSQL status' \
		'  db-shell           Open a local PostgreSQL shell' \
		'  db-migrate         Apply database migrations' \
		'  db-migrate-down    Roll back the latest migration' \
		'  db-prod            Start PostgreSQL with production settings' \
		'' \
		'API:' \
		'  api-dev            Start local development API server with auto-reload' \
		'  api-serve          Start production API server' \
		'' \
		'Crawler:' \
		'  crawler-install    Create the virtual environment and install dependencies' \
		'  crawler-fetch URL= Retrieve source metadata and archive the response' \
		'  member-import URL= Import one official Bundestag biography' \
		'  vote-import URL=   Import one official named-vote XLSX list' \
		'  speeches-import URL= Import one official plenary-protocol XML file' \
		'  speaker-verify MDB_ID= SPEAKER_ID= BIOGRAPHY_URL= PROTOCOL_URL= VERIFIED_BY= Verify and link a protocol speaker ID' \
		'  bundestag-import [LIMIT=] [DRY_RUN=1] Import all current official Bundestag source families' \
		'  bundestag-refresh [LIMIT=] [DRY_RUN=1] Refresh all current official Bundestag source families'

crawler-install:
	python3 -m venv apps/backend/.venv
	apps/backend/.venv/bin/python -m pip install --upgrade pip
	apps/backend/.venv/bin/python -m pip install -e 'apps/backend[dev]'

crawler-fetch:
	@test -n "$(URL)" || (echo "Usage: make crawler-fetch URL=https://example.org" && exit 1)
	apps/backend/.venv/bin/politiklar-crawl fetch "$(URL)"

member-import:
	@test -n "$(URL)" || (echo "Usage: make member-import URL=https://www.bundestag.de/abgeordnete/biografien/..." && exit 1)
	set -a && . ./.env.development && set +a && apps/backend/.venv/bin/politiklar-crawl import-biography "$(URL)"

vote-import:
	@test -n "$(URL)" || (echo "Usage: make vote-import URL=https://www.bundestag.de/resource/blob/...xlsx" && exit 1)
	set -a && . ./.env.development && set +a && apps/backend/.venv/bin/politiklar-crawl import-named-vote "$(URL)"

speeches-import:
	@test -n "$(URL)" || (echo "Usage: make speeches-import URL=https://www.bundestag.de/resource/blob/...xml" && exit 1)
	set -a && . ./.env.development && set +a && apps/backend/.venv/bin/politiklar-crawl import-protocol "$(URL)"

speaker-verify:
	@test -n "$(MDB_ID)" -a -n "$(SPEAKER_ID)" -a -n "$(BIOGRAPHY_URL)" -a -n "$(PROTOCOL_URL)" -a -n "$(VERIFIED_BY)" || (echo "Usage: make speaker-verify MDB_ID=... SPEAKER_ID=... BIOGRAPHY_URL=https://www.bundestag.de/... PROTOCOL_URL=https://www.bundestag.de/... VERIFIED_BY=name" && exit 1)
	set -a && . ./.env.development && set +a && apps/backend/.venv/bin/politiklar-crawl verify-plenary-speaker --mdb-id "$(MDB_ID)" --speaker-id "$(SPEAKER_ID)" --biography-evidence-url "$(BIOGRAPHY_URL)" --protocol-evidence-url "$(PROTOCOL_URL)" --verified-by "$(VERIFIED_BY)"

bundestag-import:
	set -a && . ./.env.development && set +a && apps/backend/.venv/bin/politiklar-crawl import-all $(if $(LIMIT),--limit $(LIMIT)) $(if $(DRY_RUN),--dry-run)

bundestag-refresh:
	set -a && . ./.env.development && set +a && apps/backend/.venv/bin/politiklar-crawl import-all --refresh $(if $(LIMIT),--limit $(LIMIT)) $(if $(DRY_RUN),--dry-run)

db-migrate:
	cd apps/backend && set -a && . ../../.env.development && set +a && .venv/bin/alembic upgrade head

db-migrate-down:
	cd apps/backend && set -a && . ../../.env.development && set +a && .venv/bin/alembic downgrade -1

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

db-prod:
	$(COMPOSE_PROD) up -d postgres

db-prod-down:
	$(COMPOSE_PROD) stop postgres

api-dev:
	set -a && . ./.env.development && set +a && apps/backend/.venv/bin/uvicorn api.main:app --reload --host 0.0.0.0 --port $${PORT:-8000}

api-serve:
	set -a && . ./.env.development && set +a && apps/backend/.venv/bin/uvicorn api.main:app --host 0.0.0.0 --port $${PORT:-8000}