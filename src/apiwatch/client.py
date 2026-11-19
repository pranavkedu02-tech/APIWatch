
import time
from typing import Any

import httpx

from apiwatch.config import APIWatchConfig
from apiwatch.history import APIHistory
from apiwatch.logger import setup_logger
from apiwatch.models import APIResult


class APIWatch:
    """Send HTTP requests and return structured monitoring results."""

    def __init__(
        self,
        timeout: float = 10.0,
        transport: httpx.BaseTransport | None = None,
        *,
        config: APIWatchConfig | None = None,
        history_db: str | None = None,
    ) -> None:

        if config is not None:
            self.config = config
        else:
            self.config = APIWatchConfig(timeout=timeout)

        self.timeout = self.config.timeout

        self.logger = setup_logger(
            name="apiwatch",
            level=self.config.log_level,
            log_file=self.config.log_file,
        )

        self._client = httpx.Client(
            timeout=self.timeout,
            transport=transport,
        )

        # Monitoring history.
        # If history_db is provided, SQLite is used.
        # Otherwise, history is stored in memory.
        self.history = APIHistory(
            database_path=history_db
        )

    def check(
        self,
        url: str,
        method: str | None = None,
        *,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        json: Any = None,
    ) -> APIResult:
        """Make an HTTP request with retries, logging, and history."""

        method = (method or self.config.default_method).upper()

        request_headers = {
            **self.config.headers,
            **(headers or {}),
        }

        request_params = {
            **self.config.params,
            **(params or {}),
        }

        self.logger.info(
            "Checking API: %s %s",
            method,
            url,
        )

        start_time = time.perf_counter()

        last_error = None

        for attempt in range(self.config.max_retries + 1):

            try:
                response = self._client.request(
                    method=method,
                    url=url,
                    headers=request_headers,
                    params=request_params,
                    json=json,
                )

                # Retry configured status codes
                if (
                    response.status_code
                    in self.config.retry_status_codes
                    and attempt < self.config.max_retries
                ):

                    delay = (
                        self.config.retry_delay
                        * self.config.backoff_factor ** attempt
                    )

                    self.logger.warning(
                        "HTTP %s received. "
                        "Retrying attempt %s/%s in %.2f seconds",
                        response.status_code,
                        attempt + 2,
                        self.config.max_retries + 1,
                        delay,
                    )

                    time.sleep(delay)

                    continue

                elapsed = time.perf_counter() - start_time

                if response.is_success:

                    self.logger.info(
                        "API check successful | "
                        "Status: %s | "
                        "Response time: %.4fs | "
                        "Response size: %s bytes",
                        response.status_code,
                        elapsed,
                        len(response.content),
                    )

                else:

                    self.logger.error(
                        "API check failed | "
                        "Status: %s | "
                        "Response time: %.4fs",
                        response.status_code,
                        elapsed,
                    )

                result = APIResult(
                    url=str(response.url),
                    method=method,
                    status_code=response.status_code,
                    response_time=elapsed,
                    is_success=response.is_success,
                    response_size=len(response.content),
                )

                self.history.add(result)

                return result

            except httpx.RequestError as exc:

                last_error = exc

                if attempt < self.config.max_retries:

                    delay = (
                        self.config.retry_delay
                        * self.config.backoff_factor ** attempt
                    )

                    self.logger.warning(
                        "Request error: %s | "
                        "Retrying attempt %s/%s in %.2f seconds",
                        exc,
                        attempt + 2,
                        self.config.max_retries + 1,
                        delay,
                    )

                    time.sleep(delay)

                    continue

                elapsed = time.perf_counter() - start_time

                self.logger.error(
                    "API request failed after %s attempts: %s",
                    attempt + 1,
                    exc,
                )

                result = APIResult(
                    url=url,
                    method=method,
                    response_time=elapsed,
                    is_success=False,
                    error=str(last_error),
                )

                self.history.add(result)

                return result

        elapsed = time.perf_counter() - start_time

        self.logger.error(
            "API request failed: %s",
            last_error,
        )

        result = APIResult(
            url=url,
            method=method,
            response_time=elapsed,
            is_success=False,
            error=str(last_error) if last_error else "Request failed",
        )

        self.history.add(result)

        return result

    def get_history(
        self,
        url: str | None = None,
    ) -> list[APIResult]:
        """Return monitoring history, optionally filtered by URL."""

        return self.history.get_history(url)

    def get_stats(
        self,
        url: str | None = None,
    ) -> dict:
        """Return monitoring statistics, optionally filtered by URL."""

        return self.history.get_stats(url)

    def clear_history(self) -> None:
        """Clear all stored monitoring history."""

        self.history.clear()

    def close(self) -> None:
        """Close HTTP client and history database."""

        self._client.close()
        self.history.close()

    def __enter__(self) -> "APIWatch":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()
