/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Only use static export for production builds, allow API routes in dev
  ...(process.env.NODE_ENV === 'production' ? { output: 'export' } : {}),
  trailingSlash: true,
  basePath: process.env.NODE_ENV === 'production' ? '/data-pipeline/admin' : '',
  assetPrefix: process.env.NODE_ENV === 'production' ? '/data-pipeline/admin' : '',
  images: {
    unoptimized: true
  }
}

module.exports = nextConfig