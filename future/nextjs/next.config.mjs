/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        // When the browser requests /api/...,
        source: '/api/:path*',
        // Next.js will proxy it to the FastAPI container internally!
        destination: `${process.env.API_URL || 'http://127.0.0.1:8000/api'}/:path*`, 
      },
    ];
  },
};

export default nextConfig;