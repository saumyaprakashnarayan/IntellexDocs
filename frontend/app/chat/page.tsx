"use client";

import { useState } from "react";
import ChatWindow from "../../components/ChatWindow";
import CitationPanel from "../../components/CitationPanel";

export default function ChatPage() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSend = async () => {
    setLoading(true);
    setError("");
    const token = localStorage.getItem("rag_token");
    if (!token) {
      setError("Authentication required.");
      setLoading(false);
      return;
    }

    const response = await fetch("http://localhost:8000/chat/query", {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
      body: JSON.stringify({ question }),
    });
    const data = await response.json();
    setLoading(false);
    if (!response.ok) {
      setError(data.detail || "Unable to fetch answer.");
      return;
    }
    setAnswer(data.answer);
    setSources(data.sources || []);
  };

  return (
    <main className="mx-auto max-w-6xl px-6 py-16 text-slate-100">
      <div className="grid gap-8 lg:grid-cols-[1.4fr_0.8fr]">
        <section className="space-y-6 rounded-3xl border border-slate-800 bg-slate-900 p-8">
          <div className="flex items-center justify-between gap-4">
            <div>
              <h1 className="text-3xl font-semibold">Chat with your documents</h1>
              <p className="text-slate-400">Ask questions and receive grounded answers with citations.</p>
            </div>
          </div>
          <div className="space-y-4">
            <textarea className="min-h-[140px] w-full rounded-3xl border border-slate-700 bg-slate-950 px-4 py-4 text-slate-100" value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="Type your question here..." />
            <button className="rounded-full bg-sky-500 px-6 py-3 text-white transition hover:bg-sky-400" onClick={handleSend} disabled={loading}> {loading ? "Thinking..." : "Ask Document"}</button>
            {error && <p className="text-sm text-rose-400">{error}</p>}
          </div>
          <ChatWindow answer={answer} />
        </section>
        <aside className="space-y-6 rounded-3xl border border-slate-800 bg-slate-900 p-6">
          <CitationPanel sources={sources} />
        </aside>
      </div>
    </main>
  );
}
