from apiwatch import APIWatch

POST_SCHEMA = {
    "type": "object",
    "properties": {
        "userId": {"type": "integer"},
        "id": {"type": "integer"},
        "title": {"type": "string"},
        "body": {"type": "string"},
    },
    "required": ["userId", "id", "title", "body"],
}


def main():
    print("=" * 60)
    print("APIWatch - JSONPlaceholder API Monitoring")
    print("=" * 60)

    with APIWatch() as watch:
        result = watch.check(
            "https://jsonplaceholder.typicode.com/posts/1",
            schema=POST_SCHEMA,
        )

        print("\nAPI MONITORING RESULT")
        print("-" * 40)

        print(f"URL             : {result.url}")
        print(f"Method          : {result.method}")
        print(f"Status Code     : {result.status_code}")
        print(f"Response Time   : {result.response_time:.4f} seconds")
        print(f"Response Size   : {result.response_size} bytes")
        print(f"HTTP Success    : {result.is_success}")
        print(f"Schema Valid    : {result.is_valid}")

        print("\nVALIDATION ERRORS")
        print("-" * 40)

        if result.validation_errors:
            for error in result.validation_errors:
                print(error)
        else:
            print("No validation errors.")

        print("\nASSERTIONS")
        print("-" * 40)

        result.assert_status_code(200)
        result.assert_success()
        result.assert_response_time(5.0)
        result.assert_valid()
        result.assert_no_errors()

        print("Status code assertion : PASSED")
        print("Success assertion     : PASSED")
        print("Response time         : PASSED")
        print("Schema validation     : PASSED")
        print("No errors             : PASSED")

        print("\nHISTORY")
        print("-" * 40)

        history = watch.get_history()

        print(f"Total API checks: {len(history)}")

        print("\n" + "=" * 60)
        print("API TEST COMPLETED SUCCESSFULLY")
        print("=" * 60)


if __name__ == "__main__":
    main()