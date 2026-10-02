import type { NextConfig } from "next";

// Vercel builds must never silently ship a localhost or insecure API URL.
if (process.env.VERCEL === "1") {
  const value = process.env.NEXT_PUBLIC_API_URL;
  if (!value) throw new Error("Set NEXT_PUBLIC_API_URL in the Vercel environment before building.");
  const url = new URL(value);
  if (url.protocol !== "https:" || url.username || url.password || url.search || url.hash
      || (url.pathname !== "/" && url.pathname !== "")
      || ["localhost", "127.0.0.1", "[::1]"].includes(url.hostname)) {
    throw new Error("Vercel NEXT_PUBLIC_API_URL must be a public HTTPS origin without credentials or a path.");
  }
}

const nextConfig: NextConfig = {
  /* config options here */
};

export default nextConfig;
