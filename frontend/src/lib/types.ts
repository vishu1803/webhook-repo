/**
 * TypeScript Type Definitions
 * ===========================
 * 
 * This file contains all TypeScript interfaces used in the application.
 * 
 * Interview Tip:
 *   Always define proper TypeScript interfaces for API responses.
 *   This catches type errors at compile time, not runtime.
 */

/**
 * Event action types enum.
 * Matches the backend ActionType enum.
 */
export type ActionType = 'PUSH' | 'PULL_REQUEST' | 'MERGE';

/**
 * GitHub event interface.
 * This matches the schema from the backend API response.
 */
export interface GitHubEvent {
    /** Unique identifier (commit hash or PR ID) */
    request_id: string;

    /** GitHub username who triggered the event */
    author: string;

    /** Type of action: PUSH, PULL_REQUEST, or MERGE */
    action: ActionType;

    /** Source branch name */
    from_branch: string;

    /** Target branch name */
    to_branch: string;

    /** ISO 8601 UTC timestamp */
    timestamp: string;
}

/**
 * API response for events endpoint.
 */
export interface EventsApiResponse {
    /** Status of the request */
    status: 'success' | 'error';

    /** Array of events */
    events: GitHubEvent[];

    /** Number of events returned */
    count: number;

    /** Timestamp of the most recent event (for next poll) */
    last_timestamp: string | null;

    /** Total events in database */
    total_in_db: number;
}

/**
 * Error response from API.
 */
export interface ApiError {
    status: 'error';
    message: string;
}
