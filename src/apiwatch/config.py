from typing import Any

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


class APIWatchConfig(BaseModel):
    """Configuration settings for APIWatch."""

    model_config = ConfigDict(extra="forbid")

    # HTTP configuration
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

    # Logging configuration
    log_level: str = "INFO"

    log_file: str | None = None

    @field_validator("default_method")
    @classmethod
    def validate_method(cls, value: str) -> str:
        value = value.strip().upper()

        if not value:
            raise ValueError("HTTP method cannot be empty")

        return value

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, value: str) -> str:
        value = value.strip().upper()

        allowed_levels = {
            "DEBUG",
            "INFO",
            "WARNING",
            "ERROR",
            "CRITICAL",
        }

        if value not in allowed_levels:
            raise ValueError(
                f"Invalid log level: {value}. "
                f"Choose from {allowed_levels}"
            )

        return value