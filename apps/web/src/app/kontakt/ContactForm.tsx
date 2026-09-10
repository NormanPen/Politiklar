"use client";

import { useActionState, useState } from "react";
import Link from "next/link";
import { submitContactForm, ContactFormState } from "./actions";

const initialState: ContactFormState = {};

export default function ContactForm() {
  const [state, formAction, isPending] = useActionState(submitContactForm, initialState);
  const [resetKey, setResetKey] = useState(0);

  const handleReset = () => {
    setResetKey((prev) => prev + 1);
  };

  if (state.success) {
    return (
      <div className="bg-emerald-50 border border-emerald-200 rounded-2xl p-6 sm:p-8 text-center space-y-4">
        <div className="mx-auto w-12 h-12 rounded-full bg-emerald-100 flex items-center justify-center text-emerald-600 text-xl font-bold">
          ✓
        </div>
        <h3 className="text-xl font-bold text-emerald-900">
          Nachricht gesendet!
        </h3>
        <p className="text-emerald-700 max-w-md mx-auto text-sm sm:text-base">
          {state.message}
        </p>
        <div className="pt-2">
          <button
            type="button"
            onClick={handleReset}
            className="inline-flex items-center justify-center px-5 py-2.5 rounded-xl font-medium text-sm text-emerald-800 bg-emerald-100 hover:bg-emerald-200 transition-colors"
          >
            Weitere Nachricht schreiben
          </button>
        </div>
      </div>
    );
  }

  return (
    <form
      key={resetKey}
      action={formAction}
      noValidate
      className="bg-white border border-gray-200 shadow-sm rounded-2xl p-6 sm:p-8 space-y-6"
    >
      {state.message && !state.success && (
        <div className="p-4 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm">
          {state.message}
        </div>
      )}

      {/* Honeypot für Bot-Schutz – für Menschen unsichtbar */}
      <div className="hidden" aria-hidden="true">
        <label htmlFor="website_hp">Bitte dieses Feld frei lassen</label>
        <input
          type="text"
          id="website_hp"
          name="website_hp"
          tabIndex={-1}
          autoComplete="off"
        />
      </div>

      {/* Name */}
      <div>
        <label
          htmlFor="name"
          className="block text-sm font-semibold text-gray-800 mb-1.5"
        >
          Name <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          id="name"
          name="name"
          required
          placeholder="Ihr vollständiger Name"
          disabled={isPending}
          className={`w-full px-4 py-3 rounded-xl border bg-gray-50/50 text-gray-900 text-sm transition focus:bg-white focus:outline-none focus:ring-2 disabled:opacity-60 ${
            state.errors?.name
              ? "border-red-400 focus:border-red-500 focus:ring-red-200"
              : "border-gray-200 focus:border-cyan-500 focus:ring-cyan-100"
          }`}
        />
        {state.errors?.name && (
          <p className="mt-1.5 text-xs font-medium text-red-600">
            {state.errors.name}
          </p>
        )}
      </div>

      {/* E-Mail */}
      <div>
        <label
          htmlFor="email"
          className="block text-sm font-semibold text-gray-800 mb-1.5"
        >
          E-Mail-Adresse <span className="text-red-500">*</span>
        </label>
        <input
          type="email"
          id="email"
          name="email"
          required
          placeholder="name@beispiel.de"
          disabled={isPending}
          className={`w-full px-4 py-3 rounded-xl border bg-gray-50/50 text-gray-900 text-sm transition focus:bg-white focus:outline-none focus:ring-2 disabled:opacity-60 ${
            state.errors?.email
              ? "border-red-400 focus:border-red-500 focus:ring-red-200"
              : "border-gray-200 focus:border-cyan-500 focus:ring-cyan-100"
          }`}
        />
        {state.errors?.email && (
          <p className="mt-1.5 text-xs font-medium text-red-600">
            {state.errors.email}
          </p>
        )}
      </div>

      {/* Nachricht */}
      <div>
        <label
          htmlFor="message"
          className="block text-sm font-semibold text-gray-800 mb-1.5"
        >
          Nachricht <span className="text-red-500">*</span>
        </label>
        <textarea
          id="message"
          name="message"
          rows={5}
          required
          placeholder="Ihre Frage, Anregung oder Ihr Feedback..."
          disabled={isPending}
          className={`w-full px-4 py-3 rounded-xl border bg-gray-50/50 text-gray-900 text-sm transition focus:bg-white focus:outline-none focus:ring-2 disabled:opacity-60 resize-y min-h-[120px] ${
            state.errors?.message
              ? "border-red-400 focus:border-red-500 focus:ring-red-200"
              : "border-gray-200 focus:border-cyan-500 focus:ring-cyan-100"
          }`}
        />
        {state.errors?.message && (
          <p className="mt-1.5 text-xs font-medium text-red-600">
            {state.errors.message}
          </p>
        )}
      </div>

      {/* Datenschutzhinweis */}
      <p className="text-xs text-gray-500 leading-relaxed">
        Mit dem Absenden erklären Sie sich damit einverstanden, dass Ihre Daten
        zur Beantwortung Ihrer Anfrage verarbeitet werden. Weitere Hinweise
        finden Sie in unserer{" "}
        <Link
          href="/datenschutz"
          className="text-cyan-700 underline underline-offset-2 hover:text-cyan-900"
        >
          Datenschutzerklärung
        </Link>
        .
      </p>

      {/* Absende-Button */}
      <div>
        <button
          type="submit"
          disabled={isPending}
          className="w-full inline-flex items-center justify-center px-6 py-3.5 rounded-xl font-semibold text-sm bg-cta hover:bg-cta-hover text-gray-800 border border-cta-border/30 shadow-sm transition duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-400 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
        >
          {isPending ? (
            <span className="flex items-center gap-2">
              <svg
                className="animate-spin -ml-1 mr-2 h-4 w-4 text-gray-800"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                ></circle>
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
              Wird gesendet...
            </span>
          ) : (
            "Nachricht absenden"
          )}
        </button>
      </div>
    </form>
  );
}
