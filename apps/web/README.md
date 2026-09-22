# Politiklar Web (Frontend)

Die Webanwendung von Politiklar ist das moderne, benutzerfreundliche Frontend zur Darstellung transparenter und nachvollziehbarer Daten des Deutschen Bundestages. Sie ist mit **Next.js 16 (App Router)**, **React 19**, **TypeScript** und **Tailwind CSS** aufgebaut.

---

## 🏛️ Architektur & Zusammenspiel

Das Frontend konsumiert die Daten des Python-Backends über die strukturierte REST-API:

```text
[Browser / User]
       │
       ▼
[apps/web (Next.js - Port 3000)]
       │ (REST / JSON)
       ▼
[apps/backend (FastAPI - Port 8000)]
       │
       ▼
[PostgreSQL 17 Database]
```

---

## 📂 Struktur

```text
apps/web/
├── src/
│   └── app/                # Next.js App Router
│       ├── layout.tsx      # Globales HTML-Layout, Fonts & Themes
│       ├── page.tsx        # Startseite
│       └── globals.css     # Globale Styling-Regeln & Design-Tokens
├── public/                 # Statische Assets (Icons, Logos)
├── Dockerfile              # Docker-Containerisierung für Produktion
├── package.json            # NPM-Dependencies & Scripts
└── tsconfig.json           # TypeScript-Konfiguration
```

---

## 🛠️ Entwicklung

### Über Docker (Empfohlen im Gesamtprojekt)
Die Anwendung startet automatisch mit dem Gesamt-Stack:
```bash
# Im Projekt-Root:
make setup-dev   # oder: make up
```
* **Frontend:** [http://localhost:3000](http://localhost:3000)
* **Backend API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

### Lokale Entwicklung (Node.js auf dem Host)
Falls du direkt im Frontend-Verzeichnis mit lokalem `npm` arbeiten möchtest:

```bash
cd apps/web
npm install
npm run dev
```

### Scripts

| Befehl | Beschreibung |
| :--- | :--- |
| `npm run dev` | Startet den Next.js Entwicklungsserver mit Hot-Reloading |
| `npm run build` | Erzeugt das optimierte Produktions-Build |
| `npm run start` | Startet den Produktions-Server nach dem Build |
| `npm run lint` | Führt ESLint-Prüfungen aus |

---

## 📖 Weiterführende Dokumentation

* [Gesamtprojekt-Übersicht](../../README.md)
* [Backend-Dokumentation](../backend/README.md)
* [Datenbankschema & Modelle](../../docs/database-schema.md)
