"use client";

/**
 * app/register/page.tsx
 * ----------------------
 * Registration page — collects name, email and password,
 * creates the account, then redirects to login.
 *
 * Uses apiFetch() so the backend URL comes from NEXT_PUBLIC_API_URL.
 */

import { useState } from "react";
import { useRouter } from "next/navigation";
import { apiFetch } from "@/lib/api";

export default function RegisterPage() {
  const router = useRouter();
  const [name,     setName]     = useState("");
  const [email,    setEmail]    = useState("");
  const [password, setPassword] = useState("");
  const [error,    setError]    = useState("");
  const [loading,  setLoading]  = useState(false);

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError("");
    setLoading(true);

    const response = await apiFetch("/auth/register", {
      method: "POST",
      body: JSON.stringify({ name, email, password }),
    });

    const data = await response.json();
    setLoading(false);

    if (!response.ok) {
      setError(data.detail || "Unable to register.");
      return;
    }

    // Redirect to login after successful registration
    router.push("/login");
  };

  return (
    <main className="mx-auto max-w-xl px-6 py-20 text-slate-100">
      <h1 className="text-3xl font-semibold">Register</h1>
      <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
        <label className="grid gap-2">
          <span>Name</span>
          <input
            className="rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-slate-200"
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
        </label>
        <label className="grid gap-2">
          <span>Email</span>
          <input
            className="rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-slate-200"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </label>
        <label className="grid gap-2">
          <span>Password</span>
          <input
            className="rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-slate-200"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </label>
        {error && <p className="text-sm text-rose-400">{error}</p>}
        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-full bg-sky-500 px-4 py-3 text-white transition hover:bg-sky-400 disabled:opacity-50"
        >
          {loading ? "Creating account…" : "Create account"}
        </button>
      </form>
      <p className="mt-6 text-slate-400">
        Already have an account?{" "}
        <a className="text-sky-400" href="/login">Login</a>
      </p>
    </main>
  );
}
