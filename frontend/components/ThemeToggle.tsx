"use client";

import { useState } from "react";

export default function ThemeToggle() {
  const [mode, setMode] = useState("dark");

  const toggleTheme = () => {
    const next = mode === "dark" ? "light" : "dark";
    setMode(next);
    document.documentElement.dataset.theme = next;
  };

  return (
    <button onClick={toggleTheme} className="rounded-full border border-slate-700 bg-slate-900 px-4 py-2 text-slate-200 transition hover:border-slate-500">
      {mode === "dark" ? "Light mode" : "Dark mode"}
    </button>
  );
}
