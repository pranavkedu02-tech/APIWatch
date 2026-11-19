
import httpx

from apiwatch import APIWatch, APIWatchConfig


def test_successful_request_is_recorded():
    def handler(request):
        return httpx.Response(200, request=request)

    config = APIWatchConfig(max_retries=0)

    with APIWatch(
        config=config,
        transport=httpx.MockTransport(handler),
    ) as watch:

        result = watch.check("https://example.com/api")

        history = watch.get_history()

        assert result.is_success is True
        assert len(history) == 1
        assert history[0] == result


def test_failed_request_is_recorded():
    def handler(request):
        return httpx.Response(500, request=request)

    config = APIWatchConfig(max_retries=0)

    with APIWatch(
        config=config,
        transport=httpx.MockTransport(handler),
    ) as watch:

        result = watch.check("https://example.com/api")

        history = watch.get_history()

        assert result.is_success is False
        assert len(history) == 1
        assert history[0] == result


def test_history_records_multiple_requests():
    def handler(request):
        if "/users" in request.url.path:
            return httpx.Response(200, request=request)

        return httpx.Response(404, request=request)

    config = APIWatchConfig(max_retries=0)

    with APIWatch(
        config=config,
        transport=httpx.MockTransport(handler),
    ) as watch:

        watch.check("https://example.com/users")
        watch.check("https://example.com/products")

        history = watch.get_history()

        assert len(history) == 2


def test_get_history_filtered_by_url():
    def handler(request):
        return httpx.Response(200, request=request)

    config = APIWatchConfig(max_retries=0)

    with APIWatch(
        config=config,
        transport=httpx.MockTransport(handler),
    ) as watch:

        watch.check("https://example.com/users")
        watch.check("https://example.com/products")
        watch.check("https://example.com/users")

        filtered = watch.get_history(
            "https://example.com/users"
        )

        assert len(filtered) == 2


def test_get_stats_from_apiwatch():
    def handler(request):
        if "/failed" in request.url.path:
            return httpx.Response(500, request=request)

        return httpx.Response(200, request=request)

    config = APIWatchConfig(max_retries=0)

    with APIWatch(
        config=config,
        transport=httpx.MockTransport(handler),
    ) as watch:

        watch.check("https://example.com/success")
        watch.check("https://example.com/success")
        watch.check("https://example.com/failed")

        stats = watch.get_stats()

        assert stats["total_checks"] == 3
        assert stats["successful_checks"] == 2
        assert stats["failed_checks"] == 1
        assert stats["success_rate"] == 66.67


def test_get_stats_filtered_by_url():
    def handler(request):
        if "/users" in request.url.path:
            return httpx.Response(200, request=request)

        return httpx.Response(500, request=request)

    config = APIWatchConfig(max_retries=0)

    with APIWatch(
        config=config,
        transport=httpx.MockTransport(handler),
    ) as watch:

        watch.check("https://example.com/users")
        watch.check("https://example.com/users")
        watch.check("https://example.com/products")

        stats = watch.get_stats(
            "https://example.com/users"
        )

        assert stats["total_checks"] == 2
        assert stats["successful_checks"] == 2
        assert stats["failed_checks"] == 0
        assert stats["success_rate"] == 100.0


def test_clear_history_from_apiwatch():
    def handler(request):
        return httpx.Response(200, request=request)

    config = APIWatchConfig(max_retries=0)

    with APIWatch(
        config=config,
        transport=httpx.MockTransport(handler),
    ) as watch:

        watch.check("https://example.com/api")
        watch.check("https://example.com/api")

        assert len(watch.get_history()) == 2

        watch.clear_history()

        assert len(watch.get_history()) == 0
        assert watch.get_stats()["total_checks"] == 0


def test_retry_exhaustion_is_recorded():
    def handler(request):
        return httpx.Response(503, request=request)

    config = APIWatchConfig(
        max_retries=2,
        retry_delay=0,
    )

    with APIWatch(
        config=config,
        transport=httpx.MockTransport(handler),
    ) as watch:

        result = watch.check("https://example.com/api")

        history = watch.get_history()

        assert result.is_success is False
        assert result.status_code == 503
        assert len(history) == 1
        assert history[0].status_code == 503
