"""Common reporting of check results."""

import sys

from check_python_versions.checks import Check, Result, Status


def report(check: Check, result: Result) -> None:
    """Print the result of a single check."""
    if result.status is Status.NOT_APPLICABLE:
        return
    if result.status is Status.PASSED:
        print(f"✅ {result.message}")
    elif result.status is Status.SKIPPED:
        print(f"INFO: {result.message}", file=sys.stderr)
    elif result.status is Status.WARNING:
        print(f"WARNING: {result.message}", file=sys.stderr)
    else:
        print("=" * 80, file=sys.stderr)
        print(f"!!! INCONSISTENCY IN {check.title} IN PYPROJECT.TOML !!!", file=sys.stderr)
        for detail in result.details:
            print(f"  {detail}", file=sys.stderr)
        print(f"  ERROR: {result.message}", file=sys.stderr)
        if result.recommendation:
            print(f"  RECOMMENDATION: {result.recommendation}", file=sys.stderr)
        print("=" * 80, file=sys.stderr)


def exit_code(results: list[Result]) -> int:
    """Return the process exit code for the given results."""
    return 1 if any(result.status is Status.FAILED for result in results) else 0
