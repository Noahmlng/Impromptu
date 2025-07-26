/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  trailingSlash: true,
  images: {
    unoptimized: true
  },
  assetPrefix: '',
  basePath: '',
  // 静态导出优化
  distDir: 'out',
  // 减少构建时的调试信息
  eslint: {
    ignoreDuringBuilds: false,
  },
  typescript: {
    ignoreBuildErrors: false,
  },
  // 禁用一些不兼容静态导出的功能
  experimental: {
    // 静态导出时禁用这些功能
  }
}

module.exports = nextConfig 