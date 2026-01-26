/**
 * Root Layout
 * ===========
 * 
 * This is the root layout component for the Next.js App Router.
 * It wraps all pages and provides common structure.
 * 
 * Interview Tip:
 *   In Next.js 13+, the App Router uses layouts to share UI
 *   between pages. This is more efficient than re-rendering
 *   everything on each navigation.
 */

import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
    title: 'GitHub Events Dashboard',
    description: 'Real-time GitHub webhook event viewer - Polling every 15 seconds',
    keywords: ['github', 'webhook', 'events', 'dashboard'],
};

export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <html lang="en">
            <head>
                {/* Google Fonts - Inter for clean modern look */}
                <link rel="preconnect" href="https://fonts.googleapis.com" />
                <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
                <link
                    href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
                    rel="stylesheet"
                />
            </head>
            <body>
                {children}
            </body>
        </html>
    );
}
