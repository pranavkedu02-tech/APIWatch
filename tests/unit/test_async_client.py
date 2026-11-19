
import asyncio

import httpx

from apiwatch import APIWatchConfig, AsyncAPIWatch


class MockAsyncTransport(httpx.AsyncBaseTransport):
    """Custom async transport for testing."""

    def __init__(self, handler):
        self.handler = handler

    async def handle_async_request(self, request):
        return await self.handler(request)


def test_async_successful_request():
    async def handler(request):
        return httpx.Response(200, request=request)

    async def run_test():
        config = APIWatchConfig(max_retries=0)

        async with AsyncAPIWatch(
            config=config,
            transport=MockAsyncTransport(handler),
        ) as watch:

            result = await watch.check(
                "https://example.com/api"
            )

            assert result.is_success is True
            assert result.status_code == 200
            assert len(watch.get_history()) == 1

    asyncio.run(run_test())


def test_async_failed_request():
    async def handler(request):
        return httpx.Response(500, request=request)

    async def run_test():
        config = APIWatchConfig(max_retries=0)

        async with AsyncAPIWatch(
            config=config,
            transport=MockAsyncTransport(handler),
        ) as watch:

            result = await watch.check(
                "https://example.com/api"
            )

            assert result.is_success is False
            assert result.status_code == 500
            assert len(watch.get_history()) == 1

    asyncio.run(run_test())


def test_async_retry_success():
    request_count = 0

    async def handler(request):
        nonlocal request_count

        request_count += 1

        if request_count == 1:
            return httpx.Response(503, request=request)

        return httpx.Response(200, request=request)

    async def run_test():
        config = APIWatchConfig(
            max_retries=2,
            retry_delay=0,
        )

        async with AsyncAPIWatch(
            config=config,
            transport=MockAsyncTransport(handler),
        ) as watch:

            result = await watch.check(
                "https://example.com/api"
            )

            assert result.is_success is True
            assert result.status_code == 200
            assert request_count == 2

            # One monitoring record per logical check
            assert len(watch.get_history()) == 1

    asyncio.run(run_test())


def test_async_check_many():
    async def handler(request):
        return httpx.Response(200, request=request)

    async def run_test():
        config = APIWatchConfig(max_retries=0)

        urls = [
            "https://example.com/users",
            "https://example.com/products",
            "https://example.com/orders",
        ]

        async with AsyncAPIWatch(
            config=config,
            transport=MockAsyncTransport(handler),
        ) as watch:

            results = await watch.check_many(urls)

            assert len(results) == 3
            assert all(
                result.is_success
                for result in results
            )

            assert len(watch.get_history()) == 3

    asyncio.run(run_test())


def test_async_persistent_history(tmp_path):
    database = tmp_path / "async_history.db"

    async def handler(request):
        return httpx.Response(200, request=request)

    async def run_test():
        config = APIWatchConfig(max_retries=0)

        async with AsyncAPIWatch(
            config=config,
            transport=MockAsyncTransport(handler),
            history_db=str(database),
        ) as watch:

            result = await watch.check(
                "https://example.com/api"
            )

            assert result.is_success is True
            assert len(watch.get_history()) == 1

        async with AsyncAPIWatch(
            history_db=str(database),
        ) as watch:

            history = watch.get_history()

            assert len(history) == 1
            assert history[0].url == "https://example.com/api"

    asyncio.run(run_test())


def test_async_clear_history():
    async def handler(request):
        return httpx.Response(200, request=request)

    async def run_test():
        config = APIWatchConfig(max_retries=0)

        async with AsyncAPIWatch(
            config=config,
            transport=MockAsyncTransport(handler),
        ) as watch:

            await watch.check(
                "https://example.com/api"
            )

            assert len(watch.get_history()) == 1

            watch.clear_history()

            assert len(watch.get_history()) == 0

    asyncio.run(run_test())
