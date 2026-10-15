"""Check that mypy's ``python_version`` is set to the lowest supported python version."""

from typing import Any

from packaging.version import Version

from check_python_versions.checks.base import Check, Result
from check_python_versions.classifiers import get_min_classifier_version


def mypy_python_version(version: Version) -> str:
    """Convert a python version into mypy's ``python_version`` format (ie. 3.10.2 -> 3.10)."""
    return f"{version.major}.{version.minor}"


class MypyPythonVersionCheck(Check):
    """Check that mypy's ``python_version`` is set to the lowest supported python version."""

    title = "MYPY'S PYTHON_VERSION"

    def run(self, pyproject: dict[str, Any]) -> Result:
        """Check that mypy's ``python_version`` is set to the lowest supported python version."""
        python_version = pyproject.get("tool", {}).get("mypy", {}).get("python_version")
        if python_version is None:
            # Not set - mypy uses the version of the interpreter it runs on.
            return Result.not_applicable("Mypy's `python_version` is not set.")

        classifiers = pyproject.get("project", {}).get("classifiers", [])
        min_classifier_ver = get_min_classifier_version(classifiers)
        if min_classifier_ver is None:
            return Result.skipped(
                "Cannot determine the lowest supported python version from `classifiers`, "
                "skipping mypy's `python_version` check."
            )

        expected = mypy_python_version(min_classifier_ver)
        if not isinstance(python_version, str):
            # Unquoted values are parsed by TOML as floats, which turns 3.10 into 3.1.
            return Result.failed(
                "`tool.mypy.python_version` should be a quoted string.",
                details=(
                    f"Minimum version in `classifiers`: {min_classifier_ver}",
                    f"`tool.mypy.python_version` setting is: {python_version} (not a string)",
                ),
                recommendation=f'Change `tool.mypy.python_version` into: "{expected}"',
            )

        if python_version != expected:
            return Result.failed(
                "`tool.mypy.python_version` should point to the lowest supported python version.",
                details=(
                    f"Minimum version in `classifiers`: {min_classifier_ver}",
                    f'`tool.mypy.python_version` setting is: "{python_version}"',
                ),
                recommendation=f'Change `tool.mypy.python_version` into: "{expected}"',
            )

        return Result.passed(f"Mypy's `python_version` ({python_version}) matches the lowest supported python version.")
