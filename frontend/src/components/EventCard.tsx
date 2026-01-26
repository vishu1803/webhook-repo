/**
 * EventCard Component
 * ===================
 * 
 * Displays a single GitHub event with proper formatting.
 * 
 * Display Formats (as per requirements):
 * - PUSH: "{author} pushed to {to_branch} on {timestamp}"
 * - PULL_REQUEST: "{author} submitted a pull request from {from_branch} to {to_branch} on {timestamp}"
 * - MERGE: "{author} merged branch {from_branch} to {to_branch} on {timestamp}"
 * 
 * Interview Tip:
 *   Keep components small and focused on a single responsibility.
 *   This component only handles displaying a single event.
 */

'use client';

import React from 'react';
import { GitHubEvent } from '@/lib/types';
import { formatEventMessage, formatTimestamp } from '@/lib/api';

interface EventCardProps {
    event: GitHubEvent;
}

/**
 * Get the appropriate icon for each action type.
 */
function getActionIcon(action: string): string {
    switch (action) {
        case 'PUSH':
            return '⬆️'; // Push up arrow
        case 'PULL_REQUEST':
            return '🔀'; // Merge arrows (for PR)
        case 'MERGE':
            return '✅'; // Check mark (merged)
        default:
            return '📌'; // Default pin
    }
}

/**
 * Get the CSS class for action type styling.
 */
function getActionClass(action: string): string {
    switch (action) {
        case 'PUSH':
            return 'event-push';
        case 'PULL_REQUEST':
            return 'event-pr';
        case 'MERGE':
            return 'event-merge';
        default:
            return '';
    }
}

/**
 * EventCard component.
 * 
 * Renders a single event in a card format with:
 * - Action icon
 * - Formatted message
 * - Action type badge
 * 
 * @param props - Component props with event data
 */
export default function EventCard({ event }: EventCardProps) {
    const icon = getActionIcon(event.action);
    const actionClass = getActionClass(event.action);
    const message = formatEventMessage(event);

    return (
        <div className={`event-card ${actionClass}`}>
            <div className="event-icon">
                {icon}
            </div>

            <div className="event-content">
                <p className="event-message">
                    {message}
                </p>

                <div className="event-meta">
                    <span className={`event-badge ${actionClass}`}>
                        {event.action}
                    </span>
                    <span className="event-branches">
                        {event.from_branch !== event.to_branch
                            ? `${event.from_branch} → ${event.to_branch}`
                            : event.to_branch
                        }
                    </span>
                </div>
            </div>
        </div>
    );
}
