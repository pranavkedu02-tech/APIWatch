from apiwatch.validator import ResponseValidator


schema = {
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


validator = ResponseValidator(schema)

# Valid API response
valid_response = {
    "id": 1,
    "name": "Pranav",
    "email": "pranav@example.com",
}

# Invalid API response
invalid_response = {
    "id": "one",
    "name": "Pranav",
    "email": "invalid-email",
}


print("VALID RESPONSE")
result = validator.validate(valid_response)

print("Valid:", result.is_valid)
print("Errors:", result.errors)


print("\nINVALID RESPONSE")
result = validator.validate(invalid_response)

print("Valid:", result.is_valid)
print("Error Count:", result.error_count)

for error in result.errors:
    print("-", error)