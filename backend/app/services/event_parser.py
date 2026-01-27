"""Event parser - extracts required fields from GitHub webhook payloads."""

from datetime import datetime, timezone
from typing import Optional
from app.models.event import Event, ActionType


def parse_push_event(payload: dict) -> Optional[Event]:
    """Parse GitHub PUSH webhook payload."""
    try:
        ref = payload.get("ref", "")
        branch_name = ref.replace("refs/heads/", "") if ref else "unknown"
        
        head_commit = payload.get("head_commit", {})
        commit_hash = head_commit.get("id", "") or payload.get("after", "")
        
        if not commit_hash:
            return None
        
        pusher = payload.get("pusher", {})
        author = pusher.get("name", "unknown")
        timestamp = _parse_timestamp(head_commit.get("timestamp", ""))
        
        event = Event(
            request_id=commit_hash,
            author=author,
            action=ActionType.PUSH.value,
            from_branch=branch_name,
            to_branch=branch_name,
            timestamp=timestamp
        )
        event.validate()
        return event
    
    except Exception as e:
        print(f"Error parsing push event: {e}")
        return None


def parse_pull_request_event(payload: dict) -> Optional[Event]:
    """Parse GitHub PULL_REQUEST webhook payload (handles PR and MERGE)."""
    try:
        github_action = payload.get("action", "")
        pr_data = payload.get("pull_request", {})
        
        if not pr_data:
            return None
        
        # Determine action type
        is_merged = pr_data.get("merged", False)
        is_closed = github_action == "closed"
        
        if is_closed and is_merged:
            action_type = ActionType.MERGE.value
        elif github_action in ["opened", "reopened", "synchronize"]:
            action_type = ActionType.PULL_REQUEST.value
        else:
            return None  # Skip other PR actions
        
        pr_number = pr_data.get("number", pr_data.get("id", ""))
        request_id = f"MERGE-{pr_number}" if action_type == ActionType.MERGE.value else f"PR-{pr_number}"
        
        author = pr_data.get("user", {}).get("login", "unknown")
        from_branch = pr_data.get("head", {}).get("ref", "unknown")
        to_branch = pr_data.get("base", {}).get("ref", "unknown")
        
        timestamp_str = pr_data.get("merged_at", "") if action_type == ActionType.MERGE.value else pr_data.get("created_at", "")
        timestamp = _parse_timestamp(timestamp_str)
        
        event = Event(
            request_id=request_id,
            author=author,
            action=action_type,
            from_branch=from_branch,
            to_branch=to_branch,
            timestamp=timestamp
        )
        event.validate()
        return event
    
    except Exception as e:
        print(f"Error parsing pull_request event: {e}")
        return None


def _parse_timestamp(timestamp_str: str) -> datetime:
    """Parse ISO timestamp string to UTC datetime."""
    if not timestamp_str:
        return datetime.utcnow()
    
    try:
        if timestamp_str.endswith("Z"):
            timestamp_str = timestamp_str[:-1] + "+00:00"
        
        dt = datetime.fromisoformat(timestamp_str)
        
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            dt = dt.astimezone(timezone.utc)
        
        return dt.replace(tzinfo=None)
    
    except ValueError:
        return datetime.utcnow()
