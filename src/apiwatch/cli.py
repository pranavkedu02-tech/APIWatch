
import argparse
import asyncio
import sys

from apiwatch import APIWatch, AsyncAPIWatch

DATABASE = "apiwatch_history.db"


def print_banner():
    print()
    print("=" * 55)
    print("                    APIWatch")
    print("              API Monitoring Tool")
    print("=" * 55)
    print()


def print_result(result):
    print(f"API URL:         {result.url}")
    print(f"HTTP Method:     {result.method}")
    print(f"Status Code:     {result.status_code or 'N/A'}")
    print(f"Response Time:   {result.response_time:.4f} seconds")

    if result.response_size is not None:
        print(f"Response Size:   {result.response_size} bytes")

    if result.error:
        print(f"Error:           {result.error}")

    if result.is_success:
        print("\nMonitoring Result: HEALTHY")
    else:
        print("\nMonitoring Result: UNHEALTHY")

    print("-" * 55)


def check_api(url, method="GET"):
    print_banner()

    with APIWatch(history_db=DATABASE) as watch:
        result = watch.check(url, method=method)

    print_result(result)

    return 0 if result.is_success else 1


async def check_many_apis(urls):
    print_banner()

    async with AsyncAPIWatch(history_db=DATABASE) as watch:
        results = await watch.check_many(urls)

    successful = 0
    failed = 0

    for result in results:
        print_result(result)

        if result.is_success:
            successful += 1
        else:
            failed += 1

    print("\nMonitoring Summary")
    print("=" * 55)
    print(f"Total APIs:       {len(results)}")
    print(f"Successful:       {successful}")
    print(f"Failed:           {failed}")

    return 0 if failed == 0 else 1


def show_history(url=None):
    with APIWatch(history_db=DATABASE) as watch:
        history = watch.get_history(url)

    print_banner()

    if not history:
        print("No monitoring history found.")
        return 0

    print(f"Total Records: {len(history)}")
    print("-" * 55)

    for result in history:
        status = "HEALTHY" if result.is_success else "FAILED"

        print(f"URL:            {result.url}")
        print(f"Method:         {result.method}")
        print(f"Status Code:    {result.status_code or 'N/A'}")
        print(f"Response Time:  {result.response_time:.4f}s")
        print(f"Result:         {status}")
        print(f"Timestamp:      {result.timestamp}")
        print("-" * 55)

    return 0


def show_stats(url=None):
    with APIWatch(history_db=DATABASE) as watch:
        stats = watch.get_stats(url)

    print_banner()

    print("Monitoring Statistics")
    print("-" * 55)

    if stats["total_checks"] == 0:
        print("No monitoring data available.")
        return 0

    print(f"Total Checks:           {stats['total_checks']}")
    print(f"Successful Checks:      {stats['successful_checks']}")
    print(f"Failed Checks:          {stats['failed_checks']}")
    print(f"Success Rate:           {stats['success_rate']}%")
    print(f"Average Response Time:  {stats['average_response_time']}s")
    print(f"Fastest Response:       {stats['fastest_response_time']}s")
    print(f"Slowest Response:       {stats['slowest_response_time']}s")

    return 0


def clear_history():
    with APIWatch(history_db=DATABASE) as watch:
        watch.clear_history()

    print("Monitoring history cleared successfully.")
    return 0


def main():
    parser = argparse.ArgumentParser(
        prog="apiwatch",
        description="APIWatch - Lightweight API Monitoring Tool",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    # Check one API
    check_parser = subparsers.add_parser(
        "check",
        help="Check a single API",
    )

    check_parser.add_argument(
        "url",
        help="API URL to monitor",
    )

    check_parser.add_argument(
        "-m",
        "--method",
        default="GET",
        help="HTTP method (default: GET)",
    )

    # Check multiple APIs
    many_parser = subparsers.add_parser(
        "check-many",
        help="Check multiple APIs concurrently",
    )

    many_parser.add_argument(
        "urls",
        nargs="+",
        help="URLs to monitor",
    )

    # History
    history_parser = subparsers.add_parser(
        "history",
        help="Display monitoring history",
    )

    history_parser.add_argument(
        "-u",
        "--url",
        help="Filter history by URL",
    )

    # Statistics
    stats_parser = subparsers.add_parser(
        "stats",
        help="Display monitoring statistics",
    )

    stats_parser.add_argument(
        "-u",
        "--url",
        help="Filter statistics by URL",
    )

    # Clear history
    subparsers.add_parser(
        "clear",
        help="Clear monitoring history",
    )

    args = parser.parse_args()

    try:
        if args.command == "check":
            return check_api(
                args.url,
                method=args.method,
            )

        elif args.command == "check-many":
            return asyncio.run(
                check_many_apis(args.urls)
            )

        elif args.command == "history":
            return show_history(args.url)

        elif args.command == "stats":
            return show_stats(args.url)

        elif args.command == "clear":
            return clear_history()

    except KeyboardInterrupt:
        print("\nMonitoring interrupted.")
        return 130

    except Exception as exc:  # noqa: BLE001
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
