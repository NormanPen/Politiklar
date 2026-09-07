"use client";

import { useState } from "react";

export default function StateTest() {
  // 1. Einfacher Zahlen-State (Counter)
  const [count, setCount] = useState(0);

  // 2. Text-Input State
  const [searchTerm, setSearchTerm] = useState("");

  // 3. Array-State (z. B. für Filter oder Listen)
  const [selectedParty, setSelectedParty] = useState<string | null>(null);

  const parties = ["SPD", "CDU/CSU", "Bündnis 90/Die Grünen", "FDP", "AfD", "Die Linke"];

  // Gefilterte Parteien basierend auf der Suche
  const filteredParties = parties.filter((p) =>
    p.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="max-w-xl mx-auto my-8 p-6 bg-white rounded-xl shadow-md border border-gray-100 space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">State Management Demo</h1>
        <p className="text-sm text-gray-500 mt-1">
          Wichtig: Diese Komponente nutzt ganz oben <code className="bg-gray-100 px-1 py-0.5 rounded text-pink-600 font-mono text-xs">"use client";</code>
        </p>
      </div>

      {/* Beispiel 1: Zähler (useState Zahl) */}
      <section className="p-4 bg-gray-50 rounded-lg space-y-3">
        <h2 className="text-base font-semibold text-gray-800">1. Klick-Zähler (Zahl)</h2>
        <div className="flex items-center gap-4">
          <span className="text-3xl font-bold text-indigo-600 min-w-12 text-center">
            {count}
          </span>
          <div className="flex gap-2">
            <button
              onClick={() => setCount(count + 1)}
              className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium rounded-md transition"
            >
              + 1
            </button>
            <button
              onClick={() => setCount(count - 1)}
              className="px-3 py-1.5 bg-gray-200 hover:bg-gray-300 text-gray-700 text-sm font-medium rounded-md transition"
            >
              - 1
            </button>
            <button
              onClick={() => setCount(0)}
              className="px-3 py-1.5 text-gray-500 hover:text-gray-700 text-sm font-medium underline"
            >
              Reset
            </button>
          </div>
        </div>
      </section>

      {/* Beispiel 2: Suchfeld & Listen-Filterung */}
      <section className="p-4 bg-gray-50 rounded-lg space-y-3">
        <h2 className="text-base font-semibold text-gray-800">2. Interaktive Suche & Auswahl</h2>
        
        {/* Input gebunden an Such-State */}
        <input
          type="text"
          placeholder="Fraktion filtern..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm"
        />

        {/* Buttons für Parteien-Auswahl */}
        <div className="flex flex-wrap gap-2 pt-2">
          {filteredParties.map((party) => {
            const isSelected = selectedParty === party;
            return (
              <button
                key={party}
                onClick={() => setSelectedParty(isSelected ? null : party)}
                className={`px-3 py-1.5 rounded-full text-xs font-semibold transition ${
                  isSelected
                    ? "bg-indigo-600 text-white shadow-sm"
                    : "bg-white text-gray-700 border border-gray-200 hover:border-gray-400"
                }`}
              >
                {party} {isSelected && "✓"}
              </button>
            );
          })}
        </div>

        {/* Status-Ausgabe */}
        <div className="mt-3 text-xs text-gray-500 border-t border-gray-200 pt-2">
          Aktuell ausgewählt:{" "}
          <strong className="text-gray-800">{selectedParty ?? "Keine Fraktion"}</strong>
        </div>
      </section>
    </div>
  );
}
