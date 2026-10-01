"""Check that ``requires-python`` is in sync with the python version classifiers."""

from typing import Any

from packaging.specifiers import SpecifierSet

from check_python_versions.checks.base import Check, Result
from check_python_versions.classifiers import get_min_classifier_version, previous_minor_version


class RequiresPythonCheck(Check):
    """Check that ``requires-python`` doesn't allow versions missing from classifiers."""

    title = "PYTHON VERSIONS"

    def run(self, pyproject: dict[str, Any]) -> Result:
        """Check that ``requires-python`` is in sync with the python version classifiers."""
        project_meta = pyproject.get("project", {})
        requires_python = project_meta.get("requires-python")
        classifiers = project_meta.get("classifiers", [])

        if not requires_python or not classifiers:
            return Result.skipped("Missing `requires-python` or `classifiers` in pyproject.toml, skipping.")

        min_classifier_ver = get_min_classifier_version(classifiers)
        if min_classifier_ver is None:
            return Result.warning(
                "Cannot find python version classifiers in pyproject.toml (ie. '... :: 3.10'), skipping."
            )

        # One less minor than minimal supported (ie. 3.9 for 3.10)
        prev_minor_ver_str = previous_minor_version(min_classifier_ver)

        # This is the problem:
        # Check if the version, which you no longer support (ie. 3.9)
        # STILL MATCHES `requires-python` (ie. ">=3.9").
        # If so, it's an error.
        if prev_minor_ver_str in SpecifierSet(requires_python):
            return Result.failed(
                f"{prev_minor_ver_str} version (which is not in the classifiers) still fits in `requires-python`.",
                details=(
                    f"Minimum version in `classifiers`: {min_classifier_ver}",
                    f"Oldest version still supported in classifiers: {prev_minor_ver_str}",
                    f'`requires-python` setting is: "{requires_python}"',
                ),
                recommendation=f'Change `requires-python` into: ">= {min_classifier_ver}"',
            )

        return Result.passed(
            f"Python versions consistency (`requires-python` and `classifiers` >= {min_classifier_ver}) is verified."
        )
