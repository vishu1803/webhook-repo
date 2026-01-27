"""Event model and validation."""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional
from enum import Enum


class ActionType(Enum):
    """GitHub event action types."""
    PUSH = "PUSH"
    PULL_REQUEST = "PULL_REQUEST"
    MERGE = "MERGE"


@dataclass
class Event:
    """
    Event model matching MongoDB schema.
    
    Fields:
        request_id: Unique identifier (commit hash or PR ID)
        author: GitHub username
        action: PUSH, PULL_REQUEST, or MERGE
        from_branch: Source branch
        to_branch: Target branch
        timestamp: UTC datetime
    """
    request_id: str
    author: str
    action: str
    from_branch: str
    to_branch: str
    timestamp: datetime
    
    def to_dict(self) -> dict:
        """Convert to dictionary for MongoDB insertion."""
        return asdict(self)
    
    def to_api_response(self) -> dict:
        """Convert to dictionary for API response."""
        return {
            "request_id": self.request_id,
            "author": self.author,
            "action": self.action,
            "from_branch": self.from_branch,
            "to_branch": self.to_branch,
            "timestamp": self.timestamp.isoformat() + "Z"
        }
    
    @classmethod
    def from_db_document(cls, doc: dict) -> Optional["Event"]:
        """Create Event from MongoDB document."""
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
        """Validate event data. Raises ValueError if invalid."""
        if not self.request_id or not self.request_id.strip():
            raise ValueError("request_id is required")
        
        if not self.author or not self.author.strip():
            raise ValueError("author is required")
        
        valid_actions = [a.value for a in ActionType]
        if self.action not in valid_actions:
            raise ValueError(f"action must be one of: {valid_actions}")
        
        if not self.from_branch or not self.from_branch.strip():
            raise ValueError("from_branch is required")
        
        if not self.to_branch or not self.to_branch.strip():
            raise ValueError("to_branch is required")
        
        if not isinstance(self.timestamp, datetime):
            raise ValueError("timestamp must be a datetime object")
        
        return True
