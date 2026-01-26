/**
 * API Client
 * ==========
 * 
 * Centralized API client for communicating with the Flask backend.
 * 
 * Why use a dedicated API client?
 * - Single source of truth for API URL
 * - Consistent error handling
 * - Easy to add authentication headers later
 * 
 * Interview Tip:
 *   Always centralize API calls in a dedicated module.
 *   This makes it easier to modify API logic (like adding auth)
 *   without changing every component.
 */

import { EventsApiResponse, GitHubEvent } from './types';

// API base URL from environment variable
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

/**
 * Fetch events from the backend API.
 * 
 * @param since - Optional ISO timestamp to fetch events after
 * @param fetchAll - If true, fetch all events (for initial load)
 * @returns Promise<EventsApiResponse>
 * 
 * Interview Tip:
 *   Always handle network errors gracefully.
 *   The frontend should never crash due to API issues.
 */
export async function fetchEvents(
    since?: string | null,
    fetchAll: boolean = false
): Promise<EventsApiResponse> {
    try {
        // Build query string
        const params = new URLSearchParams();

        if (fetchAll) {
            params.append('all', 'true');
        } else if (since) {
            params.append('since', since);
        }

        // Make the API request
        const url = `${API_URL}/events${params.toString() ? '?' + params.toString() : ''}`;

        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data: EventsApiResponse = await response.json();
        return data;

    } catch (error) {
        console.error('Error fetching events:', error);

        // Return empty response on error
        return {
            status: 'error',
            events: [],
            count: 0,
            last_timestamp: null,
            total_in_db: 0,
        };
    }
}

/**
 * Check if the backend API is healthy.
 * 
 * @returns Promise<boolean> - True if backend is reachable
 */
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
 * 
 * Formats events according to the requirements:
 * - PUSH: "{author} pushed to {to_branch} on {timestamp}"
 * - PULL_REQUEST: "{author} submitted a pull request from {from_branch} to {to_branch} on {timestamp}"
 * - MERGE: "{author} merged branch {from_branch} to {to_branch} on {timestamp}"
 * 
 * @param event - GitHub event object
 * @returns Formatted message string
 * 
 * Interview Tip:
 *   Keep formatting logic in utility functions, not in components.
 *   This makes the code more testable and reusable.
 */
export function formatEventMessage(event: GitHubEvent): string {
    const formattedTime = formatTimestamp(event.timestamp);

    switch (event.action) {
        case 'PUSH':
            return `${event.author} pushed to ${event.to_branch} on ${formattedTime}`;

        case 'PULL_REQUEST':
            return `${event.author} submitted a pull request from ${event.from_branch} to ${event.to_branch} on ${formattedTime}`;

        case 'MERGE':
            return `${event.author} merged branch ${event.from_branch} to ${event.to_branch} on ${formattedTime}`;

        default:
            return `${event.author} performed ${event.action} on ${formattedTime}`;
    }
}

/**
 * Format timestamp for display.
 * 
 * @param isoTimestamp - ISO 8601 timestamp string
 * @returns Formatted date string
 */
export function formatTimestamp(isoTimestamp: string): string {
    try {
        const date = new Date(isoTimestamp);

        // Format: "Jan 26, 2024 at 3:30 PM UTC"
        return date.toLocaleString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric',
            hour: 'numeric',
            minute: '2-digit',
            hour12: true,
            timeZone: 'UTC',
            timeZoneName: 'short',
        });
    } catch {
        return isoTimestamp;
    }
}
