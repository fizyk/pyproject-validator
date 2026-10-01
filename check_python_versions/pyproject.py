"""Loading of the ``pyproject.toml`` file."""

import tomllib
from pathlib import Path
from typing import Any


def load(path: Path) -> dict[str, Any]:
    """Load and parse the given ``pyproject.toml`` file."""
    with open(path, "rb") as f:
        return tomllib.load(f)
