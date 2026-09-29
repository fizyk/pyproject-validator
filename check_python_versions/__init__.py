"""Check that python versions declared in pyproject.toml are consistent."""

import sys
from pathlib import Path

# Use tomllib for python 3.11+, otherwise use tomli
try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib  # type: ignore[no-redef]
    except ImportError:
        print("ERROR: This script require tomli on Python < 3.11 (pip install tomli)", file=sys.stderr)
        sys.exit(1)

try:
    from packaging.specifiers import SpecifierSet
    from packaging.version import Version
except ImportError:
    print("ERROR: This script requires packaging installed (pip install packaging)", file=sys.stderr)
    sys.exit(1)


def get_min_classifier_version(classifiers: list) -> Version | None:
    """Find the minimal python version in classifiers."""
    prefix = "Programming Language :: Python :: "
    versions: list[Version] = []
    for classifier in classifiers:
        # Looking for entries like '... :: 3.10', '... :: 3.11'
        # IMPORTANT: Ignore general entries like '... :: 3' or '... :: 3 :: Only'
        if classifier.startswith(prefix) and "." in classifier:
            try:
                version_str = classifier.split("::")[-1].strip()
                versions.append(Version(version_str))
            except Exception:
                pass  # Ignore incorrect entries

    return min(versions) if versions else None


def previous_minor_version(min_classifier_ver: Version) -> str:
    """Calculate the previous minor version string for a given classifier version."""
    prev_minor_ver_str = f"{min_classifier_ver.major}.{min_classifier_ver.minor - 1}"
    return prev_minor_ver_str


def ruff_target_version(version: Version) -> str:
    """Convert a python version into ruff's ``target-version`` format (ie. 3.10 -> py310)."""
    return f"py{version.major}{version.minor}"


def check_requires_python(requires_python: str | None, classifiers: list) -> int:
    """Check that ``requires-python`` is in sync with the python version classifiers."""
    if not requires_python or not classifiers:
        print(
            "INFO: Missing `requires-python` or `classifiers` in pyproject.toml, skipping.",
            file=sys.stderr,
        )
        return 0

    min_classifier_ver = get_min_classifier_version(classifiers)
    if min_classifier_ver is None:
        print(
            "WARNING: Cannot find python version classifiers in pyproject.toml (ie. '... :: 3.10'), skipping.",
            file=sys.stderr,
        )
        return 0

    # One less minor than minimal supported (ie. 3.9 for 3.10)
    prev_minor_ver_str = previous_minor_version(min_classifier_ver)

    spec = SpecifierSet(requires_python)

    # This is the problem:
    # Check if the version, which you no longer support (ie. 3.9)
    # STILL MATCHES `requires-python` (ie. ">=3.9").
    # If so, it's an error.
    if prev_minor_ver_str in spec:
        print("=" * 80, file=sys.stderr)
        print("!!! INCONSISTENCY IN PYTHON VERSIONS IN PYPROJECT.TOML !!!", file=sys.stderr)
        print(f"  Minimum version in `classifiers`: {min_classifier_ver}", file=sys.stderr)
        print(
            f" Oldest versiion still supported in classifiers: {prev_minor_ver_str} ",
            file=sys.stderr,
        )
        print(f'  `requires-python` setting is: "{requires_python}"', file=sys.stderr)
        print(
            f"  ERROR: {prev_minor_ver_str} version (which is not in the classifiers) still fits in `requires-python`.",
            file=sys.stderr,
        )
        print(
            f'  RECOMMENDATION: Change`requires-python` into: ">= {min_classifier_ver}"',
            file=sys.stderr,
        )
        print("=" * 80, file=sys.stderr)
        return 1

    print(f"✅ Python versions consistency (`requires-python` and `classifiers` >= {min_classifier_ver}) is verified.")
    return 0


def check_ruff_target_version(target_version: str | None, classifiers: list) -> int:
    """Check that ruff's ``target-version`` is set to the lowest supported python version."""
    if target_version is None:
        # Not set - ruff infers it from `requires-python` on its own.
        return 0

    min_classifier_ver = get_min_classifier_version(classifiers)
    if min_classifier_ver is None:
        print(
            "INFO: Cannot determine the lowest supported python version from `classifiers`, "
            "skipping ruff's `target-version` check.",
            file=sys.stderr,
        )
        return 0

    expected = ruff_target_version(min_classifier_ver)
    if target_version != expected:
        print("=" * 80, file=sys.stderr)
        print("!!! INCONSISTENCY IN RUFF'S TARGET-VERSION IN PYPROJECT.TOML !!!", file=sys.stderr)
        print(f"  Minimum version in `classifiers`: {min_classifier_ver}", file=sys.stderr)
        print(f'  `tool.ruff.target-version` setting is: "{target_version}"', file=sys.stderr)
        print(
            "  ERROR: `tool.ruff.target-version` should point to the lowest supported python version.",
            file=sys.stderr,
        )
        print(f'  RECOMMENDATION: Change `tool.ruff.target-version` into: "{expected}"', file=sys.stderr)
        print("=" * 80, file=sys.stderr)
        return 1

    print(f"✅ Ruff's `target-version` ({target_version}) matches the lowest supported python version.")
    return 0


def main() -> int:
    """Check that python versions declared in pyproject.toml are consistent."""
    try:
        pyproject_path = Path("pyproject.toml")
        if not pyproject_path.exists():
            print(f"INFO: File {pyproject_path} does not exists, skipping checking.", file=sys.stderr)
            return 0

        with open(pyproject_path, "rb") as f:
            config = tomllib.load(f)

        project_meta = config.get("project", {})
        requires_python = project_meta.get("requires-python")
        classifiers = project_meta.get("classifiers", [])
        ruff_target = config.get("tool", {}).get("ruff", {}).get("target-version")

        results = [
            check_requires_python(requires_python, classifiers),
            check_ruff_target_version(ruff_target, classifiers),
        ]
        return max(results)

    except Exception as e:
        print(f"ERROR: Error during checking python versions in pyproject.toml: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
