/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        // When the browser requests /api/...,
        source: '/api/:path*',
        // Next.js will proxy it to the FastAPI container internally!
        destination: `${process.env.API_URL}/:path*`, 
      },
    ];
  },
};

export default nextConfig;