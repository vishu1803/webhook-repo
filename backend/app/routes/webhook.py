"""
Webhook Route
=============
This module handles incoming GitHub webhook requests.

Endpoint: POST /webhook

How GitHub Webhooks Work:
1. You configure a webhook URL in your GitHub repository settings
2. When events occur (push, PR, etc.), GitHub sends a POST request
3. The request includes the event type in the X-GitHub-Event header
4. The request body contains the event payload as JSON

Interview Tip:
    Always validate webhook payloads in production.
    GitHub provides a secret-based signature verification (X-Hub-Signature-256)
    that ensures the request actually came from GitHub.
"""

from flask import Blueprint, request, jsonify

from app.services.event_parser import parse_push_event, parse_pull_request_event
from app.services.event_service import save_event

# Create a Blueprint for webhook routes
# Blueprints help organize Flask apps into modular components
webhook_bp = Blueprint("webhook", __name__)


@webhook_bp.route("/webhook", methods=["POST"])
def handle_webhook():
    """
    Handle incoming GitHub webhook requests.
    
    This endpoint receives webhook payloads from GitHub and:
    1. Determines the event type from the X-GitHub-Event header
    2. Parses the payload to extract only required fields
    3. Saves the event to MongoDB (with duplicate prevention)
    
    Returns:
        JSON response with status message
    
    HTTP Status Codes:
        200: Event processed successfully
        400: Invalid payload or unsupported event type
        500: Server error during processing
    
    Interview Tip:
        Keep your route handlers thin - delegate logic to services.
        This makes the code easier to test and maintain.
    """
    try:
        # Get the event type from GitHub's header
        event_type = request.headers.get("X-GitHub-Event", "")
        
        # Log incoming webhook for debugging
        print(f"\n{'='*50}")
        print(f"Received webhook: {event_type}")
        print(f"{'='*50}")
        
        # Get the JSON payload
        payload = request.get_json()
        
        if not payload:
            return jsonify({
                "status": "error",
                "message": "No JSON payload received"
            }), 400
        
        # Handle ping event (sent when webhook is first configured)
        if event_type == "ping":
            return jsonify({
                "status": "success",
                "message": "Pong! Webhook configured successfully."
            }), 200
        
        # Parse the event based on type
        event = None
        
        if event_type == "push":
            event = parse_push_event(payload)
        
        elif event_type == "pull_request":
            event = parse_pull_request_event(payload)
        
        else:
            # Unsupported event type - log and acknowledge
            print(f"Unsupported event type: {event_type}")
            return jsonify({
                "status": "ignored",
                "message": f"Event type '{event_type}' is not supported"
            }), 200
        
        # If parsing failed, return error
        if event is None:
            return jsonify({
                "status": "error",
                "message": "Failed to parse event payload"
            }), 400
        
        # Save the event to database
        saved = save_event(event)
        
        if saved:
            return jsonify({
                "status": "success",
                "message": f"{event.action} event saved successfully",
                "request_id": event.request_id
            }), 200
        else:
            # Duplicate event - still return 200 (idempotent)
            return jsonify({
                "status": "duplicate",
                "message": "Event already exists",
                "request_id": event.request_id
            }), 200
    
    except Exception as e:
        # Log the error for debugging
        print(f"Error processing webhook: {e}")
        
        return jsonify({
            "status": "error",
            "message": "Internal server error"
        }), 500


@webhook_bp.route("/webhook", methods=["GET"])
def webhook_info():
    """
    Provide information about the webhook endpoint.
    
    This is helpful for debugging and documentation.
    GET requests to /webhook return usage information.
    """
    return jsonify({
        "endpoint": "/webhook",
        "method": "POST",
        "description": "GitHub webhook receiver",
        "supported_events": ["push", "pull_request"],
        "headers": {
            "required": ["X-GitHub-Event", "Content-Type: application/json"]
        }
    }), 200
