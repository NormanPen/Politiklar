"use client";

import React, { useState } from "react";

interface McpClientSetupProps {
  apiKey?: string | null;
}

type ClientTab = "antigravity" | "claude" | "cursor" | "python";

export default function McpClientSetup({ apiKey }: McpClientSetupProps) {
  const [activeTab, setActiveTab] = useState<ClientTab>("antigravity");
  const [copied, setCopied] = useState(false);

  // Use the generated key or placeholder
  const displayKey = apiKey && apiKey.trim().length > 0 ? apiKey.trim() : "pk_live_dein_api_schluessel";
  const hasLiveKey = Boolean(apiKey && apiKey.trim().length > 0);

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const antigravityConfig = `{
  "mcpServers": {
    "politiklar": {
      "command": "apps/backend/.venv/bin/politiklar-mcp",
      "args": ["stdio"],
      "env": {
        "POLITIKLAR_API_KEY": "${displayKey}"
      }
    }
  }
}`;

  const claudeConfig = `{
  "mcpServers": {
    "politiklar": {
      "command": "apps/backend/.venv/bin/politiklar-mcp",
      "args": ["stdio"],
      "env": {
        "POLITIKLAR_API_KEY": "${displayKey}"
      }
    }
  }
}`;

  const cursorConfig = `{
  "mcpServers": {
    "politiklar": {
      "command": "apps/backend/.venv/bin/politiklar-mcp",
      "args": ["stdio"],
      "env": {
        "POLITIKLAR_API_KEY": "${displayKey}"
      }
    }
  }
}`;

  const pythonSnippet = `import os
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    server_params = StdioServerParameters(
        command="apps/backend/.venv/bin/politiklar-mcp",
        args=["stdio"],
        env={"POLITIKLAR_API_KEY": "${displayKey}", **os.environ}
    )
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # 1. Verfügbare Tools listen
            tools = await session.list_tools()
            print("Verfügbare Tools:", [t.name for t in tools.tools])

            # 2. Amtliches Abgeordneten-Profil abfragen
            profile = await session.call_tool(
                "get_member_profile", 
                {"name_or_mdb_id": "Jan van Aken"}
            )
            print("Profil-Daten:", profile)

asyncio.run(main())`;

  const tabs: { id: ClientTab; label: string; icon: string; badge: string }[] = [
    { id: "antigravity", label: "Google Antigravity", icon: "🚀", badge: ".agents/mcp_config.json" },
    { id: "claude", label: "Claude Desktop", icon: "🟣", badge: "claude_desktop_config.json" },
    { id: "cursor", label: "Cursor & Windsurf", icon: "⚡", badge: "Settings / .cursor" },
    { id: "python", label: "Python & OpenAI SDK", icon: "🐍", badge: "mcp SDK Script" },
  ];

  const getCurrentSnippet = () => {
    switch (activeTab) {
      case "antigravity":
        return antigravityConfig;
      case "claude":
        return claudeConfig;
      case "cursor":
        return cursorConfig;
      case "python":
        return pythonSnippet;
    }
  };

  return (
    <div className="mt-8 pt-8 border-t border-gray-100 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h3 className="text-sm font-bold text-gray-900 flex items-center gap-2">
            <span>🔌</span> Client-Einbindung (MCP Model Context Protocol)
          </h3>
          <p className="text-xs text-gray-500 mt-0.5">
            Verbinde deinen KI-Assistenten in Sekunden mit den amtlichen Bundestags-Daten von Politiklar.
          </p>
        </div>
        {hasLiveKey ? (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium bg-emerald-50 text-emerald-700 border border-emerald-200 self-start sm:self-auto">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
            Schlüssel wird unten direkt eingesetzt
          </span>
        ) : (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium bg-amber-50 text-amber-700 border border-amber-200 self-start sm:self-auto">
            💡 Erzeuge oben einen Schlüssel für automatische Einsetzung
          </span>
        )}
      </div>

      {/* Tabs */}
      <div className="flex flex-wrap gap-2 border-b border-gray-100 pb-3">
        {tabs.map((tab) => {
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              type="button"
              onClick={() => {
                setActiveTab(tab.id);
                setCopied(false);
              }}
              className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-semibold transition-all ${
                isActive
                  ? "bg-gray-900 text-white shadow-sm"
                  : "bg-gray-50 text-gray-600 hover:bg-gray-100 hover:text-gray-900"
              }`}
            >
              <span>{tab.icon}</span>
              <span>{tab.label}</span>
              <span
                className={`text-[10px] px-1.5 py-0.5 rounded-md font-mono ${
                  isActive ? "bg-gray-800 text-gray-300" : "bg-white text-gray-400 border border-gray-200"
                }`}
              >
                {tab.badge}
              </span>
            </button>
          );
        })}
      </div>

      {/* Tab Content Instructions */}
      <div className="bg-gray-50/70 border border-gray-200/80 rounded-2xl p-5 space-y-4">
        {activeTab === "antigravity" && (
          <div className="space-y-2 text-xs text-gray-600">
            <p className="font-semibold text-gray-900">
              Einrichtung in Google Antigravity (AGY) & Antigravity IDE:
            </p>
            <ol className="list-decimal list-inside space-y-1 text-gray-600 leading-relaxed">
              <li>
                Erstelle oder öffne in deinem Projektverzeichnis die Datei{" "}
                <code className="font-mono bg-white px-1.5 py-0.5 rounded border border-gray-200 text-sky-700">
                  .agents/mcp_config.json
                </code>{" "}
                (oder global unter{" "}
                <code className="font-mono bg-white px-1.5 py-0.5 rounded border border-gray-200 text-sky-700">
                  ~/.gemini/antigravity-ide/mcp_config.json
                </code>
                ).
              </li>
              <li>Füge das untenstehende JSON-Snippet ein. Der API-Schlüssel wird als Umgebungsvariable übergeben.</li>
              <li>
                Dein Antigravity-Agent kann die 5 Politiklar-Tools nun autonom aufrufen und Quellen zitieren.
              </li>
            </ol>
          </div>
        )}

        {activeTab === "claude" && (
          <div className="space-y-2 text-xs text-gray-600">
            <p className="font-semibold text-gray-900">
              Einrichtung in Claude Desktop (Anthropic):
            </p>
            <p className="leading-relaxed">
              Öffne die Konfigurationsdatei{" "}
              <code className="font-mono bg-white px-1.5 py-0.5 rounded border border-gray-200 text-purple-700">
                claude_desktop_config.json
              </code>{" "}
              an folgendem Pfad:
            </p>
            <ul className="list-disc list-inside space-y-0.5 text-gray-500 font-mono text-[11px]">
              <li>macOS: ~/Library/Application Support/Claude/claude_desktop_config.json</li>
              <li>Windows: %APPDATA%\Claude\claude_desktop_config.json</li>
              <li>Linux: ~/.config/Claude/claude_desktop_config.json</li>
            </ul>
            <p className="leading-relaxed">
              Füge den Server unter <code className="font-mono bg-white px-1 py-0.5 rounded">mcpServers</code> ein und
              starte Claude Desktop neu. Im Eingabefeld erscheint das Hammer-Icon (🔨).
            </p>
          </div>
        )}

        {activeTab === "cursor" && (
          <div className="space-y-2 text-xs text-gray-600">
            <p className="font-semibold text-gray-900">
              Einrichtung in Cursor & Windsurf:
            </p>
            <ol className="list-decimal list-inside space-y-1 text-gray-600 leading-relaxed">
              <li>
                Öffne in den Einstellungen: <strong>Settings → Features → MCP Servers → Add new MCP server</strong>.
              </li>
              <li>
                Typ auf <strong>command (stdio)</strong> stellen, Name <strong>politiklar</strong> vergeben.
              </li>
              <li>
                Alternativ im Projekt-Root als{" "}
                <code className="font-mono bg-white px-1.5 py-0.5 rounded border border-gray-200 text-sky-700">
                  .cursor/mcp.json
                </code>{" "}
                ablegen (siehe Konfiguration unten).
              </li>
            </ol>
          </div>
        )}

        {activeTab === "python" && (
          <div className="space-y-2 text-xs text-gray-600">
            <p className="font-semibold text-gray-900">
              Verwendung via Python SDK & OpenAI Function Calling:
            </p>
            <p className="leading-relaxed">
              Installiere das offizielle MCP-Paket mit{" "}
              <code className="font-mono bg-white px-1.5 py-0.5 rounded border border-gray-200 text-emerald-700">
                pip install mcp
              </code>
              . Das folgende Skript verbindet sich via Stdio und ruft Abgeordneten-Daten ab:
            </p>
          </div>
        )}

        {/* Code Snippet Box */}
        <div className="relative rounded-xl overflow-hidden bg-gray-900 border border-gray-800 shadow-inner">
          <div className="flex items-center justify-between px-4 py-2 bg-gray-950/80 border-b border-gray-800 text-[11px] text-gray-400 font-mono">
            <span>
              {activeTab === "python" ? "mcp_client_example.py" : "mcp_config.json"}
            </span>
            <button
              type="button"
              onClick={() => handleCopy(getCurrentSnippet())}
              className={`flex items-center gap-1.5 px-3 py-1 rounded-lg font-sans font-medium text-xs transition-colors ${
                copied
                  ? "bg-emerald-600 text-white"
                  : "bg-gray-800 hover:bg-gray-700 text-gray-200 hover:text-white"
              }`}
            >
              {copied ? (
                <>
                  <span>✓</span>
                  <span>Kopiert!</span>
                </>
              ) : (
                <>
                  <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
                    />
                  </svg>
                  <span>Konfiguration kopieren</span>
                </>
              )}
            </button>
          </div>

          <pre className="p-4 text-xs font-mono text-gray-200 overflow-x-auto leading-relaxed select-all">
            <code>{getCurrentSnippet()}</code>
          </pre>
        </div>
      </div>

      {/* Available Tools Grid */}
      <div className="space-y-3">
        <h4 className="text-xs font-bold text-gray-700 uppercase tracking-wider">
          Verfügbare MCP-Werkzeuge in Politiklar
        </h4>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div className="p-3 bg-white border border-gray-200 rounded-xl">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-sm">🏛️</span>
              <span className="text-xs font-bold font-mono text-gray-900">get_member_profile</span>
            </div>
            <p className="text-[11px] text-gray-500 leading-snug">
              Liefert amtliche Stammdaten, Biografie, Ausschussmitgliedschaften und verifizierte Nebeneinkünfte eines Abgeordneten.
            </p>
          </div>

          <div className="p-3 bg-white border border-gray-200 rounded-xl">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-sm">🗳️</span>
              <span className="text-xs font-bold font-mono text-gray-900">get_named_vote</span>
            </div>
            <p className="text-[11px] text-gray-500 leading-snug">
              Amtliches Gesamtergebnis namentlicher Abstimmungen mit Fraktionsauflistung (Ja / Nein / Enthalten / Nicht abgegeben).
            </p>
          </div>

          <div className="p-3 bg-white border border-gray-200 rounded-xl">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-sm">📜</span>
              <span className="text-xs font-bold font-mono text-gray-900">list_named_votes</span>
            </div>
            <p className="text-[11px] text-gray-500 leading-snug">
              Chronologische Übersicht kürzlicher namentlicher Abstimmungen der 21. Wahlperiode mit Sitzungsnummern.
            </p>
          </div>

          <div className="p-3 bg-white border border-gray-200 rounded-xl">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-sm">🔍</span>
              <span className="text-xs font-bold font-mono text-gray-900">ask_bundestag_rag</span>
            </div>
            <p className="text-[11px] text-gray-500 leading-snug">
              Quellenbasierte Recherche in Plenarprotokollen und Reden mit exakten Zitatnachweisen (RAG-Pipeline).
            </p>
          </div>

          <div className="p-3 bg-white border border-gray-200 rounded-xl sm:col-span-2">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-sm">🎙️</span>
              <span className="text-xs font-bold font-mono text-gray-900">search_speeches</span>
            </div>
            <p className="text-[11px] text-gray-500 leading-snug">
              Semantische Vektorsuche (pgvector) in parlamentarischen Reden nach Themen mit Ähnlichkeitsscores und Rednernachweisen.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
