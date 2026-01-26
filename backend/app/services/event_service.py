"""
Event Service
=============
This module handles business logic for GitHub events.

Responsibilities:
- Saving events to MongoDB (with duplicate prevention)
- Retrieving events for the UI (with time-based filtering)

Why separate service layer?
- Separates business logic from HTTP handling (routes)
- Separates business logic from data access (models)
- Makes code more testable and maintainable

Interview Tip:
    The service layer pattern is widely used in enterprise applications.
    It helps maintain separation of concerns and keeps controllers thin.
"""

from datetime import datetime, timedelta
from typing import List, Optional
from pymongo.errors import DuplicateKeyError

from app.utils.database import get_collection
from app.models.event import Event
from app.config import Config


def save_event(event: Event) -> bool:
    """
    Save an event to MongoDB.
    
    This function handles duplicate prevention using the unique index
    on request_id. If a duplicate is detected, it returns False instead
    of raising an error.
    
    Args:
        event: Event object to save
    
    Returns:
        bool: True if saved successfully, False if duplicate
    
    Interview Tip:
        Using upsert or handling DuplicateKeyError is a common pattern
        for idempotent operations. This is important for webhook handling
        since GitHub may send the same event multiple times.
    """
    try:
        # Validate the event before saving
        event.validate()
        
        # Get the collection
        collection = get_collection()
        
        # Convert event to dictionary for MongoDB
        event_doc = event.to_dict()
        
        # Insert the event
        result = collection.insert_one(event_doc)
        
        print(f"✓ Saved event: {event.action} by {event.author} (ID: {event.request_id})")
        return True
    
    except DuplicateKeyError:
        # This is expected behavior - not an error
        # It means we already have this event
        print(f"→ Duplicate event skipped: {event.request_id}")
        return False
    
    except ValueError as e:
        # Validation error
        print(f"✗ Invalid event: {e}")
        return False
    
    except Exception as e:
        print(f"✗ Error saving event: {e}")
        return False


def get_recent_events(since: Optional[datetime] = None, limit: int = 50) -> List[dict]:
    """
    Get recent events for UI display.
    
    This function retrieves events that occurred after a given timestamp.
    If no timestamp is provided, it returns events from the last time window
    (default: 15 seconds as per polling interval).
    
    Args:
        since: Optional datetime to fetch events after
        limit: Maximum number of events to return (default: 50)
    
    Returns:
        List[dict]: List of event dictionaries ready for API response
    
    Interview Tip:
        When implementing polling endpoints, always:
        1. Support filtering by timestamp to avoid returning stale data
        2. Sort by latest first for better UX
        3. Limit results to prevent memory issues
    """
    collection = get_collection()
    
    # Build query
    query = {}
    
    if since:
        # Get events after the given timestamp
        query["timestamp"] = {"$gt": since}
    else:
        # Default: get events from the last time window (15 seconds)
        time_window = datetime.utcnow() - timedelta(seconds=Config.EVENT_TIME_WINDOW)
        query["timestamp"] = {"$gt": time_window}
    
    # Execute query with sorting (latest first) and limit
    cursor = collection.find(query).sort("timestamp", -1).limit(limit)
    
    # Convert documents to API response format
    events = []
    for doc in cursor:
        event = Event.from_db_document(doc)
        if event:
            events.append(event.to_api_response())
    
    return events


def get_all_events(limit: int = 100) -> List[dict]:
    """
    Get all events (for initial page load).
    
    Args:
        limit: Maximum number of events to return
    
    Returns:
        List[dict]: List of event dictionaries
    
    Note:
        This is useful for the initial page load when the user
        first opens the UI and wants to see recent history.
    """
    collection = get_collection()
    
    # Get all events, sorted by latest first
    cursor = collection.find().sort("timestamp", -1).limit(limit)
    
    events = []
    for doc in cursor:
        event = Event.from_db_document(doc)
        if event:
            events.append(event.to_api_response())
    
    return events


def get_events_count() -> int:
    """
    Get total count of events in the database.
    
    Returns:
        int: Total number of events
    """
    collection = get_collection()
    return collection.count_documents({})
