
from dataclasses import dataclass, field
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


@dataclass
class ValidationResult:
    """Result of validating API response data against a JSON schema."""

    is_valid: bool
    errors: list[str] = field(default_factory=list)

    @property
    def error_count(self) -> int:
        return len(self.errors)


class ResponseValidator:
    """Validate API responses using JSON Schema."""

    def __init__(self, schema: dict[str, Any]) -> None:
        self.schema = schema

        # Validate the schema itself before using it.
        Draft202012Validator.check_schema(schema)

        self.validator = Draft202012Validator(
            schema,
            format_checker=FormatChecker(),
        )

    def validate(self, data: Any) -> ValidationResult:
        """Validate data against the configured JSON Schema."""

        validation_errors = sorted(
            self.validator.iter_errors(data),
            key=lambda error: list(error.path),
        )

        errors = []

        for error in validation_errors:
            field_path = ".".join(
                str(part) for part in error.path
            )

            if field_path:
                errors.append(
                    f"{field_path}: {error.message}"
                )
            else:
                errors.append(error.message)

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
        )
