"""Helpers for testing the `main()` function in check_python_versions."""

from pathlib import Path
from typing import Iterable


def render(requires_python: str | None = None, classifiers: Iterable[str] | None = None) -> str:
    """Render minimal TOML content for a pyproject with optional fields."""
    lines: list[str] = ["[project]"]

    if requires_python:
        lines.append(f'requires-python = "{requires_python}"')

    if classifiers:
        # TOML array of strings
        lines.append("classifiers = [")
        for c in classifiers:
            lines.append(f'  "{c}",')
        lines.append("]")

    return "\n".join(lines) + "\n"


def write(tmp_dir: Path, requires_python: str | None = None, classifiers: Iterable[str] | None = None) -> Path:
    """Write a `pyproject.toml` into the given temporary directory and return its path.

    Usage in tests (to be added next):
      path = write_pyproject(tmp_path, ">=3.10", [
          "Programming Language :: Python :: 3.10",
          "Programming Language :: Python :: 3.11",
      ])
    """
    content = render(requires_python=requires_python, classifiers=classifiers)
    path = tmp_dir / "pyproject.toml"
    path.write_text(content, encoding="utf-8")
    return path
