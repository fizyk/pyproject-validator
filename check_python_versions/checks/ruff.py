"""Check that ruff's ``target-version`` is set to the lowest supported python version."""

from typing import Any

from packaging.version import Version

from check_python_versions.checks.base import Check, Result
from check_python_versions.classifiers import get_min_classifier_version


def ruff_target_version(version: Version) -> str:
    """Convert a python version into ruff's ``target-version`` format (ie. 3.10 -> py310)."""
    return f"py{version.major}{version.minor}"


class RuffTargetVersionCheck(Check):
    """Check that ruff's ``target-version`` is set to the lowest supported python version."""

    title = "RUFF'S TARGET-VERSION"

    def run(self, pyproject: dict[str, Any]) -> Result:
        """Check that ruff's ``target-version`` is set to the lowest supported python version."""
        target_version = pyproject.get("tool", {}).get("ruff", {}).get("target-version")
        if target_version is None:
            # Not set - ruff infers it from `requires-python` on its own.
            return Result.not_applicable("Ruff's `target-version` is not set.")

        classifiers = pyproject.get("project", {}).get("classifiers", [])
        min_classifier_ver = get_min_classifier_version(classifiers)
        if min_classifier_ver is None:
            return Result.skipped(
                "Cannot determine the lowest supported python version from `classifiers`, "
                "skipping ruff's `target-version` check."
            )

        expected = ruff_target_version(min_classifier_ver)
        if target_version != expected:
            return Result.failed(
                "`tool.ruff.target-version` should point to the lowest supported python version.",
                details=(
                    f"Minimum version in `classifiers`: {min_classifier_ver}",
                    f'`tool.ruff.target-version` setting is: "{target_version}"',
                ),
                recommendation=f'Change `tool.ruff.target-version` into: "{expected}"',
            )

        return Result.passed(f"Ruff's `target-version` ({target_version}) matches the lowest supported python version.")
