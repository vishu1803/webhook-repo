"""
Application Entry Point
=======================
This is the main entry point for the Flask application.
Run this file to start the webhook server.

Usage:
    python run.py

Interview Tip:
    Always separate the application entry point from the app factory.
    This allows for better testing and configuration flexibility.
"""

from app import create_app
from app.config import Config

# Create the Flask application using the factory pattern
app = create_app()

if __name__ == "__main__":
    # Run the development server
    # In production, use gunicorn: gunicorn -w 4 -b 0.0.0.0:5000 run:app
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.FLASK_DEBUG
    )
