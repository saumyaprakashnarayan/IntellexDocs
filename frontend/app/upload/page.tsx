"use client";

/**
 * app/upload/page.tsx
 * --------------------
 * PDF upload page — accepts a file via a form, posts it to the backend,
 * and shows success/error feedback.
 *
 * Uses apiFetch() so the backend URL comes from NEXT_PUBLIC_API_URL.
 * Note: apiFetch() does NOT set Content-Type for FormData payloads —
 * the browser sets the correct multipart/form-data boundary automatically.
 */

import { useState } from "react";
import { apiFetch } from "@/lib/api";

export default function UploadPage() {
  const [file,    setFile]    = useState<File | null>(null);
  const [message, setMessage] = useState("");
  const [error,   setError]   = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setMessage("");
    setError("");

    if (!file) {
      setError("Please select a PDF file first.");
      return;
    }

    setLoading(true);

    // Build the multipart form payload — DO NOT set Content-Type manually
    const formData = new FormData();
    formData.append("file", file);

    const response = await apiFetch("/documents/upload", {
      method: "POST",
      body: formData,
    });

    const data = await response.json();
    setLoading(false);

    if (!response.ok) {
      setError(data.detail || "Upload failed. Please try again.");
      return;
    }

    setMessage("Upload successful! Your document is now searchable.");
    setFile(null);
    // Reset the file input by re-rendering (clearing controlled value)
    (event.target as HTMLFormElement).reset();
  };

  return (
    <main className="mx-auto max-w-3xl px-6 py-16 text-slate-100">
      <h1 className="text-4xl font-semibold">Upload PDF</h1>
      <p className="mt-2 text-slate-400">
        Add documents to your library, then query them with natural language in the Chat.
      </p>
      <form
        className="mt-10 space-y-6 rounded-3xl border border-slate-800 bg-slate-900 p-8"
        onSubmit={handleSubmit}
      >
        <div className="grid gap-2">
          <label className="text-sm font-medium text-slate-300" htmlFor="pdf-file">
            PDF File
          </label>
          <input
            id="pdf-file"
            className="w-full rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-slate-100"
            type="file"
            accept="application/pdf"
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          />
        </div>
        {error   && <p className="text-sm text-rose-400">{error}</p>}
        {message && <p className="text-sm text-emerald-400">{message}</p>}
        <button
          className="w-full rounded-full bg-sky-500 px-5 py-3 text-white transition hover:bg-sky-400 disabled:opacity-50"
          type="submit"
          disabled={loading}
        >
          {loading ? "Uploading…" : "Upload Document"}
        </button>
      </form>
    </main>
  );
}
