/**
 * EventsList - main container for displaying GitHub events with polling.
 */

'use client';

import React from 'react';
import { useEvents } from '@/hooks/useEvents';
import EventCard from './EventCard';
import LoadingState from './LoadingState';

export default function EventsList() {
    const { events, isLoading, error, isPolling, lastUpdate, totalEvents, refresh } = useEvents();

    const lastUpdateStr = lastUpdate ? lastUpdate.toLocaleTimeString() : 'Never';

    return (
        <div className="events-container">
            <header className="events-header">
                <h1 className="events-title">🐙 GitHub Events</h1>
                <div className="events-stats">
                    <span className="stat">Total: <strong>{totalEvents}</strong></span>
                    <span className="stat">Displayed: <strong>{events.length}</strong></span>
                </div>
            </header>

            <div className="status-bar">
                <div className="status-left">
                    <span className={`status-dot ${isPolling ? 'polling' : 'idle'}`} />
                    <span className="status-text">{isPolling ? 'Syncing...' : 'Auto-refresh: 15s'}</span>
                </div>
                <div className="status-right">
                    <span className="last-update">Last update: {lastUpdateStr}</span>
                    <button className="refresh-btn" onClick={refresh} disabled={isPolling}>🔄 Refresh</button>
                </div>
            </div>

            <div className="events-list">
                {isLoading && <LoadingState type="loading" />}
                {!isLoading && error && <LoadingState type="error" message={error} />}
                {!isLoading && !error && events.length === 0 && <LoadingState type="empty" />}
                {!isLoading && !error && events.map((event) => (
                    <EventCard key={event.request_id} event={event} />
                ))}
            </div>

            <footer className="events-footer">
                <p>Polling every 15 seconds • Events stored in MongoDB</p>
            </footer>
        </div>
    );
}
