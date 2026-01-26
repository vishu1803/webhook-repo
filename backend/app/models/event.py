"""
Event Model
============
This module defines the Event model structure and validation.

Schema (STRICT - as per requirements):
{
    _id: ObjectId,          # MongoDB auto-generated
    request_id: string,     # Unique identifier (commit hash or PR ID)
    author: string,         # GitHub username
    action: string,         # Enum: "PUSH", "PULL_REQUEST", "MERGE"
    from_branch: string,    # Source branch
    to_branch: string,      # Target branch
    timestamp: datetime     # UTC datetime
}

Interview Tip:
    Using dataclasses or Pydantic for models is a best practice.
    It provides type hints, validation, and clean serialization.
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional
from enum import Enum


class ActionType(Enum):
    """
    Enum for GitHub event action types.
    
    Using an Enum ensures only valid action types are used,
    preventing typos and providing IDE autocompletion.
    """
    PUSH = "PUSH"
    PULL_REQUEST = "PULL_REQUEST"
    MERGE = "MERGE"


@dataclass
class Event:
    """
    Event model representing a GitHub event.
    
    This is the clean data structure that matches our MongoDB schema.
    Only these fields are stored - no extra data from the webhook payload.
    
    Attributes:
        request_id: Unique identifier (commit hash for PUSH, PR ID for PR/MERGE)
        author: GitHub username who triggered the event
        action: Type of action (PUSH, PULL_REQUEST, or MERGE)
        from_branch: Source branch name
        to_branch: Target branch name
        timestamp: UTC datetime when the event occurred
    
    Interview Tip:
        Using dataclasses reduces boilerplate code significantly.
        The @dataclass decorator auto-generates __init__, __repr__, etc.
    """
    request_id: str
    author: str
    action: str
    from_branch: str
    to_branch: str
    timestamp: datetime
    
    def to_dict(self) -> dict:
        """
        Convert the Event to a dictionary for MongoDB insertion.
        
        Returns:
            dict: Event data ready for MongoDB insertion
        
        Note:
            We exclude _id here as MongoDB will auto-generate it.
        """
        return asdict(self)
    
    def to_api_response(self) -> dict:
        """
        Convert the Event to a dictionary for API response.
        
        Returns:
            dict: Event data formatted for JSON API response
        
        Note:
            Timestamp is converted to ISO format string for JSON serialization.
        """
        return {
            "request_id": self.request_id,
            "author": self.author,
            "action": self.action,
            "from_branch": self.from_branch,
            "to_branch": self.to_branch,
            "timestamp": self.timestamp.isoformat() + "Z"  # ISO 8601 UTC format
        }
    
    @classmethod
    def from_db_document(cls, doc: dict) -> Optional["Event"]:
        """
        Create an Event from a MongoDB document.
        
        Args:
            doc: MongoDB document dictionary
        
        Returns:
            Event: Event instance, or None if invalid document
        
        Interview Tip:
            Using @classmethod for alternative constructors is a Python convention.
            It allows creating instances from different data sources.
        """
        if not doc:
            return None
        
        return cls(
            request_id=doc["request_id"],
            author=doc["author"],
            action=doc["action"],
            from_branch=doc["from_branch"],
            to_branch=doc["to_branch"],
            timestamp=doc["timestamp"]
        )
    
    def validate(self) -> bool:
        """
        Validate the event data.
        
        Returns:
            bool: True if valid, raises ValueError if invalid
        
        Raises:
            ValueError: If any required field is missing or invalid
        """
        # Check required fields are not empty
        if not self.request_id or not self.request_id.strip():
            raise ValueError("request_id is required")
        
        if not self.author or not self.author.strip():
            raise ValueError("author is required")
        
        # Validate action is one of the allowed types
        valid_actions = [a.value for a in ActionType]
        if self.action not in valid_actions:
            raise ValueError(f"action must be one of: {valid_actions}")
        
        # Validate branches
        if not self.from_branch or not self.from_branch.strip():
            raise ValueError("from_branch is required")
        
        if not self.to_branch or not self.to_branch.strip():
            raise ValueError("to_branch is required")
        
        # Validate timestamp
        if not isinstance(self.timestamp, datetime):
            raise ValueError("timestamp must be a datetime object")
        
        return True
