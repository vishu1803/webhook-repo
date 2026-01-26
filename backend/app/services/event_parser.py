"""
Event Parser Service
====================
This module handles parsing of GitHub webhook payloads.

Why separate parsing logic?
- Single Responsibility Principle: parsing is a distinct concern
- Easy to test in isolation
- Easy to add new event types

IMPORTANT: Only extract required fields, never store raw payload!

Interview Tip:
    Always validate and sanitize external input.
    GitHub webhooks are external data - treat them carefully.
"""

from datetime import datetime, timezone
from typing import Optional
from app.models.event import Event, ActionType


def parse_push_event(payload: dict) -> Optional[Event]:
    """
    Parse a GitHub PUSH webhook payload.
    
    GitHub PUSH payload structure (simplified):
    {
        "ref": "refs/heads/main",
        "head_commit": {
            "id": "abc123...",
            "timestamp": "2024-01-26T15:30:00Z"
        },
        "pusher": {
            "name": "username"
        }
    }
    
    Args:
        payload: GitHub webhook payload dictionary
    
    Returns:
        Event: Parsed Event object, or None if parsing fails
    
    Interview Tip:
        Use .get() for safe dictionary access to avoid KeyError.
        Always have fallback values for missing data.
    """
    try:
        # Extract branch name from ref (e.g., "refs/heads/main" -> "main")
        ref = payload.get("ref", "")
        branch_name = ref.replace("refs/heads/", "") if ref else "unknown"
        
        # Get head_commit data (the latest commit in the push)
        head_commit = payload.get("head_commit", {})
        
        # Extract commit hash as request_id
        # For push events with multiple commits, we use the head commit
        commit_hash = head_commit.get("id", "")
        
        if not commit_hash:
            # Fallback: try to get from 'after' field (commit SHA after push)
            commit_hash = payload.get("after", "")
        
        if not commit_hash:
            print("Warning: No commit hash found in push event")
            return None
        
        # Extract author from pusher
        pusher = payload.get("pusher", {})
        author = pusher.get("name", "unknown")
        
        # Parse timestamp and convert to UTC
        timestamp_str = head_commit.get("timestamp", "")
        timestamp = _parse_timestamp(timestamp_str)
        
        # For PUSH, from_branch and to_branch are the same
        # (you're pushing TO the same branch you're working on)
        event = Event(
            request_id=commit_hash,
            author=author,
            action=ActionType.PUSH.value,
            from_branch=branch_name,
            to_branch=branch_name,
            timestamp=timestamp
        )
        
        # Validate before returning
        event.validate()
        return event
    
    except Exception as e:
        print(f"Error parsing push event: {e}")
        return None


def parse_pull_request_event(payload: dict) -> Optional[Event]:
    """
    Parse a GitHub PULL_REQUEST webhook payload.
    
    GitHub PULL_REQUEST payload structure (simplified):
    {
        "action": "opened" | "closed" | "merged",
        "pull_request": {
            "id": 123456,
            "merged": true | false,
            "user": {"login": "username"},
            "head": {"ref": "feature-branch"},
            "base": {"ref": "main"},
            "created_at": "2024-01-26T15:30:00Z",
            "merged_at": "2024-01-26T16:00:00Z"
        }
    }
    
    Args:
        payload: GitHub webhook payload dictionary
    
    Returns:
        Event: Parsed Event object, or None if parsing fails
    
    Note:
        This function handles both PULL_REQUEST and MERGE events.
        If a PR is closed with merged=true, it's treated as a MERGE.
    """
    try:
        # Get the action type from GitHub's payload
        github_action = payload.get("action", "")
        
        # Get pull request data
        pr_data = payload.get("pull_request", {})
        
        if not pr_data:
            print("Warning: No pull_request data found")
            return None
        
        # Check if this is a merge event
        # A merge happens when action is "closed" AND merged is true
        is_merged = pr_data.get("merged", False)
        is_closed = github_action == "closed"
        
        # Determine our action type
        if is_closed and is_merged:
            action_type = ActionType.MERGE.value
        elif github_action in ["opened", "reopened", "synchronize"]:
            action_type = ActionType.PULL_REQUEST.value
        else:
            # Skip other PR actions (edited, labeled, etc.)
            print(f"Skipping PR action: {github_action}")
            return None
        
        # Extract PR ID as request_id
        # Using pr number which is more readable than the internal id
        pr_number = pr_data.get("number", pr_data.get("id", ""))
        request_id = f"PR-{pr_number}"
        
        # For merge events, make request_id unique per merge
        if action_type == ActionType.MERGE.value:
            request_id = f"MERGE-{pr_number}"
        
        # Extract author
        user_data = pr_data.get("user", {})
        author = user_data.get("login", "unknown")
        
        # Extract branches
        # head = source branch (feature branch)
        # base = target branch (main, develop, etc.)
        head_data = pr_data.get("head", {})
        base_data = pr_data.get("base", {})
        
        from_branch = head_data.get("ref", "unknown")
        to_branch = base_data.get("ref", "unknown")
        
        # Parse timestamp
        # For merges, use merged_at; for PRs, use created_at or updated_at
        if action_type == ActionType.MERGE.value:
            timestamp_str = pr_data.get("merged_at", "")
        else:
            timestamp_str = pr_data.get("created_at", pr_data.get("updated_at", ""))
        
        timestamp = _parse_timestamp(timestamp_str)
        
        event = Event(
            request_id=request_id,
            author=author,
            action=action_type,
            from_branch=from_branch,
            to_branch=to_branch,
            timestamp=timestamp
        )
        
        # Validate before returning
        event.validate()
        return event
    
    except Exception as e:
        print(f"Error parsing pull_request event: {e}")
        return None


def _parse_timestamp(timestamp_str: str) -> datetime:
    """
    Parse a timestamp string to UTC datetime.
    
    Args:
        timestamp_str: ISO 8601 timestamp string from GitHub
    
    Returns:
        datetime: UTC datetime object
    
    Note:
        GitHub uses ISO 8601 format: "2024-01-26T15:30:00Z"
        We always convert to UTC for consistency.
    
    Interview Tip:
        Always store timestamps in UTC in your database.
        Convert to local time only when displaying to users.
    """
    if not timestamp_str:
        # Fallback to current UTC time if no timestamp provided
        return datetime.now(timezone.utc)
    
    try:
        # Try parsing ISO 8601 format with Z suffix
        if timestamp_str.endswith("Z"):
            timestamp_str = timestamp_str[:-1] + "+00:00"
        
        # Parse the timestamp
        dt = datetime.fromisoformat(timestamp_str)
        
        # Convert to UTC if not already
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            dt = dt.astimezone(timezone.utc)
        
        # Return as UTC datetime (remove tzinfo for MongoDB compatibility)
        return dt.replace(tzinfo=None)
    
    except ValueError as e:
        print(f"Warning: Could not parse timestamp '{timestamp_str}': {e}")
        return datetime.utcnow()
