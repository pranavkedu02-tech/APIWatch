import csv
import json

import httpx

from apiwatch import APIWatch


def test_export_history_json(tmp_path):

    def handler(request):

        return httpx.Response(
            200,
            json={
                "message": "success",
            },
        )

    transport = httpx.MockTransport(handler)

    file_path = tmp_path / "report.json"

    with APIWatch(
        transport=transport,
    ) as watch:

        watch.check(
            "https://example.com/api/1"
        )

        watch.check(
            "https://example.com/api/2"
        )

        watch.export_history(
            str(file_path),
        )

    data = json.loads(
        file_path.read_text(
            encoding="utf-8"
        )
    )

    assert len(data) == 2


def test_export_history_csv(tmp_path):

    def handler(request):

        return httpx.Response(
            200,
            json={
                "message": "success",
            },
        )

    transport = httpx.MockTransport(handler)

    file_path = tmp_path / "report.csv"

    with APIWatch(
        transport=transport,
    ) as watch:

        watch.check(
            "https://example.com/api/1"
        )

        watch.export_history(
            str(file_path),
            format="csv",
        )

    with file_path.open(
        encoding="utf-8",
        newline="",
    ) as file:

        rows = list(
            csv.DictReader(file)
        )

    assert len(rows) == 1


def test_export_filtered_history(tmp_path):

    def handler(request):

        return httpx.Response(
            200,
            json={
                "message": "success",
            },
        )

    transport = httpx.MockTransport(handler)

    file_path = tmp_path / "filtered.json"

    with APIWatch(
        transport=transport,
    ) as watch:

        watch.check(
            "https://example.com/api/1"
        )

        watch.check(
            "https://example.com/api/2"
        )

        watch.export_history(
            str(file_path),
            url="https://example.com/api/1",
        )

    data = json.loads(
        file_path.read_text(
            encoding="utf-8"
        )
    )

    assert len(data) == 1

    assert data[0]["url"] == (
        "https://example.com/api/1"
    )


def test_export_sqlite_history(tmp_path):

    def handler(request):

        return httpx.Response(
            200,
            json={
                "message": "success",
            },
        )

    transport = httpx.MockTransport(handler)

    database_path = (
        tmp_path
        / "history.db"
    )

    file_path = (
        tmp_path
        / "report.json"
    )

    with APIWatch(
        transport=transport,
        history_db=str(database_path),
    ) as watch:

        watch.check(
            "https://example.com/api"
        )

        watch.export_history(
            str(file_path),
        )

    data = json.loads(
        file_path.read_text(
            encoding="utf-8"
        )
    )

    assert len(data) == 1