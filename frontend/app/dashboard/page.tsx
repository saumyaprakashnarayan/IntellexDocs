"use client";

import { useEffect, useState } from "react";

export default function DashboardPage() {
  const [documents, setDocuments] = useState<any[]>([]);

  useEffect(() => {
    const token = localStorage.getItem("rag_token");
    if (!token) return;
    fetch("http://localhost:8000/documents", {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => res.json())
      .then((data) => setDocuments(data ?? []))
      .catch(console.error);
  }, []);

  return (
    <main className="mx-auto max-w-6xl px-6 py-16 text-slate-100">
      <div className="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <h1 className="text-4xl font-semibold">Document Dashboard</h1>
          <p className="mt-2 text-slate-400">Review uploaded PDFs, open the chat interface, and summarize files.</p>
        </div>
        <div className="grid gap-3 sm:grid-cols-2">
          <a className="rounded-full bg-sky-500 px-5 py-3 text-center text-white transition hover:bg-sky-400" href="/upload">Upload</a>
          <a className="rounded-full border border-slate-700 px-5 py-3 text-center text-slate-100 transition hover:border-slate-500" href="/chat">Chat</a>
        </div>
      </div>
      <section className="mt-10 grid gap-4">
        {documents.length === 0 ? (
          <div className="rounded-3xl border border-slate-800 bg-slate-900 p-8 text-slate-400">No uploaded documents found yet.</div>
        ) : (
          documents.map((doc) => (
            <div key={doc.id} className="rounded-3xl border border-slate-800 bg-slate-900 p-6">
              <div className="flex items-center justify-between gap-4">
                <div>
                  <p className="text-lg font-medium text-white">{doc.filename}</p>
                  <p className="text-sm text-slate-400">Uploaded {new Date(doc.upload_date).toLocaleString()}</p>
                </div>
                <a className="rounded-full bg-slate-800 px-4 py-2 text-sm text-slate-200 transition hover:bg-slate-700" href={`/chat`}>Ask questions</a>
              </div>
            </div>
          ))
        )}
      </section>
    </main>
  );
}
