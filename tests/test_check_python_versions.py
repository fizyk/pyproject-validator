"""Tests for the check_python_versions module."""

import pytest
from packaging.version import Version

from check_python_versions import get_min_classifier_version, ruff_target_version


@pytest.mark.parametrize(
    "classifiers, expected_version",
    [
        (
            [
                "Programming Language :: Python :: 3.9",
                "Programming Language :: Python :: 3.10",
                "Programming Language :: Python :: 3.11",
            ],
            Version("3.9"),
        ),
        (
            ["Programming Language :: Python :: 3.8"],
            Version("3.8"),
        ),
        (
            [
                "Programming Language :: Python :: 3.11",
                "Programming Language :: Python :: 3.9",
                "Programming Language :: Python :: 3.10",
            ],
            Version("3.9"),
        ),
        (
            [
                "Programming Language :: Python :: 3.9.5",
                "Programming Language :: Python :: 3.10.0",
            ],
            Version("3.9.5"),
        ),
        (
            [
                "Programming Language :: Python :: 3.11",
                "Operating System :: OS Independent",
                "Programming Language :: Python :: 3.9",
                "Programming Language :: Python :: 3",
                "Programming Language :: Python :: 3.10",
                "Topic :: Software Development :: Build Tools",
            ],
            Version("3.9"),
        ),
        (
            [
                "Programming Language :: Python :: Only",
                "Programming Language :: Python :: 3",
                "License :: OSI Approved :: MIT License",
            ],
            None,
        ),
        (
            [],
            None,
        ),
        (
            [
                "Programming Language :: Python :: 3.x",  # Invalid version format
                "Programming Language :: Python :: foo",  # Invalid version format
            ],
            None,
        ),
    ],
)
def test_get_min_classifier_version(classifiers: list[str], expected_version: Version | None) -> None:
    """Test get_min_classifier_version with various valid classifiers, including mixed valid/invalid."""
    assert get_min_classifier_version(classifiers) == expected_version


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
