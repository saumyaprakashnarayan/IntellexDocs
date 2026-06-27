"use client";

import { useState } from "react";

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!file) {
      setError("Select a PDF file first.");
      return;
    }

    const token = localStorage.getItem("rag_token");
    if (!token) {
      setError("Authentication required.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch("http://localhost:8000/documents/upload", {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
      body: formData,
    });

    const data = await response.json();
    if (!response.ok) {
      setError(data.detail || "Upload failed.");
      return;
    }
    setMessage("Upload succeeded. Your document is now searchable.");
    setFile(null);
    setError("");
  };

  return (
    <main className="mx-auto max-w-3xl px-6 py-16 text-slate-100">
      <h1 className="text-4xl font-semibold">Upload PDF</h1>
      <p className="mt-2 text-slate-400">Add one or more documents and start querying them with natural language.</p>
      <form className="mt-10 space-y-6 rounded-3xl border border-slate-800 bg-slate-900 p-8" onSubmit={handleSubmit}>
        <label className="block text-sm font-medium text-slate-300">PDF File</label>
        <input className="w-full rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-slate-100" type="file" accept="application/pdf" onChange={(event) => setFile(event.target.files?.[0] ?? null)} />
        {error && <p className="text-sm text-rose-400">{error}</p>}
        {message && <p className="text-sm text-emerald-400">{message}</p>}
        <button className="w-full rounded-full bg-sky-500 px-5 py-3 text-white transition hover:bg-sky-400" type="submit">Upload Document</button>
      </form>
    </main>
  );
}
