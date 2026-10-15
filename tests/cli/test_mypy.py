"""Command line tests for the mypy ``python_version`` check."""

from pathlib import Path

import pytest
from pytest import CaptureFixture, MonkeyPatch

from check_python_versions.cli import main
from tests import pyproject
from tests.cli import CLASSIFIERS_310


def test_main_mypy_python_version_consistent(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
    capsys: CaptureFixture[str],
) -> None:
    """Mypy's python_version matches the lowest classifier → should succeed (return code 0)."""
    monkeypatch.chdir(tmp_path)
    pyproject.write(tmp_path, requires_python=">=3.10", classifiers=CLASSIFIERS_310, mypy_python_version="3.10")

    assert main() == 0
    captured = capsys.readouterr()
    assert "Python versions consistency" in captured.out
    assert "Mypy's `python_version` (3.10)" in captured.out
    assert captured.err == ""


@pytest.mark.parametrize("python_version", ["3.9", "3.11"])
def test_main_mypy_python_version_inconsistent(
    python_version: str,
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
    capsys: CaptureFixture[str],
) -> None:
    """Mypy's python_version other than the lowest classifier → should error (return code 1)."""
    monkeypatch.chdir(tmp_path)
    pyproject.write(tmp_path, requires_python=">=3.10", classifiers=CLASSIFIERS_310, mypy_python_version=python_version)

    assert main() == 1
    captured = capsys.readouterr()
    # requires-python check still passes and reports it
    assert "Python versions consistency" in captured.out

    err = captured.err
    assert "INCONSISTENCY IN MYPY'S PYTHON_VERSION" in err
    assert f'"{python_version}"' in err
    assert "RECOMMENDATION" in err
    assert '"3.10"' in err


def test_main_mypy_python_version_unquoted(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
    capsys: CaptureFixture[str],
) -> None:
    """Unquoted python_version = 3.10 is read by TOML as 3.1 → should error (return code 1)."""
    monkeypatch.chdir(tmp_path)
    path = pyproject.write(tmp_path, requires_python=">=3.10", classifiers=CLASSIFIERS_310)
    path.write_text(path.read_text() + "\n[tool.mypy]\npython_version = 3.10\n", encoding="utf-8")

    assert main() == 1
    captured = capsys.readouterr()
    assert "INCONSISTENCY IN MYPY'S PYTHON_VERSION" in captured.err
    assert "`tool.mypy.python_version` setting is: 3.1 (not a string)" in captured.err
    assert "should be a quoted string" in captured.err
    assert 'into: "3.10"' in captured.err


def test_main_mypy_python_version_without_classifiers(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
    capsys: CaptureFixture[str],
) -> None:
    """Without versioned classifiers the mypy check is skipped with INFO, return code 0."""
    monkeypatch.chdir(tmp_path)
    pyproject.write(tmp_path, requires_python=">=3.10", classifiers=[], mypy_python_version="3.9")

    assert main() == 0
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "skipping mypy's `python_version` check" in captured.err
