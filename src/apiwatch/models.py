
from datetime import datetime, timezone

from pydantic import BaseModel, Field


class APIResult(BaseModel):
    """Structured result returned by an APIWatch check."""

    url: str
    method: str
    status_code: int | None = None
    response_time: float
    is_success: bool
    response_size: int | None = None
    error: str | None = None
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
