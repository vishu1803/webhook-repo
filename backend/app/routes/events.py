"""Events API route - provides events for frontend polling."""

from datetime import datetime
from flask import Blueprint, request, jsonify
from app.services.event_service import get_recent_events, get_all_events, get_events_count

events_bp = Blueprint("events", __name__)


@events_bp.route("/events", methods=["GET"])
def get_events():
    """
    Get events for UI display.
    
    Query params:
        since: ISO timestamp to fetch events after
        all: If "true", fetch all events
        limit: Max events to return (default: 50)
    """
    try:
        since_param = request.args.get("since")
        fetch_all = request.args.get("all", "false").lower() == "true"
        limit = min(max(int(request.args.get("limit", 50)), 1), 100)
        
        # Parse timestamp
        since_datetime = None
        if since_param:
            try:
                if since_param.endswith("Z"):
                    since_param = since_param[:-1] + "+00:00"
                since_datetime = datetime.fromisoformat(since_param).replace(tzinfo=None)
            except ValueError as e:
                return jsonify({"status": "error", "message": f"Invalid timestamp: {e}"}), 400
        
        # Fetch events
        if fetch_all:
            events = get_all_events(limit=limit)
        else:
            events = get_recent_events(since=since_datetime, limit=limit)
        
        last_timestamp = events[0]["timestamp"] if events else None
        
        return jsonify({
            "status": "success",
            "events": events,
            "count": len(events),
            "last_timestamp": last_timestamp,
            "total_in_db": get_events_count()
        }), 200
    
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error", "message": "Failed to fetch events"}), 500


@events_bp.route("/events/stats", methods=["GET"])
def get_stats():
    """Get event statistics."""
    try:
        return jsonify({"status": "success", "total_events": get_events_count()}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error", "message": "Failed to fetch stats"}), 500
