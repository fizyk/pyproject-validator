"""Tests for the mypy ``python_version`` check."""

from typing import Any

import pytest
from packaging.version import Version

from check_python_versions.checks import MypyPythonVersionCheck, Status
from check_python_versions.checks.mypy import mypy_python_version

CLASSIFIERS = [
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
]


@pytest.mark.parametrize(
    "version, expected",
    [
        (Version("3.10"), "3.10"),
        (Version("3.9"), "3.9"),
        (Version("3.9.5"), "3.9"),
        (Version("3.14"), "3.14"),
    ],
)
def test_mypy_python_version(version: Version, expected: str) -> None:
    """Test conversion of a python version into mypy's python_version format."""
    assert mypy_python_version(version) == expected


@pytest.mark.parametrize(
    "pyproject, expected_status",
    [
        ({"project": {"classifiers": CLASSIFIERS}}, Status.NOT_APPLICABLE),
        ({"project": {"classifiers": CLASSIFIERS}, "tool": {"mypy": {"strict": True}}}, Status.NOT_APPLICABLE),
        ({"tool": {"mypy": {"python_version": "3.10"}}}, Status.SKIPPED),
        ({"project": {"classifiers": CLASSIFIERS}, "tool": {"mypy": {"python_version": "3.9"}}}, Status.FAILED),
        ({"project": {"classifiers": CLASSIFIERS}, "tool": {"mypy": {"python_version": "3.11"}}}, Status.FAILED),
        ({"project": {"classifiers": CLASSIFIERS}, "tool": {"mypy": {"python_version": "3.10"}}}, Status.PASSED),
    ],
)
def test_mypy_python_version_check(pyproject: dict[str, Any], expected_status: Status) -> None:
    """MypyPythonVersionCheck returns the expected status for each configuration."""
    assert MypyPythonVersionCheck().run(pyproject).status is expected_status


@pytest.mark.parametrize(
    "classifier, python_version",
    [
        # Unquoted 3.10 is parsed by TOML as the float 3.1
        ("Programming Language :: Python :: 3.10", 3.10),
        # Even when the float happens to match, it has to be a string
        ("Programming Language :: Python :: 3.11", 3.11),
    ],
)
def test_unquoted_python_version_fails(classifier: str, python_version: float) -> None:
    """A python_version that isn't a quoted string is always an error."""
    result = MypyPythonVersionCheck().run(
        {"project": {"classifiers": [classifier]}, "tool": {"mypy": {"python_version": python_version}}}
    )
    assert result.status is Status.FAILED
    assert result.message == "`tool.mypy.python_version` should be a quoted string."


def test_failed_result_carries_recommendation() -> None:
    """A failed result includes details and a recommendation for the reporter."""
    result = MypyPythonVersionCheck().run(
        {"project": {"classifiers": CLASSIFIERS}, "tool": {"mypy": {"python_version": "3.9"}}}
    )
    assert result.details
    assert result.recommendation == 'Change `tool.mypy.python_version` into: "3.10"'
