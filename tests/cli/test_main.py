"""Tests for the command line entry point, independent of the individual checks."""

from pathlib import Path

from pytest import CaptureFixture, MonkeyPatch

from check_python_versions.cli import main


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
