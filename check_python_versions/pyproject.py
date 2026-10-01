"""Loading of the ``pyproject.toml`` file."""

import sys
from pathlib import Path
from typing import Any

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


def load(path: Path) -> dict[str, Any]:
    """Load and parse the given ``pyproject.toml`` file."""
    with open(path, "rb") as f:
        return tomllib.load(f)
