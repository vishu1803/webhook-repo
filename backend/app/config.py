"""
Application Configuration
=========================
Centralized configuration management using environment variables.

Why use a Config class?
- Single source of truth for all settings
- Easy to switch between dev/prod configurations
- Keeps sensitive data out of code (uses .env file)

Interview Tip:
    Never hardcode sensitive information like database URIs or secret keys.
    Always use environment variables loaded from a .env file.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
# This should be called before accessing any env variables
load_dotenv()


class Config:
    """
    Application configuration class.
    
    All configuration values are loaded from environment variables
    with sensible defaults for development.
    
    Attributes:
        MONGODB_URI: MongoDB connection string
        DATABASE_NAME: Name of the MongoDB database
        SECRET_KEY: Flask secret key for sessions
        FLASK_DEBUG: Enable/disable debug mode
        HOST: Server host address
        PORT: Server port number
    """
    
    # MongoDB Configuration
    # Default to localhost for development
    MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    DATABASE_NAME = os.getenv("DATABASE_NAME", "github_webhooks")
    
    # Collection name - keeping it consistent with requirements
    COLLECTION_NAME = "github_events"
    
    # Flask Configuration
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    FLASK_DEBUG = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    
    # Server Configuration
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 5000))
    
    # Polling Configuration
    # Time window (in seconds) for fetching recent events
    EVENT_TIME_WINDOW = 15


class ProductionConfig(Config):
    """Production-specific configuration."""
    FLASK_DEBUG = False


class DevelopmentConfig(Config):
    """Development-specific configuration."""
    FLASK_DEBUG = True


class TestingConfig(Config):
    """Testing-specific configuration."""
    FLASK_DEBUG = True
    DATABASE_NAME = "github_webhooks_test"
