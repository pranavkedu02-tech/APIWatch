
import httpx

from apiwatch import APIWatch, APIWatchConfig


def test_logs_successful_request(caplog):
    """Log successful API requests."""

    def handler(request):
        return httpx.Response(200, request=request)

    config = APIWatchConfig(
        max_retries=0,
        log_level="INFO",
    )

    transport = httpx.MockTransport(handler)

    with APIWatch(config=config, transport=transport) as watch:
        result = watch.check("https://example.com/api")

    assert result.is_success is True

    assert "Checking API" in caplog.text
    assert "API check successful" in caplog.text


def test_logs_failed_request(caplog):
    """Log unsuccessful API responses."""

    def handler(request):
        return httpx.Response(404, request=request)

    config = APIWatchConfig(
        max_retries=0,
        log_level="INFO",
    )

    transport = httpx.MockTransport(handler)

    with APIWatch(config=config, transport=transport) as watch:
        result = watch.check("https://example.com/missing")

    assert result.is_success is False
    assert result.status_code == 404

    assert "API check failed" in caplog.text


def test_logs_retry_attempt(monkeypatch, caplog):
    """Log retry attempts."""

    attempts = 0

    def handler(request):
        nonlocal attempts
        attempts += 1

        if attempts == 1:
            return httpx.Response(503, request=request)

        return httpx.Response(200, request=request)

    monkeypatch.setattr(
        "apiwatch.client.time.sleep",
        lambda delay: None,
    )

    config = APIWatchConfig(
        max_retries=1,
        log_level="WARNING",
    )

    transport = httpx.MockTransport(handler)

    with APIWatch(config=config, transport=transport) as watch:
        result = watch.check("https://example.com/api")

    assert result.status_code == 200
    assert "Retrying attempt" in caplog.text


def test_file_logging(tmp_path):
    """Save logs to a file."""

    log_file = tmp_path / "apiwatch.log"

    def handler(request):
        return httpx.Response(200, request=request)

    config = APIWatchConfig(
        max_retries=0,
        log_level="INFO",
        log_file=str(log_file),
    )

    transport = httpx.MockTransport(handler)

    with APIWatch(config=config, transport=transport) as watch:
        watch.check("https://example.com/api")

    assert log_file.exists()

    content = log_file.read_text(encoding="utf-8")

    assert "Checking API" in content
    assert "API check successful" in content


def test_debug_logging_configuration():
    """Accept DEBUG as a valid logging level."""

    config = APIWatchConfig(
        log_level="DEBUG",
    )

    assert config.log_level == "DEBUG"


def test_invalid_logging_level():
    """Reject invalid logging levels."""

    import pytest

    with pytest.raises(ValueError):
        APIWatchConfig(log_level="INVALID")
