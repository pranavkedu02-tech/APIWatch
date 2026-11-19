
from apiwatch.models import APIResult


class APIHistory:
    """Store and analyze API monitoring results."""

    def __init__(self):
        self._results: list[APIResult] = []

    def add(self, result: APIResult) -> None:
        """Add an API monitoring result to history."""
        self._results.append(result)

    def get_history(self, url: str | None = None) -> list[APIResult]:
        """Return monitoring history, optionally filtered by URL."""

        if url is None:
            return self._results.copy()

        return [
            result
            for result in self._results
            if result.url == url
        ]

    def clear(self) -> None:
        """Clear all monitoring history."""
        self._results.clear()

    def get_stats(self, url: str | None = None) -> dict:
        """Calculate monitoring statistics."""

        results = self.get_history(url)

        total_checks = len(results)

        successful_checks = sum(
            1 for result in results if result.is_success
        )

        failed_checks = total_checks - successful_checks

        response_times = [
            result.response_time
            for result in results
        ]

        average_response_time = (
            sum(response_times) / len(response_times)
            if response_times
            else 0.0
        )

        fastest_response_time = (
            min(response_times)
            if response_times
            else 0.0
        )

        slowest_response_time = (
            max(response_times)
            if response_times
            else 0.0
        )

        success_rate = (
            (successful_checks / total_checks) * 100
            if total_checks
            else 0.0
        )

        return {
            "total_checks": total_checks,
            "successful_checks": successful_checks,
            "failed_checks": failed_checks,
            "success_rate": round(success_rate, 2),
            "average_response_time": round(
                average_response_time, 4
            ),
            "fastest_response_time": round(
                fastest_response_time, 4
            ),
            "slowest_response_time": round(
                slowest_response_time, 4
            ),
        }

    def __len__(self) -> int:
        """Return the number of stored monitoring results."""
        return len(self._results)
