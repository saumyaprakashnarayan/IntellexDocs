/**
 * next.config.mjs
 * ================
 * Next.js build configuration for IntellexDocs.
 *
 * @type {import('next').NextConfig}
 */
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
  // Without this, a missing .env.local would cause process.env.NEXT_PUBLIC_API_URL
  // to be undefined at runtime instead of falling back to the default.
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000",
  },
};

export default nextConfig;
