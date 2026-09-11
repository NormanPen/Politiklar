"use client";

import React, { useState, useRef, useEffect } from "react";
import Image from "next/image";
import Link from "next/link";
import { useSession, signOut } from "next-auth/react";
import AuthModal from "./AuthModal";

export default function UserMenu() {
  const { data: session, status } = useSession();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  // Close dropdown on outside click
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setDropdownOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  if (!session?.user) {
    return (
      <>
        <button
          type="button"
          onClick={() => setModalOpen(true)}
          className="p-1 text-black hover:opacity-60 cursor-pointer transition-opacity focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-black rounded"
          aria-label="Anmelden / Benutzerkonto"
        >
          <svg
            width="16"
            height="16"
            viewBox="0 0 16 16"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
            className="w-4 h-4 text-black block pointer-events-none"
            aria-hidden="true"
          >
            <circle cx="8" cy="8" r="7" stroke="currentColor" strokeWidth="1.2" />
            <circle cx="8" cy="6.2" r="2.2" stroke="currentColor" strokeWidth="1.2" />
            <path
              d="M3.7 12.7C4.5 10.5 6.1 9.4 8 9.4C9.9 9.4 11.5 10.5 12.3 12.7"
              stroke="currentColor"
              strokeWidth="1.2"
              strokeLinecap="round"
            />
          </svg>
        </button>
        <AuthModal isOpen={modalOpen} onClose={() => setModalOpen(false)} />
      </>
    );
  }

  const user = session.user;
  const role = (user as { role?: string }).role || "user";

  return (
    <div className="relative" ref={menuRef}>
      <button
        type="button"
        onClick={() => setDropdownOpen((prev) => !prev)}
        className="flex items-center gap-2 p-0.5 rounded-full hover:ring-2 hover:ring-gray-300 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-black transition-all"
        aria-label="Benutzermenü öffnen"
        aria-expanded={dropdownOpen}
      >
        {user.image ? (
          <Image
            src={user.image}
            alt={user.name || "Profilbild"}
            width={28}
            height={28}
            className="w-7 h-7 rounded-full object-cover border border-gray-200"
          />
        ) : (
          <div className="w-7 h-7 rounded-full bg-blue-600 text-white font-medium text-xs flex items-center justify-center">
            {user.name ? user.name.charAt(0).toUpperCase() : "U"}
          </div>
        )}
      </button>

      {dropdownOpen && (
        <div className="absolute right-0 mt-2 w-64 bg-white rounded-xl shadow-lg border border-gray-100 py-2 z-50 animate-in fade-in slide-in-from-top-1 duration-150">
          {/* User info */}
          <div className="px-4 py-2 border-b border-gray-100">
            <p className="text-sm font-semibold text-gray-900 truncate">{user.name || "Benutzer"}</p>
            <p className="text-xs text-gray-500 truncate">{user.email}</p>
            <div className="mt-1 flex items-center gap-1.5">
              <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium bg-blue-50 text-blue-700 border border-blue-200">
                {role === "admin" ? "Administrator" : "Benutzer"}
              </span>
            </div>
          </div>

          {/* Links */}
          <div className="py-1">
            <Link
              href="/konto"
              onClick={() => setDropdownOpen(false)}
              className="flex items-center px-4 py-2 text-xs text-gray-700 hover:bg-gray-50 transition-colors"
            >
              Mein Konto & Profil
            </Link>
            <Link
              href="/konto#favoriten"
              onClick={() => setDropdownOpen(false)}
              className="flex items-center px-4 py-2 text-xs text-gray-700 hover:bg-gray-50 transition-colors"
            >
              Gespeicherte Favoriten
            </Link>
            <Link
              href="/konto#api-keys"
              onClick={() => setDropdownOpen(false)}
              className="flex items-center px-4 py-2 text-xs text-gray-700 hover:bg-gray-50 transition-colors"
            >
              API & MCP Schlüssel
            </Link>
          </div>

          {/* Sign out */}
          <div className="pt-1 border-t border-gray-100">
            <button
              type="button"
              onClick={() => {
                setDropdownOpen(false);
                signOut();
              }}
              className="w-full text-left px-4 py-2 text-xs text-red-600 hover:bg-red-50 transition-colors font-medium"
            >
              Abmelden
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
