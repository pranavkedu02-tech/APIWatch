
import httpx

from apiwatch import APIWatch, APIWatchConfig


def test_retries_server_error_then_succeeds(monkeypatch):
    """Retry a 503 response and eventually succeed."""

    attempts = 0
    delays = []

    def handler(request):
        nonlocal attempts
        attempts += 1

        if attempts < 3:
            return httpx.Response(503, request=request)

        return httpx.Response(200, request=request)

    monkeypatch.setattr(
        "apiwatch.client.time.sleep",
        delays.append,
    )

    config = APIWatchConfig(
        max_retries=3,
        retry_delay=1,
        backoff_factor=2,
    )

    transport = httpx.MockTransport(handler)

    with APIWatch(config=config, transport=transport) as watch:
        result = watch.check("https://example.com/api")

    assert result.status_code == 200
    assert result.is_success is True
    assert attempts == 3
    assert delays == [1, 2]


def test_retries_rate_limit(monkeypatch):
    """Retry HTTP 429 responses."""

    attempts = 0

    def handler(request):
        nonlocal attempts
        attempts += 1

        if attempts == 1:
            return httpx.Response(429, request=request)

        return httpx.Response(200, request=request)

    monkeypatch.setattr(
        "apiwatch.client.time.sleep",
        lambda delay: None,
    )

    config = APIWatchConfig(max_retries=2)

    transport = httpx.MockTransport(handler)

    with APIWatch(config=config, transport=transport) as watch:
        result = watch.check("https://example.com/api")

    assert result.status_code == 200
    assert result.is_success is True
    assert attempts == 2


def test_does_not_retry_client_error(monkeypatch):
    """Do not retry HTTP 404 responses."""

    attempts = 0

    def handler(request):
        nonlocal attempts
        attempts += 1

        return httpx.Response(404, request=request)

    monkeypatch.setattr(
        "apiwatch.client.time.sleep",
        lambda delay: None,
    )

    config = APIWatchConfig(max_retries=3)

    transport = httpx.MockTransport(handler)

    with APIWatch(config=config, transport=transport) as watch:
        result = watch.check("https://example.com/missing")

    assert result.status_code == 404
    assert result.is_success is False
    assert attempts == 1


def test_retry_exhaustion(monkeypatch):
    """Return the final server error after exhausting retries."""

    attempts = 0
    delays = []

    def handler(request):
        nonlocal attempts
        attempts += 1

        return httpx.Response(503, request=request)

    monkeypatch.setattr(
        "apiwatch.client.time.sleep",
        delays.append,
    )

    config = APIWatchConfig(
        max_retries=3,
        retry_delay=1,
        backoff_factor=2,
    )

    transport = httpx.MockTransport(handler)

    with APIWatch(config=config, transport=transport) as watch:
        result = watch.check("https://example.com/api")

    assert result.status_code == 503
    assert result.is_success is False
    assert attempts == 4
    assert delays == [1, 2, 4]


def test_retries_network_error_then_succeeds(monkeypatch):
    """Retry a network error and eventually receive a successful response."""

    attempts = 0

    def handler(request):
        nonlocal attempts
        attempts += 1

        if attempts == 1:
            raise httpx.ConnectError(
                "Connection failed",
                request=request,
            )

        return httpx.Response(200, request=request)

    monkeypatch.setattr(
        "apiwatch.client.time.sleep",
        lambda delay: None,
    )

    config = APIWatchConfig(max_retries=2)

    transport = httpx.MockTransport(handler)

    with APIWatch(config=config, transport=transport) as watch:
        result = watch.check("https://example.com/api")

    assert result.status_code == 200
    assert result.is_success is True
    assert result.error is None
    assert attempts == 2


def test_network_error_after_all_retries(monkeypatch):
    """Return an error when every network attempt fails."""

    attempts = 0

    def handler(request):
        nonlocal attempts
        attempts += 1

        raise httpx.ConnectError(
            "Connection failed",
            request=request,
        )

    monkeypatch.setattr(
        "apiwatch.client.time.sleep",
        lambda delay: None,
    )

    config = APIWatchConfig(max_retries=2)

    transport = httpx.MockTransport(handler)

    with APIWatch(config=config, transport=transport) as watch:
        result = watch.check("https://example.com/api")

    assert result.status_code is None
    assert result.is_success is False
    assert result.error is not None
    assert attempts == 3


def test_retries_disabled(monkeypatch):
    """Make only one request when retries are disabled."""

    attempts = 0

    def handler(request):
        nonlocal attempts
        attempts += 1

        return httpx.Response(503, request=request)

    monkeypatch.setattr(
        "apiwatch.client.time.sleep",
        lambda delay: None,
    )

    config = APIWatchConfig(max_retries=0)

    transport = httpx.MockTransport(handler)

    with APIWatch(config=config, transport=transport) as watch:
        result = watch.check("https://example.com/api")

    assert result.status_code == 503
    assert result.is_success is False
    assert attempts == 1
