
from unittest.mock import patch

from apiwatch.cli import (
    check_api,
    clear_history,
    print_result,
    show_history,
    show_stats,
)


def test_print_result_success(capsys):
    from apiwatch.models import APIResult

    result = APIResult(
        url="https://example.com",
        method="GET",
        status_code=200,
        response_time=0.25,
        is_success=True,
        response_size=100,
    )

    print_result(result)

    captured = capsys.readouterr()

    assert "https://example.com" in captured.out
    assert "200" in captured.out
    assert "HEALTHY" in captured.out


def test_check_api_success():
    with patch("apiwatch.cli.APIWatch") as mock_watch_class:
        mock_watch = mock_watch_class.return_value.__enter__.return_value

        from apiwatch.models import APIResult

        mock_watch.check.return_value = APIResult(
            url="https://example.com",
            method="GET",
            status_code=200,
            response_time=0.1,
            is_success=True,
            response_size=50,
        )

        result = check_api("https://example.com")

        assert result == 0
        mock_watch.check.assert_called_once_with(
            "https://example.com",
            method="GET",
        )


def test_check_api_failure():
    with patch("apiwatch.cli.APIWatch") as mock_watch_class:
        mock_watch = mock_watch_class.return_value.__enter__.return_value

        from apiwatch.models import APIResult

        mock_watch.check.return_value = APIResult(
            url="https://example.com",
            method="GET",
            status_code=500,
            response_time=0.1,
            is_success=False,
        )

        result = check_api("https://example.com")

        assert result == 1


def test_show_history_empty(capsys):
    with patch("apiwatch.cli.APIWatch") as mock_watch_class:
        mock_watch = mock_watch_class.return_value.__enter__.return_value
        mock_watch.get_history.return_value = []

        result = show_history()

        captured = capsys.readouterr()

        assert result == 0
        assert "No monitoring history found" in captured.out


def test_show_stats_empty(capsys):
    with patch("apiwatch.cli.APIWatch") as mock_watch_class:
        mock_watch = mock_watch_class.return_value.__enter__.return_value

        mock_watch.get_stats.return_value = {
            "total_checks": 0,
            "successful_checks": 0,
            "failed_checks": 0,
            "success_rate": 0.0,
            "average_response_time": 0.0,
            "fastest_response_time": 0.0,
            "slowest_response_time": 0.0,
        }

        result = show_stats()

        captured = capsys.readouterr()

        assert result == 0
        assert "No monitoring data available" in captured.out


def test_clear_history(capsys):
    with patch("apiwatch.cli.APIWatch") as mock_watch_class:
        mock_watch = mock_watch_class.return_value.__enter__.return_value

        result = clear_history()

        captured = capsys.readouterr()

        assert result == 0
        mock_watch.clear_history.assert_called_once()
        assert "cleared successfully" in captured.out
