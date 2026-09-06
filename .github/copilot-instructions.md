# Politiklar Copilot Instructions

Politiklar is a civic-tech project that aggregates official German political sources and presents searchable, traceable information. Keep changes small, verifiable, and consistent with the architecture described in [README.md](../README.md).

## Project boundaries

- `apps/backend` contains Python services, APIs, data ingestion, persistence, and future MCP integrations.
- `apps/web` contains the Next.js web application.
- Treat the current directory tree as authoritative for what exists. Do not invent commands, modules, workflows, or dependencies that are not present in the repository.

## Data and AI integrity

- Preserve source provenance for every crawled, transformed, retrieved, or displayed political fact.
- Prefer primary, official sources and retain the original URL, publication metadata, retrieval time, and source identity where the data model supports them.
- Do not present an inference or generated summary as a source fact. RAG responses must be grounded in retrieved evidence and should abstain when the evidence is insufficient.
- Use neutral, descriptive language. Do not introduce political endorsements, unsupported rankings, or claims about intent.
- Make ingestion and transformations reproducible and idempotent where practical.

## Engineering workflow

- Inspect nearby code, manifests, and tests before choosing a library or command.
- Add or update focused tests for behavioral changes. Run the narrowest relevant validation available, then broader checks when they exist.
- Keep public API contracts and persisted data changes explicit. Database changes require a migration and a rollback or compatibility check.
- Never commit secrets, tokens, private source data, or local environment files. Update `.env.example` for new configuration keys when that file exists.
- Document new setup or validation commands in the project documentation instead of hiding them in Copilot instructions.