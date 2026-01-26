/** @type {import('next').NextConfig} */
const nextConfig = {
    // Enable React strict mode for better development experience
    reactStrictMode: true,

    // Disable image optimization for simpler setup
    images: {
        unoptimized: true,
    }
};

module.exports = nextConfig;
