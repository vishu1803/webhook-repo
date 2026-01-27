"""MongoDB database utilities."""

from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure
from app.config import Config

# Module-level references
_client = None
_db = None
_collection = None


def get_database():
    """Get MongoDB database instance."""
    global _client, _db
    
    if _db is None:
        try:
            _client = MongoClient(Config.MONGODB_URI)
            _db = _client[Config.DATABASE_NAME]
            _client.admin.command('ping')
            print(f"✓ Connected to MongoDB: {Config.DATABASE_NAME}")
        except ConnectionFailure as e:
            print(f"✗ Failed to connect to MongoDB: {e}")
            raise
    
    return _db


def get_collection():
    """Get github_events collection."""
    global _collection
    
    if _collection is None:
        db = get_database()
        _collection = db[Config.COLLECTION_NAME]
    
    return _collection


def init_database():
    """Initialize database and create indexes."""
    collection = get_collection()
    
    # Unique index on request_id (prevents duplicates)
    collection.create_index(
        [("request_id", ASCENDING)],
        unique=True,
        name="request_id_unique_idx"
    )
    print("✓ Created unique index on request_id")
    
    # Descending index on timestamp (for sorting)
    collection.create_index(
        [("timestamp", DESCENDING)],
        name="timestamp_desc_idx"
    )
    print("✓ Created index on timestamp")


def close_connection():
    """Close MongoDB connection."""
    global _client, _db, _collection
    
    if _client:
        _client.close()
        _client = None
        _db = None
        _collection = None
        print("✓ MongoDB connection closed")
