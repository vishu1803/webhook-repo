/**
 * Home Page
 * =========
 * 
 * Main entry point for the GitHub Events Dashboard.
 * This page displays the EventsList component with polling.
 * 
 * Interview Tip:
 *   Keep page components simple and focused on layout.
 *   Business logic should be in hooks or services.
 */

import EventsList from '@/components/EventsList';

export default function Home() {
    return (
        <main className="main">
            <EventsList />
        </main>
    );
}
