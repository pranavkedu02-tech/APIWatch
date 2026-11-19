import csv
import json
from pathlib import Path
from typing import Literal

from apiwatch.models import APIResult

ExportFormat = Literal["json", "csv"]


class APIExporter:
    """Export API monitoring results to JSON or CSV."""

    @staticmethod
    def export(
        results: list[APIResult],
        file_path: str,
        format: ExportFormat | None = None,
    ) -> None:
        """Export API results to JSON or CSV."""

        path = Path(file_path)

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        export_format = (
            format.lower()
            if format
            else path.suffix.lower().lstrip(".")
        )

        if export_format not in {"json", "csv"}:

            raise ValueError(
                "Unsupported export format. "
                "Supported formats: json, csv"
            )

        if export_format == "json":

            APIExporter._export_json(
                results,
                path,
            )

        elif export_format == "csv":

            APIExporter._export_csv(
                results,
                path,
            )

    @staticmethod
    def _export_json(
        results: list[APIResult],
        path: Path,
    ) -> None:
        """Export results to JSON."""

        data = [
            result.model_dump(mode="json")
            for result in results
        ]

        with path.open(
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False,
            )

    @staticmethod
    def _export_csv(
        results: list[APIResult],
        path: Path,
    ) -> None:
        """Export results to CSV."""

        fieldnames = [
            "url",
            "method",
            "status_code",
            "response_time",
            "is_success",
            "response_size",
            "error",
            "is_valid",
            "validation_errors",
            "timestamp",
        ]

        with path.open(
            "w",
            newline="",
            encoding="utf-8",
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=fieldnames,
            )

            writer.writeheader()

            for result in results:

                row = result.model_dump(
                    mode="json"
                )

                row["validation_errors"] = json.dumps(
                    row["validation_errors"]
                )

                writer.writerow(row)