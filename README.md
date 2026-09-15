# Politiklar

Politiklar ist eine Civic-Tech-Plattform fuer nachvollziehbare Informationen aus offiziellen deutschen politischen Quellen. Der aktuelle Entwicklungsstand konzentriert sich auf den Deutschen Bundestag, nachvollziehbare Quellenprovenienz und eine relationale PostgreSQL-Datenbasis.

## Schnellstart (Zero-Host-Dependencies)

Voraussetzung: Nur **Docker** (und optional `make`). Keine Installation von Python, Node oder PostgreSQL auf dem Host nötig!

```bash
# 1. Konfiguration anlegen (oder vorhandene .env einfügen)
cp .env.development.example .env.development

# 2. Optional: Datenbank-Backup einfügen unter
# var/dumps/politiklar_backup.dump

# 3. Setup starten (startet DB, stellt Backup wieder her oder migriert, baut & startet API + Web)
make setup-dev
# oder falls make noch nicht installiert ist:
./setup.sh dev
```

## Dokumentation

- [Dokumentationsuebersicht](docs/README.md)
- [Lokale Entwicklung und Betrieb](docs/getting-started.md)
- [Crawler und Datenimporte](docs/crawler-and-import.md)
- [Datenbankschema und Mermaid-Diagramme](docs/database-schema.md)
- [Aktuelle Architektur](docs/architecture.md)
- [Projektstruktur](docs/project-structure.md)
- [Technologie-Stack](docs/technology-stack.md)
- [Mitwirken](docs/contributing.md)
- [Roadmap](docs/roadmap.md)

## Aktueller Stand

Der Python-Crawler kann einzelne Bundestag-Biografien, namentliche Abstimmungslisten und Plenarprotokolle mit Quellen-URL, Abrufzeit, Inhalts-Hash und lokalem Quellenarchiv importieren. Individuelle Zuordnungen bei Abstimmungs- und Rededaten werden nicht aus Namen geraten, solange keine verifizierte amtliche ID-Verknuepfung vorliegt.

## Projektregeln

Die verbindlichen Projektregeln für KI-Agenten und Entwicklung stehen in [AGENTS.md](AGENTS.md) (sowie [copilot-instructions.md](.github/copilot-instructions.md)). Für fachliche Workflows und Reviews stehen Workspace-Skills unter [.agents/skills](.agents/skills/) zur Verfügung (u. a. `source-provenance-review`, `bundestag-crawler`, `db-migrations` und `rag-evidence-review`).

## Lizenz

Die Lizenz wird vor der ersten Veroeffentlichung als eigene `LICENSE`-Datei im Repository hinterlegt. Copyright 2026 Norman Pendzich.