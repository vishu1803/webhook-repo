/**
 * useEvents Hook
 * ==============
 * 
 * Custom React hook for fetching and polling GitHub events.
 * 
 * Features:
 * - Polls backend every 15 seconds
 * - Prevents duplicate events using Set
 * - Tracks loading and error states
 * - Supports manual refresh
 * 
 * Interview Tip:
 *   Custom hooks are a powerful way to extract and reuse stateful logic.
 *   They keep components clean and focused on rendering.
 */

'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { GitHubEvent } from '@/lib/types';
import { fetchEvents } from '@/lib/api';

// Polling interval from environment or default 15 seconds
const POLL_INTERVAL = parseInt(process.env.NEXT_PUBLIC_POLL_INTERVAL || '15000', 10);

interface UseEventsReturn {
    /** Array of events to display */
    events: GitHubEvent[];

    /** Loading state for initial load */
    isLoading: boolean;

    /** Error message if any */
    error: string | null;

    /** Whether polling is active */
    isPolling: boolean;

    /** Last update timestamp */
    lastUpdate: Date | null;

    /** Total events in database */
    totalEvents: number;

    /** Manually trigger a refresh */
    refresh: () => Promise<void>;
}

/**
 * Custom hook for managing GitHub events with polling.
 * 
 * @returns UseEventsReturn object with events data and controls
 * 
 * Usage:
 *   const { events, isLoading, error } = useEvents();
 * 
 * Interview Tip:
 *   Using useRef for the Set prevents unnecessary re-renders.
 *   The Set is used only for duplicate checking, not for display.
 */
export function useEvents(): UseEventsReturn {
    // State for events array (displayed in UI)
    const [events, setEvents] = useState<GitHubEvent[]>([]);

    // Loading state (only for initial load)
    const [isLoading, setIsLoading] = useState(true);

    // Error message
    const [error, setError] = useState<string | null>(null);

    // Polling active indicator
    const [isPolling, setIsPolling] = useState(false);

    // Last update timestamp
    const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

    // Total events in database
    const [totalEvents, setTotalEvents] = useState(0);

    // Track last timestamp for incremental fetching
    const lastTimestampRef = useRef<string | null>(null);

    // Track displayed event IDs to prevent duplicates
    // Using Set for O(1) lookup performance
    const displayedIdsRef = useRef<Set<string>>(new Set());

    // Interval reference for cleanup
    const intervalRef = useRef<NodeJS.Timeout | null>(null);

    /**
     * Fetch events from the API.
     * 
     * @param isInitial - If true, fetch all events; otherwise, fetch incremental
     * 
     * Interview Tip:
     *   Always use useCallback for functions that are dependencies
     *   of useEffect to prevent unnecessary effect re-runs.
     */
    const loadEvents = useCallback(async (isInitial: boolean = false) => {
        try {
            setIsPolling(true);

            // Fetch events from API
            const response = await fetchEvents(
                isInitial ? null : lastTimestampRef.current,
                isInitial
            );

            if (response.status === 'error') {
                setError('Failed to fetch events from server');
                return;
            }

            // Update total events count
            setTotalEvents(response.total_in_db);

            // Filter out duplicates and add new events
            const newEvents = response.events.filter(event => {
                // Check if we've already displayed this event
                if (displayedIdsRef.current.has(event.request_id)) {
                    return false; // Skip duplicate
                }
                // Mark as displayed
                displayedIdsRef.current.add(event.request_id);
                return true;
            });

            if (newEvents.length > 0) {
                // Add new events to the beginning (latest first)
                setEvents(prev => [...newEvents, ...prev]);

                // Update last timestamp for next poll
                if (response.last_timestamp) {
                    lastTimestampRef.current = response.last_timestamp;
                }

                console.log(`✓ Added ${newEvents.length} new event(s)`);
            }

            // Update last update time
            setLastUpdate(new Date());
            setError(null);

        } catch (err) {
            console.error('Error loading events:', err);
            setError('Unable to connect to server');
        } finally {
            setIsLoading(false);
            setIsPolling(false);
        }
    }, []);

    /**
     * Initial load and polling setup.
     * 
     * Interview Tip:
     *   Always cleanup intervals in useEffect return function
     *   to prevent memory leaks.
     */
    useEffect(() => {
        // Initial load - fetch all events
        loadEvents(true);

        // Set up polling interval
        intervalRef.current = setInterval(() => {
            loadEvents(false);
        }, POLL_INTERVAL);

        // Cleanup on unmount
        return () => {
            if (intervalRef.current) {
                clearInterval(intervalRef.current);
            }
        };
    }, [loadEvents]);

    /**
     * Manual refresh function.
     */
    const refresh = useCallback(async () => {
        await loadEvents(false);
    }, [loadEvents]);

    return {
        events,
        isLoading,
        error,
        isPolling,
        lastUpdate,
        totalEvents,
        refresh,
    };
}
