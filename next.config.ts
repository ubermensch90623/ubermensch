import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  transpilePackages: ["@excalidraw/excalidraw"],
  serverExternalPackages: ["better-sqlite3"],
};

export default nextConfig;
