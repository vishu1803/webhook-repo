/**
 * Custom hook for fetching and polling GitHub events.
 */

'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { GitHubEvent } from '@/lib/types';
import { fetchEvents } from '@/lib/api';

const POLL_INTERVAL = parseInt(process.env.NEXT_PUBLIC_POLL_INTERVAL || '15000', 10);

interface UseEventsReturn {
    events: GitHubEvent[];
    isLoading: boolean;
    error: string | null;
    isPolling: boolean;
    lastUpdate: Date | null;
    totalEvents: number;
    refresh: () => Promise<void>;
}

export function useEvents(): UseEventsReturn {
    const [events, setEvents] = useState<GitHubEvent[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [isPolling, setIsPolling] = useState(false);
    const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
    const [totalEvents, setTotalEvents] = useState(0);

    const lastTimestampRef = useRef<string | null>(null);
    const displayedIdsRef = useRef<Set<string>>(new Set());
    const intervalRef = useRef<NodeJS.Timeout | null>(null);

    const loadEvents = useCallback(async (isInitial: boolean = false) => {
        try {
            setIsPolling(true);

            const response = await fetchEvents(
                isInitial ? null : lastTimestampRef.current,
                isInitial
            );

            if (response.status === 'error') {
                setError('Failed to fetch events');
                return;
            }

            setTotalEvents(response.total_in_db);

            // Filter duplicates
            const newEvents = response.events.filter(event => {
                if (displayedIdsRef.current.has(event.request_id)) return false;
                displayedIdsRef.current.add(event.request_id);
                return true;
            });

            if (newEvents.length > 0) {
                setEvents(prev => [...newEvents, ...prev]);
                if (response.last_timestamp) {
                    lastTimestampRef.current = response.last_timestamp;
                }
            }

            setLastUpdate(new Date());
            setError(null);
        } catch {
            setError('Unable to connect to server');
        } finally {
            setIsLoading(false);
            setIsPolling(false);
        }
    }, []);

    useEffect(() => {
        loadEvents(true);
        intervalRef.current = setInterval(() => loadEvents(false), POLL_INTERVAL);
        return () => { if (intervalRef.current) clearInterval(intervalRef.current); };
    }, [loadEvents]);

    const refresh = useCallback(async () => { await loadEvents(false); }, [loadEvents]);

    return { events, isLoading, error, isPolling, lastUpdate, totalEvents, refresh };
}
