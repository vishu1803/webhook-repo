"""
MongoDB Database Utilities
==========================
This module handles MongoDB connection and provides database access utilities.

Why separate database logic?
- Single point of connection management
- Easy to mock for testing
- Centralized index creation

Interview Tip:
    Connection pooling is handled automatically by PyMongo.
    The MongoClient maintains a pool of connections for efficiency.
"""

from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError, ConnectionFailure
from app.config import Config

# Module-level database client and collection references
# These are initialized once and reused throughout the application
_client = None
_db = None
_collection = None


def get_database():
    """
    Get the MongoDB database instance.
    
    Returns:
        Database: MongoDB database object
    
    Raises:
        ConnectionFailure: If unable to connect to MongoDB
    """
    global _client, _db
    
    if _db is None:
        try:
            _client = MongoClient(Config.MONGODB_URI)
            _db = _client[Config.DATABASE_NAME]
            # Test the connection
            _client.admin.command('ping')
            print(f"✓ Connected to MongoDB: {Config.DATABASE_NAME}")
        except ConnectionFailure as e:
            print(f"✗ Failed to connect to MongoDB: {e}")
            raise
    
    return _db


def get_collection():
    """
    Get the github_events collection.
    
    Returns:
        Collection: MongoDB collection object for github_events
    
    Interview Tip:
        Always use a dedicated function to get collection references.
        This ensures consistent collection naming and easy refactoring.
    """
    global _collection
    
    if _collection is None:
        db = get_database()
        _collection = db[Config.COLLECTION_NAME]
    
    return _collection


def init_database():
    """
    Initialize database and create required indexes.
    
    This function should be called once during app startup.
    It creates:
    1. Unique index on request_id (prevents duplicates)
    2. Descending index on timestamp (for efficient sorting)
    
    Why create indexes?
    - request_id index: Ensures no duplicate events are stored
    - timestamp index: Speeds up queries that sort by time
    
    Interview Tip:
        Always create indexes on fields used in queries and unique constraints.
        Indexes significantly improve query performance on large collections.
    """
    collection = get_collection()
    
    # Create unique index on request_id to prevent duplicate events
    # If a duplicate request_id is inserted, MongoDB will raise DuplicateKeyError
    collection.create_index(
        [("request_id", ASCENDING)],
        unique=True,
        name="request_id_unique_idx"
    )
    print("✓ Created unique index on request_id")
    
    # Create descending index on timestamp for efficient sorting
    # Most queries will sort by latest first, so DESCENDING is optimal
    collection.create_index(
        [("timestamp", DESCENDING)],
        name="timestamp_desc_idx"
    )
    print("✓ Created index on timestamp")


def close_connection():
    """
    Close the MongoDB connection.
    
    Call this during application shutdown to cleanly close connections.
    """
    global _client, _db, _collection
    
    if _client:
        _client.close()
        _client = None
        _db = None
        _collection = None
        print("✓ MongoDB connection closed")
