"use client";

import React, { useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { signIn } from "next-auth/react";
import { registerUser } from "@/app/actions/register";

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function AuthModal({ isOpen, onClose }: AuthModalProps) {
  const modalRef = useRef<HTMLDivElement>(null);
  const [mounted, setMounted] = useState(false);

  // Tab State: "login" oder "register"
  const [authMode, setAuthMode] = useState<"login" | "register">("login");

  // Login Form State
  const [loginEmail, setLoginEmail] = useState("");
  const [loginPassword, setLoginPassword] = useState("");
  const [loginError, setLoginError] = useState<string | null>(null);
  const [isLoginPending, setIsLoginPending] = useState(false);

  // Register Form State
  const [regName, setRegName] = useState("");
  const [regEmail, setRegEmail] = useState("");
  const [regPassword, setRegPassword] = useState("");
  const [regError, setRegError] = useState<string | null>(null);
  const [regSuccess, setRegSuccess] = useState<string | null>(null);
  const [isRegPending, setIsRegPending] = useState(false);

  const [isGoogleLoading, setIsGoogleLoading] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  async function handleGoogleSignIn() {
    setIsGoogleLoading(true);
    try {
      await signIn("google", { redirectTo: "/", callbackUrl: "/" });
    } catch (err) {
      console.error("Sign in error, redirecting to signin page:", err);
      window.location.href = "/api/auth/signin";
    }
  }

  async function handleCredentialsLogin(e: React.FormEvent) {
    e.preventDefault();
    setLoginError(null);
    setIsLoginPending(true);
    try {
      const res = await signIn("credentials", {
        email: loginEmail.trim(),
        password: loginPassword,
        redirect: false,
      });

      if (res?.error) {
        setLoginError("E-Mail oder Passwort nicht korrekt oder E-Mail noch nicht bestätigt.");
      } else {
        onClose();
        window.location.reload();
      }
    } catch {
      setLoginError("Fehler bei der Anmeldung. Bitte überprüfe deine Angaben.");
    } finally {
      setIsLoginPending(false);
    }
  }

  async function handleRegister(e: React.FormEvent) {
    e.preventDefault();
    setRegError(null);
    setRegSuccess(null);
    setIsRegPending(true);
    try {
      const formData = new FormData();
      formData.set("name", regName.trim());
      formData.set("email", regEmail.trim());
      formData.set("password", regPassword);

      const res = await registerUser(null, formData);
      if (!res.success) {
        setRegError(res.error || "Registrierung fehlgeschlagen.");
      } else {
        setRegSuccess(res.message || "Bestätigungs-E-Mail gesendet! Bitte überprüfe dein Postfach.");
        setRegPassword("");
      }
    } catch {
      setRegError("Ein unerwarteter Fehler ist aufgetreten. Bitte versuche es später erneut.");
    } finally {
      setIsRegPending(false);
    }
  }

  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      if (e.key === "Escape") {
        onClose();
      }
    }
    if (isOpen) {
      document.addEventListener("keydown", handleKeyDown);
      document.body.style.overflow = "hidden";
    }
    return () => {
      document.removeEventListener("keydown", handleKeyDown);
      document.body.style.overflow = "unset";
    };
  }, [isOpen, onClose]);

  if (!isOpen || !mounted) return null;

  const modalContent = (
    <div
      className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/50 backdrop-blur-sm p-4 animate-in fade-in duration-200"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div
        ref={modalRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby="auth-modal-title"
        className="relative w-full max-w-md bg-white rounded-2xl shadow-2xl border border-gray-100 p-6 sm:p-8 text-gray-900 transition-all my-auto max-h-[90vh] overflow-y-auto"
      >
        {/* Close Button */}
        <button
          type="button"
          onClick={onClose}
          className="absolute top-4 right-4 p-2 text-gray-400 hover:text-gray-700 hover:bg-gray-100 rounded-full cursor-pointer transition-colors"
          aria-label="Schließen"
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>

        {/* Tab Switcher */}
        <div className="flex border-b border-gray-200 mb-6">
          <button
            type="button"
            onClick={() => {
              setAuthMode("login");
              setLoginError(null);
            }}
            className={`flex-1 pb-3 text-sm font-semibold transition-colors border-b-2 cursor-pointer ${
              authMode === "login"
                ? "border-sky-600 text-sky-600"
                : "border-transparent text-gray-500 hover:text-gray-700"
            }`}
          >
            Anmelden
          </button>
          <button
            type="button"
            onClick={() => {
              setAuthMode("register");
              setRegError(null);
              setRegSuccess(null);
            }}
            className={`flex-1 pb-3 text-sm font-semibold transition-colors border-b-2 cursor-pointer ${
              authMode === "register"
                ? "border-sky-600 text-sky-600"
                : "border-transparent text-gray-500 hover:text-gray-700"
            }`}
          >
            Konto erstellen
          </button>
        </div>

        {authMode === "login" ? (
          <div>
            <div className="text-center mb-6">
              <h2 id="auth-modal-title" className="text-xl font-bold tracking-tight text-gray-900 mb-1">
                Willkommen bei Politiklar
              </h2>
              <p className="text-xs text-gray-500">
                Melde dich mit deinem Konto an, um Favoriten zu speichern und die API zu nutzen.
              </p>
            </div>

            {loginError && (
              <div className="mb-4 p-3 bg-rose-50 border border-rose-200 rounded-xl text-xs text-rose-700">
                {loginError}
              </div>
            )}

            <form onSubmit={handleCredentialsLogin} className="space-y-3 mb-4">
              <div>
                <label className="block text-xs font-semibold text-gray-700 mb-1">
                  E-Mail-Adresse
                </label>
                <input
                  type="email"
                  required
                  value={loginEmail}
                  onChange={(e) => setLoginEmail(e.target.value)}
                  placeholder="name@beispiel.de"
                  className="w-full px-3 py-2 text-sm border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-sky-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-700 mb-1">
                  Passwort
                </label>
                <input
                  type="password"
                  required
                  value={loginPassword}
                  onChange={(e) => setLoginPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full px-3 py-2 text-sm border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-sky-500"
                />
              </div>

              <button
                type="submit"
                disabled={isLoginPending}
                className="w-full py-2.5 px-4 bg-sky-600 hover:bg-sky-500 disabled:opacity-50 text-white text-sm font-semibold rounded-xl shadow-sm transition cursor-pointer"
              >
                {isLoginPending ? "Wird angemeldet..." : "Mit E-Mail anmelden"}
              </button>
            </form>

            <div className="relative my-4 text-center">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-200" />
              </div>
              <span className="relative bg-white px-3 text-xs text-gray-400">
                oder
              </span>
            </div>

            <button
              type="button"
              onClick={handleGoogleSignIn}
              disabled={isGoogleLoading}
              className="w-full flex items-center justify-center gap-3 px-4 py-2.5 border border-gray-300 rounded-xl bg-white hover:bg-gray-50 cursor-pointer text-gray-700 font-medium text-sm shadow-sm transition disabled:opacity-60"
            >
              <svg className="w-4 h-4 flex-shrink-0" viewBox="0 0 24 24">
                <path fill="#4285F4" d="M23.745 12.27c0-.7-.06-1.4-.19-2.07H12v4.51h6.6c-.29 1.52-1.14 2.82-2.4 3.68v3.05h3.88c2.27-2.09 3.66-5.17 3.66-9.17z" />
                <path fill="#34A853" d="M12 24c3.24 0 5.95-1.08 7.93-2.91l-3.88-3.05c-1.08.72-2.45 1.16-4.05 1.16-3.12 0-5.77-2.1-6.72-4.93H1.25v3.15C3.26 21.36 7.33 24 12 24z" />
                <path fill="#FBBC05" d="M5.28 14.27A7.16 7.16 0 0 1 4.9 12c0-.79.14-1.57.38-2.27V6.58H1.25A11.96 11.96 0 0 0 0 12c0 1.92.45 3.74 1.25 5.42l4.03-3.15z" />
                <path fill="#EA4335" d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C17.95 1.19 15.24 0 12 0 7.33 0 3.26 2.64 1.25 6.58l4.03 3.15c.95-2.83 3.6-4.98 6.72-4.98z" />
              </svg>
              <span>{isGoogleLoading ? "Weiterleitung..." : "Mit Google anmelden"}</span>
            </button>
          </div>
        ) : (
          <div>
            <div className="text-center mb-6">
              <h2 id="auth-modal-title" className="text-xl font-bold tracking-tight text-gray-900 mb-1">
                Neues Konto erstellen
              </h2>
              <p className="text-xs text-gray-500">
                Registriere dich mit deiner E-Mail. Du erhältst anschließend einen Bestätigungslink per E-Mail (Double-Opt-In).
              </p>
            </div>

            {regError && (
              <div className="mb-4 p-3 bg-rose-50 border border-rose-200 rounded-xl text-xs text-rose-700">
                {regError}
              </div>
            )}

            {regSuccess && (
              <div className="mb-4 p-3 bg-emerald-50 border border-emerald-200 rounded-xl text-xs text-emerald-800 leading-relaxed">
                <p className="font-semibold mb-1">✓ Fast geschafft!</p>
                {regSuccess}
              </div>
            )}

            {!regSuccess && (
              <form onSubmit={handleRegister} className="space-y-3 mb-4">
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">
                    Name <span className="text-gray-400 font-normal">(optional)</span>
                  </label>
                  <input
                    type="text"
                    value={regName}
                    onChange={(e) => setRegName(e.target.value)}
                    placeholder="Max Mustermann"
                    className="w-full px-3 py-2 text-sm border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-sky-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">
                    E-Mail-Adresse
                  </label>
                  <input
                    type="email"
                    required
                    value={regEmail}
                    onChange={(e) => setRegEmail(e.target.value)}
                    placeholder="name@beispiel.de"
                    className="w-full px-3 py-2 text-sm border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-sky-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">
                    Passwort <span className="text-gray-400 font-normal">(mind. 8 Zeichen)</span>
                  </label>
                  <input
                    type="password"
                    required
                    minLength={8}
                    value={regPassword}
                    onChange={(e) => setRegPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full px-3 py-2 text-sm border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-sky-500"
                  />
                </div>

                <button
                  type="submit"
                  disabled={isRegPending}
                  className="w-full py-2.5 px-4 bg-sky-600 hover:bg-sky-500 disabled:opacity-50 text-white text-sm font-semibold rounded-xl shadow-sm transition cursor-pointer"
                >
                  {isRegPending ? "Konto wird erstellt..." : "Registrieren (Double-Opt-In)"}
                </button>
              </form>
            )}

            <div className="relative my-4 text-center">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-200" />
              </div>
              <span className="relative bg-white px-3 text-xs text-gray-400">
                oder
              </span>
            </div>

            <button
              type="button"
              onClick={handleGoogleSignIn}
              disabled={isGoogleLoading}
              className="w-full flex items-center justify-center gap-3 px-4 py-2.5 border border-gray-300 rounded-xl bg-white hover:bg-gray-50 cursor-pointer text-gray-700 font-medium text-sm shadow-sm transition disabled:opacity-60"
            >
              <svg className="w-4 h-4 flex-shrink-0" viewBox="0 0 24 24">
                <path fill="#4285F4" d="M23.745 12.27c0-.7-.06-1.4-.19-2.07H12v4.51h6.6c-.29 1.52-1.14 2.82-2.4 3.68v3.05h3.88c2.27-2.09 3.66-5.17 3.66-9.17z" />
                <path fill="#34A853" d="M12 24c3.24 0 5.95-1.08 7.93-2.91l-3.88-3.05c-1.08.72-2.45 1.16-4.05 1.16-3.12 0-5.77-2.1-6.72-4.93H1.25v3.15C3.26 21.36 7.33 24 12 24z" />
                <path fill="#FBBC05" d="M5.28 14.27A7.16 7.16 0 0 1 4.9 12c0-.79.14-1.57.38-2.27V6.58H1.25A11.96 11.96 0 0 0 0 12c0 1.92.45 3.74 1.25 5.42l4.03-3.15z" />
                <path fill="#EA4335" d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C17.95 1.19 15.24 0 12 0 7.33 0 3.26 2.64 1.25 6.58l4.03 3.15c.95-2.83 3.6-4.98 6.72-4.98z" />
              </svg>
              <span>{isGoogleLoading ? "Weiterleitung..." : "Mit Google anmelden"}</span>
            </button>
          </div>
        )}

        <div className="mt-6 pt-3 border-t border-gray-100 text-center">
          <p className="text-[11px] text-gray-500 leading-normal">
            Politiklar ist grundsätzlich ohne Anmeldung frei nutzbar. Mit einem Konto kannst du Favoriten anlegen und den MCP-Server nutzen.
          </p>
        </div>
      </div>
    </div>
  );

  return createPortal(modalContent, document.body);
}
