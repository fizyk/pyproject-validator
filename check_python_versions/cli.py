"""Command line entry point."""

import sys
from pathlib import Path

from check_python_versions import pyproject
from check_python_versions.checks import ALL_CHECKS
from check_python_versions.report import exit_code, report


def main() -> int:
    """Check that python versions declared in pyproject.toml are consistent."""
    try:
        pyproject_path = Path("pyproject.toml")
        if not pyproject_path.exists():
            print(f"INFO: File {pyproject_path} does not exists, skipping checking.", file=sys.stderr)
            return 0

        config = pyproject.load(pyproject_path)

        results = []
        for check in ALL_CHECKS:
            result = check.run(config)
            report(check, result)
            results.append(result)
        return exit_code(results)

    except Exception as e:
        print(f"ERROR: Error during checking python versions in pyproject.toml: {e}", file=sys.stderr)
        return 1
