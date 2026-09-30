"""Tests for the individual checks, independent of output reporting."""

from typing import Any

import pytest

from check_python_versions.checks import RequiresPythonCheck, RuffTargetVersionCheck, Status

CLASSIFIERS = [
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
]


@pytest.mark.parametrize(
    "pyproject, expected_status",
    [
        ({}, Status.SKIPPED),
        ({"project": {"classifiers": CLASSIFIERS}}, Status.SKIPPED),
        ({"project": {"requires-python": ">=3.10"}}, Status.SKIPPED),
        (
            {"project": {"requires-python": ">=3.10", "classifiers": ["Programming Language :: Python :: 3"]}},
            Status.WARNING,
        ),
        ({"project": {"requires-python": ">=3.9", "classifiers": CLASSIFIERS}}, Status.FAILED),
        ({"project": {"requires-python": ">=3.10", "classifiers": CLASSIFIERS}}, Status.PASSED),
    ],
)
def test_requires_python_check(pyproject: dict[str, Any], expected_status: Status) -> None:
    """RequiresPythonCheck returns the expected status for each configuration."""
    assert RequiresPythonCheck().run(pyproject).status is expected_status


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
