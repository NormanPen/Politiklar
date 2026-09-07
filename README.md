# Politiklar

Politiklar ist eine Civic-Tech-Plattform fuer nachvollziehbare Informationen aus offiziellen deutschen politischen Quellen. Der aktuelle Entwicklungsstand konzentriert sich auf den Deutschen Bundestag, nachvollziehbare Quellenprovenienz und eine relationale PostgreSQL-Datenbasis.

## Einstieg

```bash
cp .env.development.example .env.development
make db
make crawler-install
make db-migrate
make help
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