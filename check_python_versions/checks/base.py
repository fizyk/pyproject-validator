"""Common interface for the pyproject.toml checks."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any


class Status(Enum):
    """Outcome of a single check."""

    PASSED = "passed"
    NOT_APPLICABLE = "not_applicable"
    SKIPPED = "skipped"
    WARNING = "warning"
    FAILED = "failed"


@dataclass(frozen=True)
class Result:
    """Result of running a check, to be reported by the caller."""

    status: Status
    message: str
    details: tuple[str, ...] = ()
    recommendation: str | None = None

    @classmethod
    def passed(cls, message: str) -> "Result":
        """Check ran and the configuration is consistent."""
        return cls(Status.PASSED, message)

    @classmethod
    def not_applicable(cls, message: str) -> "Result":
        """Check has nothing to verify in this configuration; not reported."""
        return cls(Status.NOT_APPLICABLE, message)

    @classmethod
    def skipped(cls, message: str) -> "Result":
        """Check did not apply to this configuration."""
        return cls(Status.SKIPPED, message)

    @classmethod
    def warning(cls, message: str) -> "Result":
        """Check could not run, which likely points to an incomplete configuration."""
        return cls(Status.WARNING, message)

    @classmethod
    def failed(cls, message: str, details: tuple[str, ...] = (), recommendation: str | None = None) -> "Result":
        """Check found an inconsistency."""
        return cls(Status.FAILED, message, details, recommendation)


class Check(ABC):
    """A single consistency check run against the parsed pyproject.toml."""

    #: Short, upper-case name of what's being checked, used in failure reports.
    title: str

    @abstractmethod
    def run(self, pyproject: dict[str, Any]) -> Result:
        """Run the check against the parsed pyproject.toml content."""
