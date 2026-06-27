"use client";

/**
 * app/chat/page.tsx
 * ------------------
 * The main Q&A interface — users type a question, hit submit,
 * and receive a Gemini-powered answer grounded in their documents,
 * with source citations shown in the sidebar.
 *
 * Uses apiFetch() so the backend URL comes from NEXT_PUBLIC_API_URL.
 */

import { useState } from "react";
import { apiFetch } from "@/lib/api";
import ChatWindow from "../../components/ChatWindow";
import CitationPanel from "../../components/CitationPanel";

interface Source {
  document:   string;
  page:       number;
  chunk_id:   number;
  similarity: number;
}

export default function ChatPage() {
  const [question, setQuestion] = useState("");
  const [answer,   setAnswer]   = useState("");
  const [sources,  setSources]  = useState<Source[]>([]);
  const [loading,  setLoading]  = useState(false);
  const [error,    setError]    = useState("");

  const handleSend = async () => {
    if (!question.trim()) return;
    setLoading(true);
    setError("");

    const response = await apiFetch("/chat/query", {
      method: "POST",
      body: JSON.stringify({ question }),
    });

    const data = await response.json();
    setLoading(false);

    if (!response.ok) {
      // Show a helpful message if the user isn't authenticated
      if (response.status === 401) {
        setError("You must be logged in to ask questions.");
      } else {
        setError(data.detail || "Unable to fetch an answer. Please try again.");
      }
      return;
    }

    setAnswer(data.answer);
    setSources(data.sources ?? []);
  };

  /** Allow Ctrl+Enter / Cmd+Enter to submit the question */
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
      handleSend();
    }
  };

  return (
    <main className="mx-auto max-w-6xl px-6 py-16 text-slate-100">
      <div className="grid gap-8 lg:grid-cols-[1.4fr_0.8fr]">

        {/* ---- Left column: question input + answer ---- */}
        <section className="space-y-6 rounded-3xl border border-slate-800 bg-slate-900 p-8">
          <div>
            <h1 className="text-3xl font-semibold">Chat with your documents</h1>
            <p className="mt-1 text-slate-400">
              Ask questions and receive grounded answers with source citations.
              Press Ctrl+Enter to submit.
            </p>
          </div>

          <div className="space-y-4">
            <textarea
              className="min-h-[140px] w-full rounded-3xl border border-slate-700 bg-slate-950 px-4 py-4 text-slate-100 focus:outline-none focus:ring-2 focus:ring-sky-500"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Type your question here…"
            />
            <button
              className="rounded-full bg-sky-500 px-6 py-3 text-white transition hover:bg-sky-400 disabled:opacity-50"
              onClick={handleSend}
              disabled={loading || !question.trim()}
            >
              {loading ? "Thinking…" : "Ask Document"}
            </button>
            {error && <p className="text-sm text-rose-400">{error}</p>}
          </div>

          <ChatWindow answer={answer} />
        </section>

        {/* ---- Right column: citations ---- */}
        <aside className="space-y-6 rounded-3xl border border-slate-800 bg-slate-900 p-6">
          <CitationPanel sources={sources} />
        </aside>

      </div>
    </main>
  );
}
