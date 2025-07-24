/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: ['localhost', 'example.com'],
  },
  env: {
    CUSTOM_KEY: 'my-value',
  },
}

module.exports = nextConfig 