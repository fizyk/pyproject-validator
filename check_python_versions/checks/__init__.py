"""Individual consistency checks run against pyproject.toml."""

from check_python_versions.checks.base import Check, Result, Status
from check_python_versions.checks.requires_python import RequiresPythonCheck
from check_python_versions.checks.ruff import RuffTargetVersionCheck

__all__ = ["ALL_CHECKS", "Check", "RequiresPythonCheck", "Result", "RuffTargetVersionCheck", "Status"]

#: Checks run by the command line tool, in order.
ALL_CHECKS: tuple[Check, ...] = (RequiresPythonCheck(), RuffTargetVersionCheck())
