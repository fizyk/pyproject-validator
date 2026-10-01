"""Tests for the ruff ``target-version`` check."""

from typing import Any

import pytest
from packaging.version import Version

from check_python_versions.checks import RuffTargetVersionCheck, Status
from check_python_versions.checks.ruff import ruff_target_version

CLASSIFIERS = [
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
]


@pytest.mark.parametrize(
    "version, expected",
    [
        (Version("3.10"), "py310"),
        (Version("3.9"), "py39"),
        (Version("3.9.5"), "py39"),
        (Version("3.14"), "py314"),
    ],
)
def test_ruff_target_version(version: Version, expected: str) -> None:
    """Test conversion of a python version into ruff's target-version format."""
    assert ruff_target_version(version) == expected


@pytest.mark.parametrize(
    "pyproject, expected_status",
    [
        ({"project": {"classifiers": CLASSIFIERS}}, Status.NOT_APPLICABLE),
        ({"tool": {"ruff": {"target-version": "py310"}}}, Status.SKIPPED),
        ({"project": {"classifiers": CLASSIFIERS}, "tool": {"ruff": {"target-version": "py39"}}}, Status.FAILED),
        ({"project": {"classifiers": CLASSIFIERS}, "tool": {"ruff": {"target-version": "py310"}}}, Status.PASSED),
    ],
)
def test_ruff_target_version_check(pyproject: dict[str, Any], expected_status: Status) -> None:
    """RuffTargetVersionCheck returns the expected status for each configuration."""
    assert RuffTargetVersionCheck().run(pyproject).status is expected_status


def test_failed_result_carries_recommendation() -> None:
    """A failed result includes details and a recommendation for the reporter."""
    result = RuffTargetVersionCheck().run(
        {"project": {"classifiers": CLASSIFIERS}, "tool": {"ruff": {"target-version": "py39"}}}
    )
    assert result.details
    assert result.recommendation == 'Change `tool.ruff.target-version` into: "py310"'
