"use client";

import React, { useState, useEffect, useCallback } from "react";
import Image from "next/image";
import { useSession, signIn, signOut } from "next-auth/react";

interface ApiKeyItem {
  id: string;
  name: string;
  key_prefix: string;
  is_active: boolean;
  created_at: string;
}

interface FavoriteItem {
  id: string;
  entity_type: string;
  entity_id: string;
  created_at: string;
}

export default function AccountPage() {
  const { data: session, status } = useSession();
  const [apiKeys, setApiKeys] = useState<ApiKeyItem[]>([]);
  const [favorites, setFavorites] = useState<FavoriteItem[]>([]);
  const [newKeyName, setNewKeyName] = useState("");
  const [createdRawKey, setCreatedRawKey] = useState<string | null>(null);
  const [isLoadingKeys, setIsLoadingKeys] = useState(false);
  const [keyError, setKeyError] = useState<string | null>(null);

  const userId = session?.user?.id;
  const user = session?.user;
  const role = (user as { role?: string })?.role || "user";
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const fetchUserData = useCallback(async () => {
    if (!userId) return;
    try {
      setIsLoadingKeys(true);
      // Fetch API Keys
      const keysRes = await fetch(`${apiUrl}/api/v1/auth/users/${userId}/api-keys`).catch(() => null);
      if (keysRes && keysRes.ok) {
        const data = await keysRes.json();
        setApiKeys(data);
      }
      // Fetch Favorites
      const favsRes = await fetch(`${apiUrl}/api/v1/auth/users/${userId}/favorites`).catch(() => null);
      if (favsRes && favsRes.ok) {
        const data = await favsRes.json();
        setFavorites(data);
      }
    } catch {
      // Backend might be quiet
    } finally {
      setIsLoadingKeys(false);
    }
  }, [userId, apiUrl]);

  useEffect(() => {
    if (userId) {
      fetchUserData();
    }
  }, [userId, fetchUserData]);

  async function handleCreateApiKey(e: React.FormEvent) {
    e.preventDefault();
    if (!userId || !newKeyName.trim()) return;
    try {
      setKeyError(null);
      const res = await fetch(`${apiUrl}/api/v1/auth/users/${userId}/api-keys`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: newKeyName.trim() }),
      });
      if (!res.ok) {
        throw new Error("Fehler beim Erstellen des Schlüssels");
      }
      const data = await res.json();
      setCreatedRawKey(data.raw_key);
      setNewKeyName("");
      fetchUserData();
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Schlüssel konnte nicht erstellt werden";
      setKeyError(message);
    }
  }

  if (status === "loading") {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16 text-center">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mb-4" />
        <p className="text-sm text-gray-500">Lade Benutzerkonto...</p>
      </div>
    );
  }

  if (!session || !user) {
    return (
      <div className="max-w-md mx-auto my-16 p-8 bg-white border border-gray-200 rounded-2xl shadow-sm text-center">
        <div className="w-12 h-12 rounded-full bg-blue-50 text-blue-600 mx-auto mb-4 flex items-center justify-center">
          <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.75} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
          </svg>
        </div>
        <h1 className="text-xl font-bold text-gray-900 mb-2">Anmeldung erforderlich</h1>
        <p className="text-xs text-gray-600 mb-6 leading-relaxed">
          Um dein Profil, Favoriten und API-/MCP-Schlüssel zu verwalten, melde dich bitte an.
        </p>
        <button
          type="button"
          onClick={() => signIn("google")}
          className="w-full inline-flex items-center justify-center gap-3 px-4 py-2.5 bg-white border border-gray-300 rounded-xl hover:bg-gray-50 text-sm font-medium text-gray-700 shadow-sm transition"
        >
          <svg className="w-4 h-4" viewBox="0 0 24 24">
            <path fill="#4285F4" d="M23.745 12.27c0-.7-.06-1.4-.19-2.07H12v4.51h6.6c-.29 1.52-1.14 2.82-2.4 3.68v3.05h3.88c2.27-2.09 3.66-5.17 3.66-9.17z" />
            <path fill="#34A853" d="M12 24c3.24 0 5.95-1.08 7.93-2.91l-3.88-3.05c-1.08.72-2.45 1.16-4.05 1.16-3.12 0-5.77-2.1-6.72-4.93H1.25v3.15C3.26 21.36 7.33 24 12 24z" />
            <path fill="#FBBC05" d="M5.28 14.27A7.16 7.16 0 0 1 4.9 12c0-.79.14-1.57.38-2.27V6.58H1.25A11.96 11.96 0 0 0 0 12c0 1.92.45 3.74 1.25 5.42l4.03-3.15z" />
            <path fill="#EA4335" d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C17.95 1.19 15.24 0 12 0 7.33 0 3.26 2.64 1.25 6.58l4.03 3.15c.95-2.83 3.6-4.98 6.72-4.98z" />
          </svg>
          Mit Google anmelden
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-10 space-y-8">
      {/* Profile Overview Card */}
      <div className="bg-white rounded-2xl border border-gray-200 p-6 sm:p-8 shadow-sm">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            {user.image ? (
              <Image
                src={user.image}
                alt={user.name || "Profilbild"}
                width={64}
                height={64}
                className="w-16 h-16 rounded-full object-cover border border-gray-200"
              />
            ) : (
              <div className="w-16 h-16 rounded-full bg-blue-600 text-white font-bold text-xl flex items-center justify-center">
                {user.name ? user.name.charAt(0).toUpperCase() : "U"}
              </div>
            )}
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-xl font-bold text-gray-900">{user.name || "Benutzer"}</h1>
                <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-semibold bg-blue-50 text-blue-700 border border-blue-200">
                  {role === "admin" ? "Administrator" : "Benutzer"}
                </span>
              </div>
              <p className="text-sm text-gray-500 mt-0.5">{user.email}</p>
              <p className="text-[11px] text-gray-400 mt-1">Authentifiziert über Google OAuth 2.0</p>
            </div>
          </div>
          <button
            type="button"
            onClick={() => signOut({ callbackUrl: "/" })}
            className="px-4 py-2 text-xs font-medium text-red-600 bg-red-50 hover:bg-red-100 rounded-xl transition-colors"
          >
            Abmelden
          </button>
        </div>
      </div>

      {/* Favorites Section */}
      <div id="favoriten" className="bg-white rounded-2xl border border-gray-200 p-6 sm:p-8 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-base font-bold text-gray-900">Gespeicherte Favoriten & Beobachtungen</h2>
            <p className="text-xs text-gray-500 mt-1">
              Deine gemerkten Abgeordneten, Gesetze und Themendossiers.
            </p>
          </div>
        </div>
        {favorites.length === 0 ? (
          <div className="text-center py-8 border border-dashed border-gray-200 rounded-xl">
            <p className="text-xs text-gray-500">Du hast noch keine Favoriten gespeichert.</p>
            <p className="text-[11px] text-gray-400 mt-1">Klicke auf den Abgeordneten- oder Dossier-Seiten auf das Stern-Symbol, um Einträge zu merken.</p>
          </div>
        ) : (
          <ul className="divide-y divide-gray-100">
            {favorites.map((fav) => (
              <li key={fav.id} className="py-3 flex items-center justify-between">
                <div>
                  <span className="text-xs font-medium text-gray-800 uppercase">{fav.entity_type}</span>
                  <p className="text-xs text-gray-500">ID: {fav.entity_id}</p>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* API & MCP Keys Section */}
      <div id="api-keys" className="bg-white rounded-2xl border border-gray-200 p-6 sm:p-8 shadow-sm space-y-6">
        <div>
          <h2 className="text-base font-bold text-gray-900">API- & MCP-Server-Schlüssel</h2>
          <p className="text-xs text-gray-500 mt-1">
            Verwende sichere Authentifizierungs-Tokens für das Model Context Protocol (MCP) und externe Abfragen.
          </p>
        </div>

        {/* Modal-like banner for newly created key */}
        {createdRawKey && (
          <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-xl space-y-2 animate-in fade-in">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-emerald-800">Neuer Schlüssel erstellt!</span>
              <button
                type="button"
                onClick={() => setCreatedRawKey(null)}
                className="text-xs text-emerald-600 hover:text-emerald-900 font-medium"
              >
                Ausblenden
              </button>
            </div>
            <p className="text-[11px] text-emerald-700">
              Kopiere diesen Schlüssel jetzt. Er wird aus Sicherheitsgründen nicht erneut angezeigt:
            </p>
            <div className="flex items-center gap-2">
              <input
                type="text"
                readOnly
                value={createdRawKey}
                className="flex-1 px-3 py-1.5 bg-white border border-emerald-300 rounded-lg text-xs font-mono text-gray-800 select-all"
              />
              <button
                type="button"
                onClick={() => navigator.clipboard.writeText(createdRawKey)}
                className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-medium transition-colors"
              >
                Kopieren
              </button>
            </div>
          </div>
        )}

        {/* Key Creation Form */}
        <form onSubmit={handleCreateApiKey} className="flex gap-3">
          <input
            type="text"
            value={newKeyName}
            onChange={(e) => setNewKeyName(e.target.value)}
            placeholder="Schlüsselname (z. B. MCP Claude Desktop)"
            className="flex-1 px-3.5 py-2 text-xs border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            type="submit"
            disabled={!newKeyName.trim()}
            className="px-4 py-2 bg-gray-900 hover:bg-black text-white text-xs font-semibold rounded-xl transition-colors disabled:opacity-50"
          >
            Schlüssel erzeugen
          </button>
        </form>
        {keyError && <p className="text-xs text-red-600">{keyError}</p>}

        {/* Existing keys */}
        <div>
          <h3 className="text-xs font-semibold text-gray-700 mb-2">Aktive Schlüssel</h3>
          {isLoadingKeys ? (
            <p className="text-xs text-gray-400">Lade Schlüssel...</p>
          ) : apiKeys.length === 0 ? (
            <p className="text-xs text-gray-500 py-3">Es wurden noch keine API-Schlüssel erstellt.</p>
          ) : (
            <div className="divide-y divide-gray-100 border border-gray-100 rounded-xl overflow-hidden">
              {apiKeys.map((key) => (
                <div key={key.id} className="px-4 py-3 flex items-center justify-between text-xs bg-gray-50/50">
                  <div>
                    <span className="font-semibold text-gray-800">{key.name}</span>
                    <span className="ml-2 font-mono text-gray-400">{key.key_prefix}...</span>
                  </div>
                  <span className="text-[11px] text-gray-400">
                    Erstellt am {new Date(key.created_at).toLocaleDateString("de-DE")}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
