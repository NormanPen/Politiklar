# 🏛️ Politiklar – Offene Transparenzplattform für Politik in Deutschland


> **Politiklar** ist ein digitales Civic-Tech-Projekt, das politische Informationen aus offiziellen deutschen Quellen automatisiert aggregiert, strukturiert und mithilfe moderner KI-Technologien (RAG & MCP) verständlich und nachvollziehbar aufbereitet. 

Das Projekt verfolgt das Ziel, politische Bildung und Informationsgerechtigkeit zu fördern, und wächst schrittweise in Richtung eines gemeinnützigen Trägers (*Politiklar e.V.*) in enger Kooperation mit Studierenden und Hochschulen.

---

## 🚀 Kernziele

* **Automatisierte Aggregation:** Strukturierte Sammlung von Protokollen, Abstimmungen, Gesetzestexten und Statements.
* **Semantische KI-Suche (RAG):** Vektorbasierte Kontextsuche über parlamentarische Inhalte und Dokumente ohne Black-Box-Halluzinationen.
* **Offener MCP-Server:** Bereitstellung von standardisierten Tools und Ressourcen via *Model Context Protocol* für externe KI-Agenten.
* **Interdisziplinäre Plattform:** Praxisnahe Zusammenarbeit für Studierende aus Informatik, Politik- und Medienwissenschaften.

---

## 🛠️ Technologie-Stack

* **Frontend:** Next.js (App Router), TypeScript, Tailwind CSS
* **Backend & API:** FastAPI (Python), uv / poetry, Pydantic
* **Pipelines & Agentik:** Scraper (httpx, selectolax), MCP-Server, LangChain / native RAG-Pipeline
* **Datenspeicherung:** PostgreSQL (Fakten & Relationen), Qdrant oder pgvector (Embeddings)
* **DevOps & Orchestrierung:** Docker Compose (lokale DX), GitHub Actions (CI/CD), vorbereitet für Kubernetes

---

## 📦 Projektstruktur

<details open>
<summary><b>Ordnerhierarchie anzeigen / ausblenden</b></summary>

```text
mein-projekt/
│
├── .github/
│   └── workflows/              # GitHub Actions (CI/CD Workflows)
│       ├── web-ci.yml          # Triggert nur bei Änderungen in apps/web/**
│       └── backend-ci.yml      # Triggert nur bei Änderungen in apps/backend/**
│
├── apps/
│   ├── web/                    # Next.js Frontend (App Router, Tailwind, TypeScript)
│   │   ├── src/
│   │   │   ├── app/            # Routen, Layouts & Server Components
│   │   │   ├── components/     # UI-Komponenten
│   │   │   └── lib/            # Utilities, API-Clients, Hooks
│   │   ├── Dockerfile          # Multi-stage Dockerfile für Next.js
│   │   ├── package.json
│   │   └── tsconfig.json
│   │
│   └── backend/                # Python Stack (FastAPI, Crawler, MCP Server)
│       ├── src/
│       │   ├── api/            # REST-Endpunkte & Router (FastAPI)
│       │   ├── crawler/        # Scraper-Logik & Worker
│       │   ├── mcp/            # MCP Server (Model Context Protocol Tools/Resources)
│       │   ├── core/           # Config, Logging, Settings (Pydantic)
│       │   └── db/             # Datenbankverbindungen & Repositories
│       │       ├── relational/ # SQL-Models (SQLAlchemy / SQLModel)
│       │       └── vector/     # Vektor-Datenbank-Client (z. B. pgvector / Qdrant)
│       ├── migrations/         # Alembic Migrations
│       ├── tests/              # Pytest Unit- & Integrationstests
│       ├── Dockerfile          # Python Container Build
│       └── pyproject.toml      # Dependency Management (uv / poetry)
│
├── deploy/                     # Infrastruktur- & Deployment-Konfigurationen
│   ├── docker/
│   │   └── init-scripts/       # DB-Init-Skripte (z. B. pgvector Extensions)
│   └── k8s/                    # Kubernetes Manifeste (Kustomize / Helm)
│       ├── base/               # Basis-Deployments, Services, ConfigMaps
│       └── overlays/
│           ├── dev/
│           └── prod/
│
├── docker-compose.yml          # Lokales Multi-Container-Setup
├── docker-compose.override.yml # Lokale Dev-Overrides (Volume Mounts, Debugger)
├── .env.example                # Vorlage aller benötigten Umgebungsvariablen
├── .gitignore
└── README.md
```

</details>

---

## ⚡ Schnellstart (Lokale Entwicklung)

### Voraussetzungen
* Docker und Docker Compose
* Git

### Installation

1. **Repository klonen:**
   ```bash
   git clone [https://github.com/dein-user/politiklar.git](https://github.com/dein-user/politiklar.git)
   cd politiklar
   ```

2. **Umgebungsvariablen einrichten:**
   ```bash
   cp .env.example .env
   ```

3. **Container-Stack starten:**
   ```bash
   docker compose up --build -d
   ```

* Frontend: `http://localhost:3000`
* FastAPI Docs: `http://localhost:8000/docs`
* Vektor-DB Web-UI: `http://localhost:6333/dashboard` (falls Qdrant genutzt wird)

---

## 🎓 Mitwirken & Zusammenarbeit für Studierende

Politiklar ist interdisziplinär konzipiert. Wir bieten Studierenden der Informatik, Politikwissenschaft, Sozialwissenschaften und des Datenjournalismus die Möglichkeit, praktische Erfahrungen an einem echten Open-Source-Projekt zu sammeln.

Mögliche Schwerpunkte für **Praxissemester, Bachelor-/Masterarbeiten oder Projektarbeiten**:
* **Informatik / AI Engineering:** Evaluierung von RAG-Pipelines, Chunking-Strategien für Gesetzestexte, MCP-Server-Erweiterungen, Performance lokaler Embeddings.
* **Politik- & Sozialwissenschaften:** Validierung von Datenquellen, Konzeption neutraler Bewertungsmetriken für parlamentarische Transparenz, Usability für Bürger.
* **Medien & Journalismus:** Datenvisualisierung komplexer Gesetzgebungsprozesse, Aufbereitung von Erklärformaten.

<details>
<summary><b>Wissenschaftliche Schwerpunkte im Detail anzeigen</b></summary>

* **Politikwissenschaft:** Analyse parlamentarischer Kommunikation, Transparenzforschung, Stärkung der Deliberation.
* **Informatik:** Skalierbare Webcrawler, hybride Suchverfahren (BM25 + Dense Vectors), Reproduzierbarkeit von LLM-Outputs.
* **Medienwissenschaft:** Bekämpfung von Desinformation durch direkte Quellenverlinkung, Datenjournalismus.
</details>

---

## 🗺️ Roadmap & Phasen

* [x] **Phase 1: Proof of Concept (Monate 0–3)** – Basis-Architektur, Docker-Setup, FastAPI + Next.js Grundgerüst, MCP-Server, RAG-Pipeline.
* [ ] **Phase 2: Community & Hochschul-Kooperationen (Monate 3–6)** – Onboarding erster Studierender, Integration von Primärquellen (z. B. DIP21 / Bundestag-API).
* [ ] **Phase 3: Teamaufbau & Strukturierung (Monate 6–12)** – Feste Verantwortlichkeiten in Backend, Data-Pipelines und Frontend.
* [ ] **Phase 4: Vereinsgründung (Monate 12–18)** – Gründung von *Politiklar e.V.*, Anerkennung der Gemeinnützigkeit.
* [ ] **Phase 5: Verstetigung & Förderung (Monate 18–36)** – Akquise von Stiftungsgeldern und öffentlichen Fördermitteln für Civic Tech.

## 📄 Lizenz

Dieses Projekt ist unter der **MIT-Lizenz** lizenziert – siehe die Datei [LICENSE](LICENSE) für Details.

Copyright © 2026 Norman Pendzich.

Das Projekt ist quelloffen und lädt zur freien Nutzung, Modifikation und Zusammenarbeit im Rahmen von Lehre, Forschung und Civic-Tech-Initiativen ein.