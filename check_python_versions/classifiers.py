"""Helpers for extracting python versions from trove classifiers."""

from packaging.version import Version


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
