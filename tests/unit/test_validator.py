
import pytest
from jsonschema.exceptions import SchemaError

from apiwatch.validator import ResponseValidator

USER_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {
            "type": "integer",
        },
        "name": {
            "type": "string",
        },
        "username": {
            "type": "string",
        },
        "email": {
            "type": "string",
            "format": "email",
        },
    },
    "required": [
        "id",
        "name",
        "username",
        "email",
    ],
}


def test_valid_response():
    validator = ResponseValidator(USER_SCHEMA)

    data = {
        "id": 1,
        "name": "Leanne Graham",
        "username": "Bret",
        "email": "leanne@example.com",
    }

    result = validator.validate(data)

    assert result.is_valid is True
    assert result.errors == []
    assert result.error_count == 0


def test_missing_required_field():
    validator = ResponseValidator(USER_SCHEMA)

    data = {
        "id": 1,
        "name": "Leanne Graham",
        "username": "Bret",
    }

    result = validator.validate(data)

    assert result.is_valid is False
    assert result.error_count == 1
    assert any("email" in error for error in result.errors)


def test_invalid_data_type():
    validator = ResponseValidator(USER_SCHEMA)

    data = {
        "id": "one",
        "name": "Leanne Graham",
        "username": "Bret",
        "email": "leanne@example.com",
    }

    result = validator.validate(data)

    assert result.is_valid is False
    assert any("id" in error for error in result.errors)


def test_invalid_email_format():
    validator = ResponseValidator(USER_SCHEMA)

    data = {
        "id": 1,
        "name": "Leanne Graham",
        "username": "Bret",
        "email": "invalid-email",
    }

    result = validator.validate(data)

    assert result.is_valid is False
    assert any("email" in error for error in result.errors)


def test_multiple_validation_errors():
    validator = ResponseValidator(USER_SCHEMA)

    data = {
        "id": "invalid",
        "email": "not-an-email",
    }

    result = validator.validate(data)

    assert result.is_valid is False
    assert result.error_count >= 3


def test_nested_schema_validation():
    schema = {
        "type": "object",
        "properties": {
            "user": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "integer",
                    },
                },
                "required": ["id"],
            },
        },
        "required": ["user"],
    }

    validator = ResponseValidator(schema)

    result = validator.validate(
        {
            "user": {
                "id": "invalid",
            },
        }
    )

    assert result.is_valid is False
    assert any("user.id" in error for error in result.errors)


def test_invalid_schema_raises_error():
    invalid_schema = {
        "type": "invalid-type",
    }

    with pytest.raises(SchemaError):
        ResponseValidator(invalid_schema)


def test_valid_empty_object_schema():
    validator = ResponseValidator(
        {
            "type": "object",
        }
    )

    result = validator.validate({})

    assert result.is_valid is True
    assert result.errors == []
