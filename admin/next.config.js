/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  output: 'export',
  trailingSlash: true,
  basePath: process.env.NODE_ENV === 'production' ? '/data-pipeline/admin' : '',
  assetPrefix: process.env.NODE_ENV === 'production' ? '/data-pipeline/admin' : '',
  images: {
    unoptimized: true
  }
}

module.exports = nextConfig