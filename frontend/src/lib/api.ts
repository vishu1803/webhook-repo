/**
 * API client for communicating with Flask backend.
 */

import { EventsApiResponse, GitHubEvent } from './types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

export async function fetchEvents(
    since?: string | null,
    fetchAll: boolean = false
): Promise<EventsApiResponse> {
    try {
        const params = new URLSearchParams();
        if (fetchAll) params.append('all', 'true');
        else if (since) params.append('since', since);

        const url = `${API_URL}/events${params.toString() ? '?' + params.toString() : ''}`;
        const response = await fetch(url, {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' },
        });

        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return await response.json();
    } catch (error) {
        console.error('Error fetching events:', error);
        return { status: 'error', events: [], count: 0, last_timestamp: null, total_in_db: 0 };
    }
}

export async function checkApiHealth(): Promise<boolean> {
    try {
        const response = await fetch(`${API_URL}/health`);
        return response.ok;
    } catch {
        return false;
    }
}

/**
 * Format event message for display.
 */
export function formatEventMessage(event: GitHubEvent): string {
    const time = formatTimestamp(event.timestamp);

    switch (event.action) {
        case 'PUSH':
            return `${event.author} pushed to ${event.to_branch} on ${time}`;
        case 'PULL_REQUEST':
            return `${event.author} submitted a pull request from ${event.from_branch} to ${event.to_branch} on ${time}`;
        case 'MERGE':
            return `${event.author} merged branch ${event.from_branch} to ${event.to_branch} on ${time}`;
        default:
            return `${event.author} performed ${event.action} on ${time}`;
    }
}

export function formatTimestamp(isoTimestamp: string): string {
    try {
        return new Date(isoTimestamp).toLocaleString('en-US', {
            month: 'short', day: 'numeric', year: 'numeric',
            hour: 'numeric', minute: '2-digit', hour12: true,
            timeZone: 'UTC', timeZoneName: 'short',
        });
    } catch {
        return isoTimestamp;
    }
}
