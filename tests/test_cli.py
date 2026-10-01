"""Tests for the command line entry point."""

from pathlib import Path

import pytest
from pytest import CaptureFixture, MonkeyPatch

from check_python_versions.cli import main
from tests import pyproject


def test_main_when_pyproject_toml_missing(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
    capsys: CaptureFixture[str],
) -> None:
    """If pyproject.toml is missing, the main () should exit 0 and log INFO to stderr."""
    # Ensure we run in an empty temp directory with no pyproject.toml
    monkeypatch.chdir(tmp_path)
    assert not (tmp_path / "pyproject.toml").exists()

    assert main() == 0
    captured = capsys.readouterr()

    # No output to stdout
    assert captured.out == ""

    # Informational message to stderr mentioning that the file doesn't exist
    err = captured.err
    assert "INFO" in err
    assert "pyproject.toml" in err
    assert ("does not exists" in err) or ("does not exist" in err)


def test_main_only_classifiers_no_requires_python(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
    capsys: CaptureFixture[str],
) -> None:
    """When only classifiers are present, expect INFO skip and return code 0."""
    monkeypatch.chdir(tmp_path)
    # Write pyproject with classifiers but without requires-python
    pyproject.write(
        tmp_path,
        requires_python=None,
        classifiers=[
            "Programming Language :: Python :: 3.10",
            "Programming Language :: Python :: 3.11",
        ],
    )

    assert main() == 0
    captured = capsys.readouterr()
    assert captured.out == ""

    err = captured.err
    assert "INFO" in err
    assert "Missing `requires-python` or `classifiers`" in err
    assert "skipping" in err.lower()


def test_main_only_requires_python_no_classifiers(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
    capsys: CaptureFixture[str],
) -> None:
    """When only requires-python is present, expect INFO skip and return code 0."""
    monkeypatch.chdir(tmp_path)
    # Write a pyproject with requires-python but without classifiers
    pyproject.write(
        tmp_path,
        requires_python=">=3.10",
        classifiers=[],
    )

    assert main() == 0
    captured = capsys.readouterr()
    assert captured.out == ""

    err = captured.err
    assert "INFO" in err
    assert "Missing `requires-python` or `classifiers`" in err
    assert "skipping" in err.lower()


def test_main_no_versioned_classifiers(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
    capsys: CaptureFixture[str],
) -> None:
    """When classifiers lack specific versions (e.g., only '... :: 3'), warn and skip.

    Expect return code 0, stdout empty, and WARNING on stderr about not finding versioned classifiers.
    """
    monkeypatch.chdir(tmp_path)

    pyproject.write(
        tmp_path,
        requires_python=">=3.8",
        classifiers=[
            "Programming Language :: Python :: 3",  # generic should be ignored
            "Programming Language :: Python :: Only",  # invalid
            "License :: OSI Approved :: MIT License",
        ],
    )

    assert main() == 0
    captured = capsys.readouterr()
    assert captured.out == ""

    err = captured.err
    assert "WARNING" in err
    assert "Cannot find python version classifiers" in err


def test_main_inconsistency_between_classifiers_and_requires_python(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
    capsys: CaptureFixture[str],
) -> None:
    """Classifiers min=3.10 but requires-python allows 3.9 → should error (return code 1).

    We assert the presence of key substrings from the error block to keep tests
    resilient to minor formatting changes.
    """
    monkeypatch.chdir(tmp_path)

    pyproject.write(
        tmp_path,
        requires_python=">=3.9",
        classifiers=[
            "Programming Language :: Python :: 3.10",
            "Programming Language :: Python :: 3.11",
        ],
    )

    assert main() == 1
    captured = capsys.readouterr()

    # No success message to stdout in an error scenario
    assert captured.out == ""

    err = captured.err
    # Header marker and main title
    assert "INCONSISTENCY IN PYTHON VERSIONS" in err
    # Minimal classifier echoed
    assert "Minimum version in `classifiers`" in err
    assert "3.10" in err
    # Previous minor version mentioned (3.9 expected)
    assert "Oldest version still supported in classifiers" in err
    assert "3.9" in err
    # requires-python echoed back
    assert "`requires-python`" in err
    assert ">=3.9" in err
    # Recommendation line present
    assert "RECOMMENDATION" in err
    assert ">= 3.10" in err


def test_main_consistent_versions(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
    capsys: CaptureFixture[str],
) -> None:
    """Classifiers min=3.10 and requires-python ">=3.10" → should succeed (return code 0).

    Expect a success line on stdout mentioning consistency and the minimal
    classifier version; stderr should be empty.
    """
    monkeypatch.chdir(tmp_path)

    pyproject.write(
        tmp_path,
        requires_python=">=3.10",
        classifiers=[
            "Programming Language :: Python :: 3.10",
            "Programming Language :: Python :: 3.11",
        ],
    )

    assert main() == 0
    captured = capsys.readouterr()

    # Success message should be on stdout
    out = captured.out
    assert "Python versions consistency" in out
    assert ">= 3.10" in out or ">=3.10" in out or "3.10" in out

    # No errors expected
    assert captured.err == ""


CLASSIFIERS_310 = [
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
]


def test_main_ruff_target_version_consistent(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
    capsys: CaptureFixture[str],
) -> None:
    """Ruff's target-version matches the lowest classifier → should succeed (return code 0)."""
    monkeypatch.chdir(tmp_path)
    pyproject.write(tmp_path, requires_python=">=3.10", classifiers=CLASSIFIERS_310, ruff_target_version="py310")

    assert main() == 0
    captured = capsys.readouterr()
    assert "Python versions consistency" in captured.out
    assert "Ruff's `target-version` (py310)" in captured.out
    assert captured.err == ""


@pytest.mark.parametrize("target_version", ["py39", "py311"])
def test_main_ruff_target_version_inconsistent(
    target_version: str,
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
    capsys: CaptureFixture[str],
) -> None:
    """Ruff's target-version other than the lowest classifier → should error (return code 1)."""
    monkeypatch.chdir(tmp_path)
    pyproject.write(tmp_path, requires_python=">=3.10", classifiers=CLASSIFIERS_310, ruff_target_version=target_version)

    assert main() == 1
    captured = capsys.readouterr()
    # requires-python check still passes and reports it
    assert "Python versions consistency" in captured.out

    err = captured.err
    assert "INCONSISTENCY IN RUFF'S TARGET-VERSION" in err
    assert f'"{target_version}"' in err
    assert "RECOMMENDATION" in err
    assert '"py310"' in err


def test_main_ruff_target_version_and_requires_python_inconsistent(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
    capsys: CaptureFixture[str],
) -> None:
    """Both checks fail → both are reported, return code 1."""
    monkeypatch.chdir(tmp_path)
    pyproject.write(tmp_path, requires_python=">=3.9", classifiers=CLASSIFIERS_310, ruff_target_version="py39")

    assert main() == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "INCONSISTENCY IN PYTHON VERSIONS" in captured.err
    assert "INCONSISTENCY IN RUFF'S TARGET-VERSION" in captured.err


def test_main_ruff_target_version_without_requires_python(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
    capsys: CaptureFixture[str],
) -> None:
    """Ruff's target-version is checked against classifiers even without requires-python."""
    monkeypatch.chdir(tmp_path)
    pyproject.write(tmp_path, requires_python=None, classifiers=CLASSIFIERS_310, ruff_target_version="py39")

    assert main() == 1
    captured = capsys.readouterr()
    assert "Missing `requires-python` or `classifiers`" in captured.err
    assert "INCONSISTENCY IN RUFF'S TARGET-VERSION" in captured.err


def test_main_ruff_target_version_without_classifiers(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
    capsys: CaptureFixture[str],
) -> None:
    """Without versioned classifiers the ruff check is skipped with INFO, return code 0."""
    monkeypatch.chdir(tmp_path)
    pyproject.write(tmp_path, requires_python=">=3.10", classifiers=[], ruff_target_version="py39")

    assert main() == 0
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "skipping ruff's `target-version` check" in captured.err
