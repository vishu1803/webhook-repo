"""
Events API Route
================
This module provides the REST API for the frontend to fetch events.

Endpoint: GET /events

This endpoint is used by the Next.js frontend to poll for new events
every 15 seconds. It supports filtering by timestamp to return only
events that haven't been displayed yet.

Interview Tip:
    For polling endpoints, always support incremental fetching
    using timestamps. This prevents the frontend from re-fetching
    and re-rendering data it already has.
"""

from datetime import datetime
from flask import Blueprint, request, jsonify

from app.services.event_service import get_recent_events, get_all_events, get_events_count

# Create a Blueprint for events routes
events_bp = Blueprint("events", __name__)


@events_bp.route("/events", methods=["GET"])
def get_events():
    """
    Get events for the frontend UI.
    
    Query Parameters:
        since (optional): ISO 8601 timestamp to fetch events after
                         Format: "2024-01-26T15:30:00Z"
        all (optional): If "true", fetch all events (for initial load)
        limit (optional): Maximum number of events to return (default: 50)
    
    Returns:
        JSON response with:
        - events: Array of event objects
        - count: Number of events returned
        - last_timestamp: Timestamp of the most recent event (for next poll)
    
    Usage Examples:
        # Initial load - get all recent events
        GET /events?all=true
        
        # Subsequent polls - get only new events
        GET /events?since=2024-01-26T15:30:00Z
    
    Interview Tip:
        Returning last_timestamp in the response helps the frontend
        know what timestamp to use for the next poll. This is a clean
        pattern for incremental data fetching.
    """
    try:
        # Parse query parameters
        since_param = request.args.get("since")
        fetch_all = request.args.get("all", "false").lower() == "true"
        limit = int(request.args.get("limit", 50))
        
        # Validate limit
        if limit < 1:
            limit = 1
        elif limit > 100:
            limit = 100
        
        # Parse the 'since' timestamp if provided
        since_datetime = None
        if since_param:
            try:
                # Handle ISO 8601 format with Z suffix
                if since_param.endswith("Z"):
                    since_param = since_param[:-1] + "+00:00"
                since_datetime = datetime.fromisoformat(since_param)
                # Remove timezone info for MongoDB query (we store as naive UTC)
                since_datetime = since_datetime.replace(tzinfo=None)
            except ValueError as e:
                return jsonify({
                    "status": "error",
                    "message": f"Invalid timestamp format: {e}"
                }), 400
        
        # Fetch events based on parameters
        if fetch_all:
            events = get_all_events(limit=limit)
        else:
            events = get_recent_events(since=since_datetime, limit=limit)
        
        # Determine last_timestamp for the next poll
        last_timestamp = None
        if events:
            # The first event is the most recent (sorted by latest first)
            last_timestamp = events[0]["timestamp"]
        
        # Return response
        return jsonify({
            "status": "success",
            "events": events,
            "count": len(events),
            "last_timestamp": last_timestamp,
            "total_in_db": get_events_count()
        }), 200
    
    except Exception as e:
        print(f"Error fetching events: {e}")
        return jsonify({
            "status": "error",
            "message": "Failed to fetch events"
        }), 500


@events_bp.route("/events/stats", methods=["GET"])
def get_stats():
    """
    Get statistics about stored events.
    
    This endpoint is useful for debugging and monitoring.
    
    Returns:
        JSON response with event counts and statistics.
    """
    try:
        total_count = get_events_count()
        
        return jsonify({
            "status": "success",
            "total_events": total_count
        }), 200
    
    except Exception as e:
        print(f"Error fetching stats: {e}")
        return jsonify({
            "status": "error",
            "message": "Failed to fetch statistics"
        }), 500
