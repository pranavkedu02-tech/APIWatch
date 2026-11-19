
import time
from typing import Any

import httpx

from apiwatch.config import APIWatchConfig
from apiwatch.models import APIResult


class APIWatch:
    """Send HTTP requests and return structured monitoring results."""

    def __init__(
        self,
        timeout: float = 10.0,
        transport: httpx.BaseTransport | None = None,
        *,
        config: APIWatchConfig | None = None,
    ) -> None:

        if config is not None:
            self.config = config
        else:
            self.config = APIWatchConfig(timeout=timeout)

        self.timeout = self.config.timeout

        self._client = httpx.Client(
            timeout=self.timeout,
            transport=transport,
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

        method = (method or self.config.default_method).upper()

        request_headers = {
            **self.config.headers,
            **(headers or {}),
        }

        request_params = {
            **self.config.params,
            **(params or {}),
        }

        start_time = time.perf_counter()

        try:
            response = self._client.request(
                method=method,
                url=url,
                headers=request_headers,
                params=request_params,
                json=json,
            )

            elapsed = time.perf_counter() - start_time

            return APIResult(
                url=str(response.url),
                method=method,
                status_code=response.status_code,
                response_time=elapsed,
                is_success=response.is_success,
                response_size=len(response.content),
            )

        except httpx.RequestError as exc:

            elapsed = time.perf_counter() - start_time

            return APIResult(
                url=url,
                method=method,
                response_time=elapsed,
                is_success=False,
                error=str(exc),
            )

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "APIWatch":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()
