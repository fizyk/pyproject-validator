"""Tests for the main function of the check-python-versions script."""

from pathlib import Path

from pytest import CaptureFixture, MonkeyPatch

from check_python_versions import main
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
    assert "Oldest versiion still supported in classifiers" in err
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
