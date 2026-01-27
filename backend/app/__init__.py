"""Flask application factory."""

from flask import Flask
from flask_cors import CORS

from app.config import Config
from app.utils.database import init_database
from app.routes.webhook import webhook_bp
from app.routes.events import events_bp


def create_app(config_class=Config):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Enable CORS for frontend
    CORS(app, resources={
        r"/*": {
            "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type", "X-GitHub-Event", "X-Hub-Signature-256"]
        }
    })
    
    # Initialize database
    with app.app_context():
        init_database()
    
    # Register routes
    app.register_blueprint(webhook_bp)
    app.register_blueprint(events_bp)
    
    @app.route("/health")
    def health_check():
        return {"status": "healthy", "service": "github-webhook-receiver"}
    
    return app
