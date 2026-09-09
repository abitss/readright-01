import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  transpilePackages: ["@readright/design-system", "@readright/task-schema"],
};

export default nextConfig;
