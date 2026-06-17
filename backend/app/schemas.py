from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Tags(BaseModel):
    team: Optional[str] = None
    feature: Optional[str] = None
    env: Optional[str] = None
    client: Optional[str] = None


class EventIn(BaseModel):
    """Payload sent by the SDK to POST /v1/events (PRD §5)."""

    timestamp: datetime
    model: str
    tokens_in: int = Field(ge=0)
    tokens_out: int = Field(ge=0)
    cost_usd: float = Field(ge=0)
    duration_ms: Optional[int] = Field(default=None, ge=0)
    success: bool = True
    tags: Tags = Field(default_factory=Tags)


class EventAccepted(BaseModel):
    id: str
