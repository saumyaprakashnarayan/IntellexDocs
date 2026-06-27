/**
 * next.config.mjs
 * ================
 * Next.js build configuration for IntellexDocs.
 *
 * @type {import('next').NextConfig}
 */
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const nextConfig = {
  reactStrictMode: true,

  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "*",
      },
    ],
  },

  // Explicitly re-exporting the variable here ensures it is available both
  // server-side (for SSR routes) and gets inlined into the browser bundle.
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000",
  },


};

export default nextConfig;
