
import httpx

from apiwatch import APIWatch, APIWatchConfig


def test_apiwatch_persists_history(tmp_path):
    database = tmp_path / "apiwatch.db"

    def handler(request):
        return httpx.Response(200, request=request)

    config = APIWatchConfig(max_retries=0)

    with APIWatch(
        config=config,
        transport=httpx.MockTransport(handler),
        history_db=str(database),
    ) as watch:

        result = watch.check(
            "https://example.com/users"
        )

        assert result.is_success is True
        assert len(watch.get_history()) == 1

    # Reopen the same database
    with APIWatch(
        history_db=str(database),
    ) as watch:

        history = watch.get_history()

        assert len(history) == 1
        assert history[0].url == "https://example.com/users"
        assert history[0].is_success is True


def test_apiwatch_persistent_statistics(tmp_path):
    database = tmp_path / "apiwatch.db"

    def handler(request):
        if "/failed" in request.url.path:
            return httpx.Response(500, request=request)

        return httpx.Response(200, request=request)

    config = APIWatchConfig(max_retries=0)

    with APIWatch(
        config=config,
        transport=httpx.MockTransport(handler),
        history_db=str(database),
    ) as watch:

        watch.check("https://example.com/success")
        watch.check("https://example.com/failed")

    # Statistics should survive reopening
    with APIWatch(
        history_db=str(database),
    ) as watch:

        stats = watch.get_stats()

        assert stats["total_checks"] == 2
        assert stats["successful_checks"] == 1
        assert stats["failed_checks"] == 1
        assert stats["success_rate"] == 50.0


def test_apiwatch_persistent_url_filter(tmp_path):
    database = tmp_path / "apiwatch.db"

    def handler(request):
        return httpx.Response(200, request=request)

    config = APIWatchConfig(max_retries=0)

    with APIWatch(
        config=config,
        transport=httpx.MockTransport(handler),
        history_db=str(database),
    ) as watch:

        watch.check("https://example.com/users")
        watch.check("https://example.com/products")
        watch.check("https://example.com/users")

    with APIWatch(
        history_db=str(database),
    ) as watch:

        filtered = watch.get_history(
            "https://example.com/users"
        )

        assert len(filtered) == 2


def test_apiwatch_persistent_clear_history(tmp_path):
    database = tmp_path / "apiwatch.db"

    def handler(request):
        return httpx.Response(200, request=request)

    config = APIWatchConfig(max_retries=0)

    with APIWatch(
        config=config,
        transport=httpx.MockTransport(handler),
        history_db=str(database),
    ) as watch:

        watch.check("https://example.com/api")
        watch.clear_history()

        assert len(watch.get_history()) == 0

    # Verify deletion is persistent
    with APIWatch(
        history_db=str(database),
    ) as watch:

        assert len(watch.get_history()) == 0
