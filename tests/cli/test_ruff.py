"""Command line tests for the ruff ``target-version`` check."""

from pathlib import Path

import pytest
from pytest import CaptureFixture, MonkeyPatch

from check_python_versions.cli import main
from tests import pyproject
from tests.cli import CLASSIFIERS_310


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
