"""Approvals bind an explicit action to exact content, URL, and site review."""
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json


@dataclass(frozen=True)
class Approval:
    action: str
    digest: str
    reviewer: str
    expires_at: datetime


def content_digest(payload: dict) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def require_approval(approval: Approval, action: str, payload: dict) -> None:
    if (approval.action != action or approval.digest != content_digest(payload)
            or not approval.reviewer.strip() or approval.expires_at.tzinfo is None
            or approval.expires_at <= datetime.now(timezone.utc)):
        raise PermissionError("A current human approval for this exact action is required")
