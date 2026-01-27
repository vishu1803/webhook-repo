/**
 * EventCard - displays a single GitHub event.
 */

'use client';

import React from 'react';
import { GitHubEvent } from '@/lib/types';
import { formatEventMessage } from '@/lib/api';

interface EventCardProps {
    event: GitHubEvent;
}

function getActionIcon(action: string): string {
    switch (action) {
        case 'PUSH': return '⬆️';
        case 'PULL_REQUEST': return '🔀';
        case 'MERGE': return '✅';
        default: return '📌';
    }
}

function getActionClass(action: string): string {
    switch (action) {
        case 'PUSH': return 'event-push';
        case 'PULL_REQUEST': return 'event-pr';
        case 'MERGE': return 'event-merge';
        default: return '';
    }
}

export default function EventCard({ event }: EventCardProps) {
    const icon = getActionIcon(event.action);
    const actionClass = getActionClass(event.action);
    const message = formatEventMessage(event);

    return (
        <div className={`event-card ${actionClass}`}>
            <div className="event-icon">{icon}</div>
            <div className="event-content">
                <p className="event-message">{message}</p>
                <div className="event-meta">
                    <span className={`event-badge ${actionClass}`}>{event.action}</span>
                    <span className="event-branches">
                        {event.from_branch !== event.to_branch
                            ? `${event.from_branch} → ${event.to_branch}`
                            : event.to_branch}
                    </span>
                </div>
            </div>
        </div>
    );
}
