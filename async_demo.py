import asyncio

from apiwatch import AsyncAPIWatch


async def main():

    urls = [
        "https://jsonplaceholder.typicode.com/posts/1",
        "https://jsonplaceholder.typicode.com/posts/2",
        "https://jsonplaceholder.typicode.com/users/1",
        "https://jsonplaceholder.typicode.com/users/2",
    ]

    async with AsyncAPIWatch() as watch:

        print("Checking APIs concurrently...\n")

        results = await watch.check_many(urls)

        for result in results:
            print(
                f"URL: {result.url}\n"
                f"Status: {result.status_code}\n"
                f"Success: {result.is_success}\n"
                f"Response Time: {result.response_time:.4f}s\n"
            )

        print("Monitoring Statistics:")
        print(watch.get_stats())


if __name__ == "__main__":
    asyncio.run(main())