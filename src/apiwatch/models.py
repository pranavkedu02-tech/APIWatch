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

    # JSON Schema validation results
    is_valid: bool | None = None
    validation_errors: list[str] = Field(default_factory=list)

    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    # ----------------------------------------
    # Assertion Methods
    # ----------------------------------------

    def assert_status_code(
        self,
        expected: int,
    ) -> None:
        """Assert that the response status code matches the expected value."""

        assert self.status_code == expected, (
            f"Expected status code {expected}, "
            f"but received {self.status_code}. "
            f"URL: {self.url}"
        )

    def assert_success(self) -> None:
        """Assert that the API request was successful."""

        assert self.is_success, (
            f"API request failed. "
            f"Status code: {self.status_code}. "
            f"Error: {self.error}. "
            f"URL: {self.url}"
        )

    def assert_response_time(
        self,
        max_seconds: float,
    ) -> None:
        """Assert that response time is within the specified limit."""

        assert self.response_time <= max_seconds, (
            f"Response time exceeded limit. "
            f"Expected <= {max_seconds:.4f}s, "
            f"but received {self.response_time:.4f}s. "
            f"URL: {self.url}"
        )

    def assert_valid(self) -> None:
        """Assert that JSON Schema validation passed."""

        assert self.is_valid is True, (
            "Response schema validation failed. "
            f"Errors: {self.validation_errors}. "
            f"URL: {self.url}"
        )

    def assert_no_errors(self) -> None:
        """Assert that the request and validation have no errors."""

        assert self.is_success, (
            f"API request failed. "
            f"Status code: {self.status_code}. "
            f"Error: {self.error}"
        )

        assert not self.error, (
            f"Request error detected: {self.error}"
        )

        assert not self.validation_errors, (
            f"Validation errors detected: "
            f"{self.validation_errors}"
        )