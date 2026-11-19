
import sqlite3
from pathlib import Path

from apiwatch.models import APIResult


class APIHistory:
    """Store and analyze API monitoring results."""

    def __init__(
        self,
        database_path: str | None = None,
    ):
        self._results: list[APIResult] = []
        self._database_path = database_path
        self._connection: sqlite3.Connection | None = None

        if database_path is not None:
            if database_path != ":memory:":
                Path(database_path).parent.mkdir(
                    parents=True,
                    exist_ok=True,
                )

            self._connection = sqlite3.connect(
                database_path
            )

            self._connection.row_factory = sqlite3.Row

            self._create_table()

    def _create_table(self) -> None:
        """Create monitoring history table if it doesn't exist."""

        if self._connection is None:
            return

        self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS api_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                method TEXT NOT NULL,
                status_code INTEGER,
                response_time REAL NOT NULL,
                is_success INTEGER NOT NULL,
                response_size INTEGER,
                error TEXT,
                timestamp TEXT NOT NULL
            )
            """
        )

        self._connection.commit()

    def add(self, result: APIResult) -> None:
        """Add an API monitoring result."""

        if self._connection is None:
            self._results.append(result)
            return

        self._connection.execute(
            """
            INSERT INTO api_history (
                url,
                method,
                status_code,
                response_time,
                is_success,
                response_size,
                error,
                timestamp
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                result.url,
                result.method,
                result.status_code,
                result.response_time,
                int(result.is_success),
                result.response_size,
                result.error,
                result.timestamp.isoformat(),
            ),
        )

        self._connection.commit()

    def get_history(
        self,
        url: str | None = None,
    ) -> list[APIResult]:
        """Return monitoring history, optionally filtered by URL."""

        if self._connection is None:

            if url is None:
                return self._results.copy()

            return [
                result
                for result in self._results
                if result.url == url
            ]

        if url is None:
            cursor = self._connection.execute(
                """
                SELECT *
                FROM api_history
                ORDER BY id ASC
                """
            )
        else:
            cursor = self._connection.execute(
                """
                SELECT *
                FROM api_history
                WHERE url = ?
                ORDER BY id ASC
                """,
                (url,),
            )

        rows = cursor.fetchall()

        return [
            APIResult(
                url=row["url"],
                method=row["method"],
                status_code=row["status_code"],
                response_time=row["response_time"],
                is_success=bool(row["is_success"]),
                response_size=row["response_size"],
                error=row["error"],
                timestamp=row["timestamp"],
            )
            for row in rows
        ]

    def clear(self) -> None:
        """Clear all stored monitoring history."""

        if self._connection is None:
            self._results.clear()
            return

        self._connection.execute(
            "DELETE FROM api_history"
        )

        self._connection.commit()

    def get_stats(
        self,
        url: str | None = None,
    ) -> dict:
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

    def close(self) -> None:
        """Close SQLite connection."""

        if self._connection is not None:
            self._connection.close()
            self._connection = None

    def __len__(self) -> int:
        """Return the number of stored monitoring results."""

        if self._connection is None:
            return len(self._results)

        cursor = self._connection.execute(
            "SELECT COUNT(*) FROM api_history"
        )

        return cursor.fetchone()[0]
