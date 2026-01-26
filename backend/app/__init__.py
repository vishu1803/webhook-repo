"""
Flask Application Factory
=========================
This module contains the application factory function that creates
and configures the Flask application.

Why use an App Factory?
- Allows creating multiple instances for testing
- Enables different configurations for dev/prod
- Better separation of concerns

Interview Tip:
    The application factory pattern is a Flask best practice.
    It's commonly asked about in Python web development interviews.
"""

from flask import Flask
from flask_cors import CORS

from app.config import Config
from app.utils.database import init_database
from app.routes.webhook import webhook_bp
from app.routes.events import events_bp


def create_app(config_class=Config):
    """
    Create and configure the Flask application.
    
    Args:
        config_class: Configuration class to use (default: Config)
    
    Returns:
        Flask: Configured Flask application instance
    
    Interview Tip:
        This factory pattern allows you to create different app instances
        with different configurations - essential for testing.
    """
    # Initialize Flask app
    app = Flask(__name__)
    
    # Load configuration from config class
    app.config.from_object(config_class)
    
    # Enable CORS for frontend communication
    # This allows the Next.js frontend to make requests to this API
    CORS(app, resources={
        r"/*": {
            "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type", "X-GitHub-Event", "X-Hub-Signature-256"]
        }
    })
    
    # Initialize database connection and create indexes
    with app.app_context():
        init_database()
    
    # Register blueprints (route modules)
    # Blueprints help organize routes into logical groups
    app.register_blueprint(webhook_bp)
    app.register_blueprint(events_bp)
    
    # Health check endpoint
    @app.route("/health")
    def health_check():
        """Simple health check endpoint for monitoring."""
        return {"status": "healthy", "service": "github-webhook-receiver"}
    
    return app
