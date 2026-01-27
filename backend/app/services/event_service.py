"""Event service - business logic for saving and retrieving events."""

from datetime import datetime, timedelta
from typing import List, Optional
from pymongo.errors import DuplicateKeyError

from app.utils.database import get_collection
from app.models.event import Event
from app.config import Config


def save_event(event: Event) -> bool:
    """Save event to MongoDB. Returns False if duplicate."""
    try:
        event.validate()
        collection = get_collection()
        collection.insert_one(event.to_dict())
        print(f"✓ Saved: {event.action} by {event.author} ({event.request_id})")
        return True
    
    except DuplicateKeyError:
        print(f"→ Duplicate skipped: {event.request_id}")
        return False
    
    except Exception as e:
        print(f"✗ Error saving event: {e}")
        return False


def get_recent_events(since: Optional[datetime] = None, limit: int = 50) -> List[dict]:
    """Get recent events since timestamp (default: last 15 seconds)."""
    collection = get_collection()
    
    if since:
        query = {"timestamp": {"$gt": since}}
    else:
        time_window = datetime.utcnow() - timedelta(seconds=Config.EVENT_TIME_WINDOW)
        query = {"timestamp": {"$gt": time_window}}
    
    cursor = collection.find(query).sort("timestamp", -1).limit(limit)
    
    events = []
    for doc in cursor:
        event = Event.from_db_document(doc)
        if event:
            events.append(event.to_api_response())
    
    return events


def get_all_events(limit: int = 100) -> List[dict]:
    """Get all events (for initial page load)."""
    collection = get_collection()
    cursor = collection.find().sort("timestamp", -1).limit(limit)
    
    events = []
    for doc in cursor:
        event = Event.from_db_document(doc)
        if event:
            events.append(event.to_api_response())
    
    return events


def get_events_count() -> int:
    """Get total event count."""
    return get_collection().count_documents({})
