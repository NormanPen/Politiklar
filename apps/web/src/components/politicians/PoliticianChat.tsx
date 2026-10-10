"use client";

import React, { useState, useRef, useEffect } from "react";

interface Citation {
  source_document_id: string;
  speech_id: string | null;
  locator: string;
  speaker: string;
  similarity_score: number;
}

interface Message {
  id: string;
  sender: "user" | "assistant";
  text: string;
  citations?: Citation[];
  timestamp: string;
}

interface PoliticianChatProps {
  mdbId: number;
  memberName: string;
  memberGroup?: string | null;
}

export default function PoliticianChat({
  mdbId,
  memberName,
  memberGroup,
}: PoliticianChatProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      sender: "assistant",
      text: `Hallo! Ich beantworte deine Fragen zu ${memberName} (${memberGroup || "Deutscher Bundestag"}). Ich greife dabei direkt auf die verifizierten Bundestags-Stammdaten und die parlamentarische RAG-Pipeline zu. Was möchtest du wissen?`,
      timestamp: "Gerade eben",
    },
  ]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [expandedCitationId, setExpandedCitationId] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const quickPrompts = [
    "Hat der Politiker noch weitere Jobs oder Nebentätigkeiten?",
    "In welchen Ausschüssen und Gremien ist er aktiv?",
    "Welche Schwerpunkte vertritt er im Bundestag?",
  ];

  const handleSendMessage = async (questionText: string) => {
    const trimmed = questionText.trim();
    if (!trimmed || isLoading) return;

    setError(null);
    const userMessageId = `user-${Date.now()}`;
    const userMsg: Message = {
      id: userMessageId,
      sender: "user",
      text: trimmed,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputValue("");
    setIsLoading(true);

    try {
      const response = await fetch("/api/politician-chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          mdbId,
          question: trimmed,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || `Fehler ${response.status}`);
      }

      const assistantMsg: Message = {
        id: `assistant-${Date.now()}`,
        sender: "assistant",
        text: data.answer || "Keine Antwort erhalten.",
        citations: data.citations || [],
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      };

      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Unbekannter Fehler beim Abrufen der Antwort.";
      setError(msg);
      setMessages((prev) => [
        ...prev,
        {
          id: `assistant-err-${Date.now()}`,
          sender: "assistant",
          text: `⚠️ Entschuldigung, es gab ein Problem beim Abrufen der Information: ${msg}`,
          timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage(inputValue);
    }
  };

  return (
    <div className="bg-white border border-gray-200 rounded-2xl shadow-sm overflow-hidden flex flex-col">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-900 via-indigo-900 to-slate-900 px-6 py-4 text-white flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-full bg-purple-500/20 border border-purple-400/30 flex items-center justify-center text-lg shadow-inner">
            🤖
          </div>
          <div>
            <h3 className="font-bold text-base tracking-tight leading-snug">
              Fragen zu {memberName} stellen
            </h3>
            <p className="text-xs text-purple-200/80 flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse inline-block"></span>
              Live-Auskunft aus SQL &amp; Vektor-RAG
            </p>
          </div>
        </div>

        {messages.length > 1 && (
          <button
            onClick={() => {
              setMessages([messages[0]]);
              setError(null);
            }}
            className="text-xs text-purple-200/70 hover:text-white px-2.5 py-1 rounded-md hover:bg-white/10 transition"
            title="Chat-Verlauf zurücksetzen"
          >
            Zurücksetzen
          </button>
        )}
      </div>

      {/* Quick Prompts */}
      <div className="bg-purple-50/60 border-b border-purple-100 px-6 py-2.5 flex items-center gap-2 overflow-x-auto text-xs">
        <span className="text-purple-700 font-semibold shrink-0">Vorschläge:</span>
        {quickPrompts.map((prompt, idx) => (
          <button
            key={idx}
            disabled={isLoading}
            onClick={() => handleSendMessage(prompt)}
            className="shrink-0 px-2.5 py-1 bg-white hover:bg-purple-100/80 text-purple-900 border border-purple-200 rounded-full transition disabled:opacity-50 text-left font-medium shadow-xs"
          >
            {prompt}
          </button>
        ))}
      </div>

      {/* Message History */}
      <div className="p-6 space-y-4 max-h-[440px] min-h-[260px] overflow-y-auto bg-gray-50/50">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex flex-col ${
              msg.sender === "user" ? "items-end" : "items-start"
            }`}
          >
            <div
              className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed shadow-xs ${
                msg.sender === "user"
                  ? "bg-purple-700 text-white rounded-br-none"
                  : "bg-white text-gray-800 border border-gray-200/80 rounded-bl-none"
              }`}
            >
              <div className="whitespace-pre-wrap">{msg.text}</div>

              {/* Citations / Belege Badge */}
              {msg.citations && msg.citations.length > 0 && (
                <div className="mt-3 pt-2.5 border-t border-gray-100">
                  <button
                    onClick={() =>
                      setExpandedCitationId((curr) =>
                        curr === msg.id ? null : msg.id
                      )
                    }
                    className="inline-flex items-center gap-1.5 text-xs font-semibold text-indigo-600 hover:text-indigo-800 transition"
                  >
                    <span>📜</span>
                    <span>
                      {msg.citations.length}{" "}
                      {msg.citations.length === 1 ? "Quelle" : "Quellen & Belege"}
                    </span>
                    <span className="text-[10px]">
                      {expandedCitationId === msg.id ? "▲" : "▼"}
                    </span>
                  </button>

                  {expandedCitationId === msg.id && (
                    <div className="mt-2 space-y-1.5 bg-gray-50 p-2.5 rounded-lg border border-gray-200/70 text-xs text-gray-600">
                      {msg.citations.map((c, cIdx) => (
                        <div key={cIdx} className="flex items-start gap-1.5">
                          <span className="text-indigo-500 font-bold shrink-0">
                            [{cIdx + 1}]
                          </span>
                          <div>
                            <span className="font-semibold text-gray-800">
                              {c.locator}
                            </span>
                            {c.speaker && (
                              <span className="text-gray-500">
                                {" "}
                                (Redner: {c.speaker})
                              </span>
                            )}
                            {c.similarity_score < 1.0 && (
                              <span className="ml-1 text-[11px] text-emerald-600 font-mono">
                                Match: {Math.round(c.similarity_score * 100)}%
                              </span>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>

            <span className="text-[10px] text-gray-400 mt-1 px-1">
              {msg.timestamp}
            </span>
          </div>
        ))}

        {isLoading && (
          <div className="flex items-start gap-2">
            <div className="bg-white border border-gray-200 rounded-2xl rounded-bl-none px-4 py-3 shadow-xs flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-purple-600 animate-bounce"></span>
              <span
                className="w-2 h-2 rounded-full bg-purple-600 animate-bounce"
                style={{ animationDelay: "0.2s" }}
              ></span>
              <span
                className="w-2 h-2 rounded-full bg-purple-600 animate-bounce"
                style={{ animationDelay: "0.4s" }}
              ></span>
              <span className="text-xs text-gray-500 ml-2 font-medium">
                Recherchiere Bundestagsdaten...
              </span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {error && (
        <div className="bg-red-50 border-t border-red-200 px-6 py-2 text-xs text-red-700 flex items-center justify-between">
          <span>{error}</span>
          <button
            onClick={() => setError(null)}
            className="font-bold hover:text-red-900 ml-2"
          >
            ✕
          </button>
        </div>
      )}

      {/* Input Form */}
      <div className="p-4 bg-white border-t border-gray-200">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSendMessage(inputValue);
          }}
          className="flex items-center gap-2"
        >
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isLoading}
            placeholder={`Frage zu ${memberName} stellen (z.B. „Hat er weitere Jobs?“…)`}
            className="flex-1 px-4 py-2.5 text-sm bg-gray-50 border border-gray-300 rounded-xl focus:outline-hidden focus:ring-2 focus:ring-purple-500 focus:bg-white transition disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={isLoading || !inputValue.trim()}
            className="px-5 py-2.5 bg-purple-700 hover:bg-purple-800 disabled:bg-gray-300 text-white font-semibold text-sm rounded-xl transition shadow-xs disabled:cursor-not-allowed shrink-0 flex items-center gap-1.5"
          >
            <span>Senden</span>
            <span>➔</span>
          </button>
        </form>
        <p className="text-[11px] text-gray-400 mt-2 text-center">
          Politiklar KI stützt sich auf offizielle Bundestagsquellen (Plenarprotokolle, namentliche Abstimmungen &amp; Stammdaten).
        </p>
      </div>
    </div>
  );
}
