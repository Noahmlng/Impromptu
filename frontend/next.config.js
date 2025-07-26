/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  trailingSlash: true,
  images: {
    unoptimized: true
  },
  assetPrefix: '',
  basePath: '',
  // 禁用一些不兼容静态导出的功能
  experimental: {
    // 静态导出时禁用这些功能
  }
}

module.exports = nextConfig 