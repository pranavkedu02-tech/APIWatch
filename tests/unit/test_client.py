
import httpx

from apiwatch import APIWatch


def test_successful_api_check():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"message": "API is working"},
        )

    with APIWatch(transport=httpx.MockTransport(handler)) as watcher:
        result = watcher.check("https://example.com/api")

    assert result.status_code == 200
    assert result.is_success is True
    assert result.error is None
    assert result.response_time >= 0
    assert result.response_size is not None
    assert result.method == "GET"


def test_server_error_is_unsuccessful():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503, json={"error": "Unavailable"})

    with APIWatch(transport=httpx.MockTransport(handler)) as watcher:
        result = watcher.check("https://example.com/api")

    assert result.status_code == 503
    assert result.is_success is False
    assert result.error is None


def test_request_error_is_returned_in_result():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError(
            "Connection failed",
            request=request,
        )

    with APIWatch(transport=httpx.MockTransport(handler)) as watcher:
        result = watcher.check("https://example.com/api")

    assert result.status_code is None
    assert result.is_success is False
    assert "Connection failed" in result.error
