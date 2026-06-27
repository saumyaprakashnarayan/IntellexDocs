"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

export default function Navbar() {
  const pathname = usePathname();
  const router = useRouter();
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  // Run on mount to check if user has a token
  useEffect(() => {
    const token = localStorage.getItem("rag_token");
    setIsLoggedIn(!!token);
  }, [pathname]); // Re-evaluate when the route changes

  const handleLogout = () => {
    localStorage.removeItem("rag_token");
    setIsLoggedIn(false);
    router.push("/login");
  };

  // Don't show the navbar on the landing/login/register pages if desired,
  // or just show a simplified version. For now, we always show it.
  const isAuthPage = pathname === "/login" || pathname === "/register" || pathname === "/";

  return (
    <header className="border-b border-slate-800 bg-slate-950 px-6 py-4">
      <div className="mx-auto flex max-w-6xl items-center justify-between">
        <Link href={isLoggedIn ? "/dashboard" : "/"} className="text-xl font-bold text-slate-100 hover:text-sky-400 transition">
          IntellexDocs
        </Link>

        <nav className="flex items-center gap-6 text-sm font-medium">
          {isLoggedIn ? (
            <>
              <Link
                href="/dashboard"
                className={`transition ${pathname === "/dashboard" ? "text-sky-400" : "text-slate-300 hover:text-slate-100"}`}
              >
                Dashboard
              </Link>
              <Link
                href="/chat"
                className={`transition ${pathname === "/chat" ? "text-sky-400" : "text-slate-300 hover:text-slate-100"}`}
              >
                Chat
              </Link>
              <Link
                href="/upload"
                className={`transition ${pathname === "/upload" ? "text-sky-400" : "text-slate-300 hover:text-slate-100"}`}
              >
                Upload
              </Link>
              <button
                onClick={handleLogout}
                className="rounded-full border border-slate-700 bg-slate-900 px-4 py-2 text-slate-200 transition hover:bg-slate-800 hover:text-white"
              >
                Logout
              </button>
            </>
          ) : (
            !isAuthPage && (
              <>
                <Link href="/login" className="text-slate-300 transition hover:text-slate-100">
                  Log in
                </Link>
                <Link
                  href="/register"
                  className="rounded-full bg-sky-500 px-4 py-2 text-white transition hover:bg-sky-400"
                >
                  Sign up
                </Link>
              </>
            )
          )}
        </nav>
      </div>
    </header>
  );
}
