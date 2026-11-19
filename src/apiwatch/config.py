from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class APIWatchConfig(BaseModel):
    """Configuration settings for APIWatch."""

    model_config = ConfigDict(extra="forbid")

    timeout: float = Field(default=10.0, gt=0)

    default_method: str = "GET"

    headers: dict[str, str] = Field(default_factory=dict)

    params: dict[str, Any] = Field(default_factory=dict)

    # Retry configuration
    max_retries: int = Field(default=3, ge=0)

    retry_delay: float = Field(default=1.0, ge=0)

    backoff_factor: float = Field(default=2.0, ge=1)

    retry_status_codes: set[int] = Field(
        default_factory=lambda: {
            429,
            500,
            502,
            503,
            504,
        }
    )

    @field_validator("default_method")
    @classmethod
    def validate_method(cls, value: str) -> str:
        value = value.strip().upper()

        if not value:
            raise ValueError("HTTP method cannot be empty")

        return value