from apiwatch import APIWatch

REPOSITORY_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "name": {"type": "string"},
        "full_name": {"type": "string"},
        "private": {"type": "boolean"},
        "html_url": {"type": "string"},
    },
    "required": ["id", "name", "full_name", "private", "html_url"],
}


def main():
    print("=" * 60)
    print("APIWatch - GitHub REST API Monitoring")
    print("=" * 60)

    url = "https://api.github.com/repos/python/cpython"

    with APIWatch() as watch:
        result = watch.check(url, schema=REPOSITORY_SCHEMA)

        print("\nMONITORING RESULT")
        print("-" * 40)
        print(f"URL           : {result.url}")
        print(f"Status        : {result.status_code}")
        print(f"Response Time : {result.response_time:.4f} seconds")
        print(f"Response Size : {result.response_size} bytes")
        print(f"HTTP Success  : {result.is_success}")
        print(f"Schema Valid  : {result.is_valid}")

        print("\nVALIDATION")
        print("-" * 40)

        if result.validation_errors:
            for error in result.validation_errors:
                print(f"ERROR: {error}")
        else:
            print("Schema validation successful.")

        print("\nASSERTIONS")
        print("-" * 40)

        result.assert_status_code(200)
        result.assert_success()
        result.assert_response_time(10.0)
        result.assert_valid()
        result.assert_no_errors()

        print("Status assertion        : PASSED")
        print("Success assertion       : PASSED")
        print("Response time assertion : PASSED")
        print("Schema assertion        : PASSED")
        print("No errors assertion     : PASSED")

        print("\nHISTORY")
        print("-" * 40)

        history = watch.get_history()
        print(f"Total API checks: {len(history)}")

        print("\n" + "=" * 60)
        print("GITHUB API TEST COMPLETED SUCCESSFULLY")
        print("=" * 60)


if __name__ == "__main__":
    main()