/**
 * EventsList Component
 * ====================
 * 
 * Main container component that displays all GitHub events.
 * 
 * Features:
 * - Automatic polling every 15 seconds
 * - Loading and empty states
 * - Status bar showing poll status
 * - No duplicate rendering
 * 
 * Interview Tip:
 *   Container components manage state and data fetching.
 *   Presentational components (like EventCard) just render data.
 *   This separation makes your code more maintainable.
 */

'use client';

import React from 'react';
import { useEvents } from '@/hooks/useEvents';
import EventCard from './EventCard';
import LoadingState from './LoadingState';

export default function EventsList() {
    const {
        events,
        isLoading,
        error,
        isPolling,
        lastUpdate,
        totalEvents,
        refresh,
    } = useEvents();

    // Format last update time
    const lastUpdateStr = lastUpdate
        ? lastUpdate.toLocaleTimeString()
        : 'Never';

    return (
        <div className="events-container">
            {/* Header with status */}
            <header className="events-header">
                <h1 className="events-title">
                    🐙 GitHub Events
                </h1>

                <div className="events-stats">
                    <span className="stat">
                        Total: <strong>{totalEvents}</strong>
                    </span>
                    <span className="stat">
                        Displayed: <strong>{events.length}</strong>
                    </span>
                </div>
            </header>

            {/* Status bar */}
            <div className="status-bar">
                <div className="status-left">
                    <span className={`status-dot ${isPolling ? 'polling' : 'idle'}`} />
                    <span className="status-text">
                        {isPolling ? 'Syncing...' : 'Auto-refresh: 15s'}
                    </span>
                </div>

                <div className="status-right">
                    <span className="last-update">
                        Last update: {lastUpdateStr}
                    </span>
                    <button
                        className="refresh-btn"
                        onClick={refresh}
                        disabled={isPolling}
                    >
                        🔄 Refresh
                    </button>
                </div>
            </div>

            {/* Events list */}
            <div className="events-list">
                {/* Loading state */}
                {isLoading && (
                    <LoadingState type="loading" />
                )}

                {/* Error state */}
                {!isLoading && error && (
                    <LoadingState type="error" message={error} />
                )}

                {/* Empty state */}
                {!isLoading && !error && events.length === 0 && (
                    <LoadingState type="empty" />
                )}

                {/* Events */}
                {!isLoading && !error && events.map((event) => (
                    <EventCard key={event.request_id} event={event} />
                ))}
            </div>

            {/* Footer */}
            <footer className="events-footer">
                <p>Polling every 15 seconds • Events are stored in MongoDB</p>
            </footer>
        </div>
    );
}
