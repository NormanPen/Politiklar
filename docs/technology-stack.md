# Technologie-Stack

| Bereich | Aktuell eingesetzt | Geplant oder vorbereitet |
| --- | --- | --- |
| Datenbank | PostgreSQL 17, pgvector, SQLAlchemy 2.0, Alembic, psycopg | Qdrant fuer verteilte Embeddings (optional) |
| Crawler | Python, httpx, selectolax, openpyxl | Weitere amtliche Importer |
| API | FastAPI, Uvicorn, Pydantic V2 | Erweiterte GraphQL/gRPC-Schnittstellen |
| Konfiguration | Pydantic Settings, `.env`-Dateien | Docker Secrets fuer produktive Geheimnisse |
| Betrieb | Docker Compose, Make, Dockerfile (Backend-Image, Web-Image) | Production Reverse-Proxy |
| Web | Next.js 16 (Turbopack), React 19, TypeScript, Tailwind CSS v4, NextAuth v5 | Erweiterte Dashboard-Ansichten |
| KI & MCP | Modularer `AIProvider` (Gemini, LangChain), pgvector RAG-Pipeline, Politiklar MCP-Server (`mcp>=1.2`) | Optionale lokale Ollama/vLLM-Modelle |

Technologieentscheidungen richten sich an nachverfolgbaren, reproduzierbaren Quellenimporten aus. Geplante Komponenten sind noch kein Teil des laufenden Stacks.

Zurueck zur [Dokumentationsuebersicht](README.md).