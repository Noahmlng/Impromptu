/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: ['localhost', '127.0.0.1', 'example.com'],
  },
  env: {
    NEXT_PUBLIC_API_URL: 'http://127.0.0.1:5003',
  },
}

module.exports = nextConfig 