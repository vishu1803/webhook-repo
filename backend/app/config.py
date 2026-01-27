"""Application configuration."""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration from environment variables."""
    
    # MongoDB
    MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    DATABASE_NAME = os.getenv("DATABASE_NAME", "github_webhooks")
    COLLECTION_NAME = "github_events"
    
    # Flask
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    FLASK_DEBUG = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    
    # Server
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 5000))
    
    # Polling time window (seconds)
    EVENT_TIME_WINDOW = 15
