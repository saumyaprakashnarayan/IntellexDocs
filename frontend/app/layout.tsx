import "../styles/globals.css";
import type { Metadata } from "next";
import type { ReactNode } from "react";

export const metadata: Metadata = {
  title: "RAG AI Document Assistant",
  description: "Upload PDFs and chat with your documents.",
};

import Navbar from "../components/Navbar";

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body className="flex min-h-screen flex-col bg-slate-950 text-slate-100">
        <Navbar />
        <div className="flex-1">{children}</div>
      </body>
    </html>
  );
}
