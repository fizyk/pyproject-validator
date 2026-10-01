"""Tests for the ``requires-python`` check."""

from typing import Any

import pytest

from check_python_versions.checks import RequiresPythonCheck, Status

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
