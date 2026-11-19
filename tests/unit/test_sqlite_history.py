
from apiwatch.history import APIHistory
from apiwatch.models import APIResult


def create_result(
    url="https://example.com/api",
    success=True,
    response_time=0.2,
    status_code=200,
):
    return APIResult(
        url=url,
        method="GET",
        status_code=status_code,
        response_time=response_time,
        is_success=success,
        response_size=100,
    )


def test_sqlite_stores_results(tmp_path):
    database = tmp_path / "history.db"

    history = APIHistory(str(database))

    result = create_result()

    history.add(result)

    stored = history.get_history()

    assert len(stored) == 1
    assert stored[0].url == result.url
    assert stored[0].status_code == 200

    history.close()


def test_sqlite_persistence_after_reopening(tmp_path):
    database = tmp_path / "history.db"

    history = APIHistory(str(database))

    history.add(
        create_result(
            url="https://example.com/users"
        )
    )

    history.close()

    # Open the same database again
    history = APIHistory(str(database))

    stored = history.get_history()

    assert len(stored) == 1
    assert stored[0].url == "https://example.com/users"

    history.close()


def test_sqlite_filter_by_url(tmp_path):
    database = tmp_path / "history.db"

    history = APIHistory(str(database))

    history.add(
        create_result(
            url="https://example.com/users"
        )
    )

    history.add(
        create_result(
            url="https://example.com/products"
        )
    )

    history.add(
        create_result(
            url="https://example.com/users"
        )
    )

    filtered = history.get_history(
        "https://example.com/users"
    )

    assert len(filtered) == 2

    history.close()


def test_sqlite_statistics(tmp_path):
    database = tmp_path / "history.db"

    history = APIHistory(str(database))

    history.add(
        create_result(
            success=True,
            response_time=0.2,
        )
    )

    history.add(
        create_result(
            success=False,
            response_time=0.4,
            status_code=500,
        )
    )

    stats = history.get_stats()

    assert stats["total_checks"] == 2
    assert stats["successful_checks"] == 1
    assert stats["failed_checks"] == 1
    assert stats["success_rate"] == 50.0
    assert stats["average_response_time"] == 0.3

    history.close()


def test_sqlite_clear_history(tmp_path):
    database = tmp_path / "history.db"

    history = APIHistory(str(database))

    history.add(create_result())
    history.add(create_result())

    assert len(history) == 2

    history.clear()

    assert len(history) == 0
    assert history.get_history() == []

    history.close()


def test_sqlite_empty_database(tmp_path):
    database = tmp_path / "history.db"

    history = APIHistory(str(database))

    assert len(history) == 0
    assert history.get_history() == []

    stats = history.get_stats()

    assert stats["total_checks"] == 0
    assert stats["success_rate"] == 0.0

    history.close()
