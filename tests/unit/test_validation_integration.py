import httpx

from apiwatch import APIWatch

VALID_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "name": {"type": "string"},
        "email": {
            "type": "string",
            "format": "email",
        },
    },
    "required": ["id", "name", "email"],
}


def test_valid_response_with_schema():
    def handler(request):
        return httpx.Response(
            200,
            json={
                "id": 1,
                "name": "Pranav",
                "email": "pranav@example.com",
            },
        )

    transport = httpx.MockTransport(handler)

    with APIWatch(transport=transport) as watch:
        result = watch.check(
            "https://example.com/api/user",
            schema=VALID_SCHEMA,
        )

    assert result.is_success is True
    assert result.is_valid is True
    assert result.validation_errors == []


def test_invalid_response_with_schema():
    def handler(request):
        return httpx.Response(
            200,
            json={
                "id": "wrong",
                "name": "Pranav",
                "email": "invalid-email",
            },
        )

    transport = httpx.MockTransport(handler)

    with APIWatch(transport=transport) as watch:
        result = watch.check(
            "https://example.com/api/user",
            schema=VALID_SCHEMA,
        )

    assert result.is_success is True
    assert result.is_valid is False
    assert len(result.validation_errors) == 2


def test_missing_required_fields():
    def handler(request):
        return httpx.Response(
            200,
            json={
                "id": 1,
            },
        )

    transport = httpx.MockTransport(handler)

    with APIWatch(transport=transport) as watch:
        result = watch.check(
            "https://example.com/api/user",
            schema=VALID_SCHEMA,
        )

    assert result.is_valid is False
    assert len(result.validation_errors) == 2


def test_validation_not_performed_without_schema():
    def handler(request):
        return httpx.Response(
            200,
            json={
                "id": 1,
                "name": "Pranav",
            },
        )

    transport = httpx.MockTransport(handler)

    with APIWatch(transport=transport) as watch:
        result = watch.check(
            "https://example.com/api/user",
        )

    assert result.is_valid is None
    assert result.validation_errors == []


def test_non_json_response_with_schema():
    def handler(request):
        return httpx.Response(
            200,
            text="This is not JSON",
        )

    transport = httpx.MockTransport(handler)

    with APIWatch(transport=transport) as watch:
        result = watch.check(
            "https://example.com/api/user",
            schema=VALID_SCHEMA,
        )

    assert result.is_success is True
    assert result.is_valid is False
    assert len(result.validation_errors) == 1
    assert "not valid JSON" in result.validation_errors[0]


def test_validation_result_is_stored_in_history():
    def handler(request):
        return httpx.Response(
            200,
            json={
                "id": 1,
                "name": "Pranav",
                "email": "pranav@example.com",
            },
        )

    transport = httpx.MockTransport(handler)

    with APIWatch(transport=transport) as watch:
        watch.check(
            "https://example.com/api/user",
            schema=VALID_SCHEMA,
        )

        history = watch.get_history()

    assert len(history) == 1
    assert history[0].is_valid is True
    assert history[0].validation_errors == []