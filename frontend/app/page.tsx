import Link from "next/link";

export default function HomePage() {
  return (
    <main className="mx-auto max-w-5xl px-6 py-20">
      <section className="space-y-6 text-center">
        <p className="text-sm uppercase tracking-[0.3em] text-sky-400">RAG Document Intelligence</p>
        <h1 className="text-5xl font-semibold tracking-tight text-white">Upload, search, and chat with PDFs using Gemini AI.</h1>
        <p className="mx-auto max-w-2xl text-lg text-slate-300">Securely upload academic papers, reports, and business files, then ask questions that are grounded in your documents with source citations.</p>
        <div className="flex flex-col gap-4 sm:flex-row sm:justify-center">
          <Link className="rounded-full bg-sky-500 px-7 py-3 text-white transition hover:bg-sky-400" href="/register">Get Started</Link>
          <Link className="rounded-full border border-slate-700 px-7 py-3 text-slate-100 transition hover:border-slate-500" href="/login">Login</Link>
        </div>
      </section>
    </main>
  );
}
