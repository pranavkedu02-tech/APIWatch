import asyncio

from apiwatch import AsyncAPIWatch


async def main():
    print("=" * 70)
    print("APIWatch - Concurrent API Monitoring")
    print("=" * 70)

    urls = [
        "https://jsonplaceholder.typicode.com/posts/1",
        "https://jsonplaceholder.typicode.com/users/1",
        "https://jsonplaceholder.typicode.com/comments/1",
    ]

    async with AsyncAPIWatch() as watch:

        print("\nMonitoring multiple APIs simultaneously...")
        print("-" * 70)

        results = await watch.check_many(urls)

        for index, result in enumerate(results, start=1):

            print(f"\nAPI #{index}")
            print("-" * 40)

            print(f"URL           : {result.url}")
            print(f"Method        : {result.method}")
            print(f"Status Code   : {result.status_code}")
            print(f"Response Time : {result.response_time:.4f} seconds")
            print(f"Success       : {result.is_success}")

            if result.error:
                print(f"Error         : {result.error}")

        print("\n" + "=" * 70)
        print("MONITORING SUMMARY")
        print("=" * 70)

        successful = sum(
            1 for result in results if result.is_success
        )

        failed = len(results) - successful

        print(f"Total APIs monitored : {len(results)}")
        print(f"Successful APIs      : {successful}")
        print(f"Failed APIs          : {failed}")

        if results:
            average_response_time = sum(
                result.response_time for result in results
            ) / len(results)

            print(
                "Average response time : "
                f"{average_response_time:.4f} seconds"
            )

        print("\nAPI HISTORY")
        print("-" * 40)

        history = watch.get_history()

        print(f"Total recorded checks: {len(history)}")

        print("\n" + "=" * 70)
        print("CONCURRENT MONITORING COMPLETED")
        print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())