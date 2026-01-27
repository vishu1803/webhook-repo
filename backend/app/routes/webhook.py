"""Webhook route - receives GitHub webhook payloads."""

from flask import Blueprint, request, jsonify
from app.services.event_parser import parse_push_event, parse_pull_request_event
from app.services.event_service import save_event

webhook_bp = Blueprint("webhook", __name__)


@webhook_bp.route("/webhook", methods=["POST"])
def handle_webhook():
    """
    Handle incoming GitHub webhook requests.
    
    Supported events: push, pull_request (including merge)
    """
    try:
        event_type = request.headers.get("X-GitHub-Event", "")
        payload = request.get_json()
        
        print(f"\n{'='*50}")
        print(f"Received webhook: {event_type}")
        print(f"{'='*50}")
        
        if not payload:
            return jsonify({"status": "error", "message": "No JSON payload"}), 400
        
        # Handle ping (webhook configuration test)
        if event_type == "ping":
            return jsonify({"status": "success", "message": "Pong!"}), 200
        
        # Parse event based on type
        event = None
        if event_type == "push":
            event = parse_push_event(payload)
        elif event_type == "pull_request":
            event = parse_pull_request_event(payload)
        else:
            return jsonify({"status": "ignored", "message": f"Unsupported event: {event_type}"}), 200
        
        if event is None:
            return jsonify({"status": "error", "message": "Failed to parse payload"}), 400
        
        # Save event
        saved = save_event(event)
        
        if saved:
            return jsonify({
                "status": "success",
                "message": f"{event.action} event saved",
                "request_id": event.request_id
            }), 200
        else:
            return jsonify({
                "status": "duplicate",
                "message": "Event already exists",
                "request_id": event.request_id
            }), 200
    
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error", "message": "Internal server error"}), 500


@webhook_bp.route("/webhook", methods=["GET"])
def webhook_info():
    """Return webhook endpoint documentation."""
    return jsonify({
        "endpoint": "/webhook",
        "method": "POST",
        "supported_events": ["push", "pull_request"],
        "headers": {"required": ["X-GitHub-Event", "Content-Type: application/json"]}
    }), 200
