/**
 * TypeScript type definitions for GitHub events.
 */

export type ActionType = 'PUSH' | 'PULL_REQUEST' | 'MERGE';

export interface GitHubEvent {
    request_id: string;
    author: string;
    action: ActionType;
    from_branch: string;
    to_branch: string;
    timestamp: string;
}

export interface EventsApiResponse {
    status: 'success' | 'error';
    events: GitHubEvent[];
    count: number;
    last_timestamp: string | null;
    total_in_db: number;
}
