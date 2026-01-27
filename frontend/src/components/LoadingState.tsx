/**
 * LoadingState - displays loading, empty, and error states.
 */

'use client';

import React from 'react';

interface LoadingStateProps {
    type: 'loading' | 'empty' | 'error';
    message?: string;
}

export default function LoadingState({ type, message }: LoadingStateProps) {
    if (type === 'loading') {
        return (
            <div className="state-container loading">
                <div className="spinner" />
                <p className="state-message">{message || 'Loading events...'}</p>
            </div>
        );
    }

    if (type === 'error') {
        return (
            <div className="state-container error">
                <span className="state-icon">⚠️</span>
                <p className="state-message">{message || 'Something went wrong'}</p>
                <p className="state-hint">Make sure the backend is running on port 5000</p>
            </div>
        );
    }

    if (type === 'empty') {
        return (
            <div className="state-container empty">
                <span className="state-icon">📭</span>
                <p className="state-message">{message || 'No events yet'}</p>
                <p className="state-hint">Push code or create a pull request to see events</p>
            </div>
        );
    }

    return null;
}
