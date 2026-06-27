"use client";

/**
 * app/login/page.tsx
 * -------------------
 * Login page — accepts email + password, exchanges for a JWT token,
 * stores it in localStorage, then redirects to the dashboard.
 *
 * The backend URL is read from the NEXT_PUBLIC_API_URL environment variable
 * via the central apiFetch() helper — no hardcoded URLs here.
 */

import { useState } from "react";
import { useRouter } from "next/navigation";
import { apiFetch } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [email,    setEmail]    = useState("");
  const [password, setPassword] = useState("");
  const [error,    setError]    = useState("");
  const [loading,  setLoading]  = useState(false);

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError("");
    setLoading(true);

    const response = await apiFetch("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });

    const data = await response.json();
    setLoading(false);

    if (!response.ok) {
      setError(data.detail || "Failed to log in.");
      return;
    }

    // Store the JWT token so all subsequent API calls can attach it
    localStorage.setItem("rag_token", data.access_token);
    router.push("/dashboard");
  };

  return (
    <main className="mx-auto max-w-xl px-6 py-20 text-slate-100">
      <h1 className="text-3xl font-semibold">Login</h1>
      <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
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
          {loading ? "Signing in…" : "Sign in"}
        </button>
      </form>
      <p className="mt-6 text-slate-400">
        Don&apos;t have an account?{" "}
        <a className="text-sky-400" href="/register">Register</a>
      </p>
    </main>
  );
}
