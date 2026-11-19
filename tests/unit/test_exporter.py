import csv
import json

import pytest

from apiwatch.exporter import APIExporter
from apiwatch.models import APIResult


@pytest.fixture
def sample_results():

    return [
        APIResult(
            url="https://example.com/api/users",
            method="GET",
            status_code=200,
            response_time=0.45,
            is_success=True,
            response_size=120,
            is_valid=True,
            validation_errors=[],
        ),
        APIResult(
            url="https://example.com/api/users",
            method="POST",
            status_code=400,
            response_time=0.72,
            is_success=False,
            response_size=80,
            error="Bad Request",
            is_valid=False,
            validation_errors=[
                "email: invalid format",
            ],
        ),
    ]


def test_export_json(
    sample_results,
    tmp_path,
):

    file_path = tmp_path / "report.json"

    APIExporter.export(
        sample_results,
        str(file_path),
    )

    assert file_path.exists()

    data = json.loads(
        file_path.read_text(
            encoding="utf-8"
        )
    )

    assert len(data) == 2
    assert data[0]["status_code"] == 200
    assert data[0]["is_valid"] is True
    assert data[1]["validation_errors"] == [
        "email: invalid format"
    ]


def test_export_csv(
    sample_results,
    tmp_path,
):

    file_path = tmp_path / "report.csv"

    APIExporter.export(
        sample_results,
        str(file_path),
    )

    assert file_path.exists()

    with file_path.open(
        encoding="utf-8",
        newline="",
    ) as file:

        rows = list(
            csv.DictReader(file)
        )

    assert len(rows) == 2
    assert rows[0]["status_code"] == "200"
    assert rows[0]["is_success"] == "True"


def test_export_json_explicit_format(
    sample_results,
    tmp_path,
):

    file_path = tmp_path / "report.data"

    APIExporter.export(
        sample_results,
        str(file_path),
        format="json",
    )

    assert file_path.exists()

    data = json.loads(
        file_path.read_text(
            encoding="utf-8"
        )
    )

    assert len(data) == 2


def test_export_csv_explicit_format(
    sample_results,
    tmp_path,
):

    file_path = tmp_path / "report.data"

    APIExporter.export(
        sample_results,
        str(file_path),
        format="csv",
    )

    assert file_path.exists()


def test_unsupported_format(
    sample_results,
    tmp_path,
):

    file_path = tmp_path / "report.xml"

    with pytest.raises(ValueError):

        APIExporter.export(
            sample_results,
            str(file_path),
        )


def test_creates_parent_directories(
    sample_results,
    tmp_path,
):

    file_path = (
        tmp_path
        / "reports"
        / "monthly"
        / "report.json"
    )

    APIExporter.export(
        sample_results,
        str(file_path),
    )

    assert file_path.exists()


def test_export_empty_results(
    tmp_path,
):

    file_path = tmp_path / "empty.json"

    APIExporter.export(
        [],
        str(file_path),
    )

    data = json.loads(
        file_path.read_text(
            encoding="utf-8"
        )
    )

    assert data == []