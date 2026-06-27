"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function RegisterPage() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError("");

    const response = await fetch("http://localhost:8000/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, email, password }),
    });

    const data = await response.json();
    if (!response.ok) {
      setError(data.detail || "Unable to register.");
      return;
    }
    router.push("/login");
  };

  return (
    <main className="mx-auto max-w-xl px-6 py-20 text-slate-100">
      <h1 className="text-3xl font-semibold">Register</h1>
      <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
        <label className="grid gap-2">
          <span>Name</span>
          <input className="rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-slate-200" type="text" value={name} onChange={(event) => setName(event.target.value)} required />
        </label>
        <label className="grid gap-2">
          <span>Email</span>
          <input className="rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-slate-200" type="email" value={email} onChange={(event) => setEmail(event.target.value)} required />
        </label>
        <label className="grid gap-2">
          <span>Password</span>
          <input className="rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-slate-200" type="password" value={password} onChange={(event) => setPassword(event.target.value)} required />
        </label>
        {error && <p className="text-sm text-rose-400">{error}</p>}
        <button type="submit" className="w-full rounded-full bg-sky-500 px-4 py-3 text-white transition hover:bg-sky-400">Create account</button>
      </form>
      <p className="mt-6 text-slate-400">Already have an account? <a className="text-sky-400" href="/login">Login</a></p>
    </main>
  );
}
