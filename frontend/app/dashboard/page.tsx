"use client";

/**
 * app/dashboard/page.tsx
 * -----------------------
 * Dashboard — shows all documents the user has uploaded.
 * Provides links to upload new documents and open the chat.
 *
 * Uses apiFetch() so the backend URL comes from NEXT_PUBLIC_API_URL.
 */

import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";

interface Document {
  id: number;
  filename: string;
  upload_date: string;
}

export default function DashboardPage() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [error,     setError]     = useState("");

  useEffect(() => {
    // Fetch the user's document list when the page mounts.
    // apiFetch automatically attaches the stored JWT token.
    apiFetch("/documents/")
      .then((res) => {
        if (!res.ok) throw new Error("Failed to load documents.");
        return res.json();
      })
      .then((data: Document[]) => setDocuments(data ?? []))
      .catch((err: Error) => setError(err.message));
  }, []);

  return (
    <main className="mx-auto max-w-6xl px-6 py-16 text-slate-100">
      <div className="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <h1 className="text-4xl font-semibold">Document Dashboard</h1>
          <p className="mt-2 text-slate-400">
            Review uploaded PDFs, open the chat interface, and summarise files.
          </p>
        </div>
        <div className="grid gap-3 sm:grid-cols-2">
          <a
            className="rounded-full bg-sky-500 px-5 py-3 text-center text-white transition hover:bg-sky-400"
            href="/upload"
          >
            Upload
          </a>
          <a
            className="rounded-full border border-slate-700 px-5 py-3 text-center text-slate-100 transition hover:border-slate-500"
            href="/chat"
          >
            Chat
          </a>
        </div>
      </div>

      {error && (
        <p className="mt-6 text-sm text-rose-400">{error}</p>
      )}

      <section className="mt-10 grid gap-4">
        {documents.length === 0 && !error ? (
          <div className="rounded-3xl border border-slate-800 bg-slate-900 p-8 text-slate-400">
            No uploaded documents yet.{" "}
            <a className="text-sky-400 underline" href="/upload">Upload your first PDF →</a>
          </div>
        ) : (
          documents.map((doc) => (
            <div key={doc.id} className="rounded-3xl border border-slate-800 bg-slate-900 p-6">
              <div className="flex items-center justify-between gap-4">
                <div>
                  <p className="text-lg font-medium text-white">{doc.filename}</p>
                  <p className="text-sm text-slate-400">
                    Uploaded {new Date(doc.upload_date).toLocaleString()}
                  </p>
                </div>
                <a
                  className="rounded-full bg-slate-800 px-4 py-2 text-sm text-slate-200 transition hover:bg-slate-700"
                  href="/chat"
                >
                  Ask questions
                </a>
              </div>
            </div>
          ))
        )}
      </section>
    </main>
  );
}
