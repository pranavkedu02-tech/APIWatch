
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


def test_add_result_to_history():
    history = APIHistory()

    result = create_result()

    history.add(result)

    assert len(history) == 1
    assert history.get_history()[0] == result


def test_get_history_by_url():
    history = APIHistory()

    result1 = create_result(
        url="https://example.com/users"
    )

    result2 = create_result(
        url="https://example.com/products"
    )

    history.add(result1)
    history.add(result2)

    filtered = history.get_history(
        "https://example.com/users"
    )

    assert len(filtered) == 1
    assert filtered[0].url == "https://example.com/users"


def test_get_statistics():
    history = APIHistory()

    history.add(
        create_result(
            success=True,
            response_time=0.2,
        )
    )

    history.add(
        create_result(
            success=True,
            response_time=0.4,
        )
    )

    history.add(
        create_result(
            success=False,
            response_time=0.6,
            status_code=500,
        )
    )

    stats = history.get_stats()

    assert stats["total_checks"] == 3
    assert stats["successful_checks"] == 2
    assert stats["failed_checks"] == 1
    assert stats["success_rate"] == 66.67
    assert stats["average_response_time"] == 0.4
    assert stats["fastest_response_time"] == 0.2
    assert stats["slowest_response_time"] == 0.6


def test_empty_history_statistics():
    history = APIHistory()

    stats = history.get_stats()

    assert stats["total_checks"] == 0
    assert stats["successful_checks"] == 0
    assert stats["failed_checks"] == 0
    assert stats["success_rate"] == 0.0
    assert stats["average_response_time"] == 0.0
    assert stats["fastest_response_time"] == 0.0
    assert stats["slowest_response_time"] == 0.0


def test_clear_history():
    history = APIHistory()

    history.add(create_result())
    history.add(create_result())

    assert len(history) == 2

    history.clear()

    assert len(history) == 0
    assert history.get_history() == []


def test_statistics_filtered_by_url():
    history = APIHistory()

    history.add(
        create_result(
            url="https://example.com/users",
            success=True,
            response_time=0.2,
        )
    )

    history.add(
        create_result(
            url="https://example.com/users",
            success=False,
            response_time=0.4,
            status_code=500,
        )
    )

    history.add(
        create_result(
            url="https://example.com/products",
            success=True,
            response_time=0.8,
        )
    )

    stats = history.get_stats(
        "https://example.com/users"
    )

    assert stats["total_checks"] == 2
    assert stats["successful_checks"] == 1
    assert stats["failed_checks"] == 1
    assert stats["success_rate"] == 50.0
    assert stats["average_response_time"] == 0.3
