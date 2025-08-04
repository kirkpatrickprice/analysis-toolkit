"""Base classes and utilities for the KPAT Process Scripts models."""

from collections.abc import Callable, Generator
from pathlib import Path
from typing import TYPE_CHECKING

from pydantic import ConfigDict, field_validator

from kp_analysis_toolkit.models.base import KPATBaseModel
from kp_analysis_toolkit.process_scripts.models.mixins import PathValidationMixin

if TYPE_CHECKING:
    from _hashlib import HASH


class FileModel(PathValidationMixin):
    """Base model for working with file data."""

    file: Path
    encoding: str | None = None
    file_hash: str | None = None

    # Enable arbitrary types to handle Path objects and callables
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator("file")
    @classmethod
    def validate_file(cls, value: Path) -> Path:
        """Validate that the file exists."""
        return cls.validate_file_exists(value)

    def read_line(self) -> Generator[str, None, None]:
        """
        Read the file content with appropriate encoding.

        This method reads the file line by line, using the specified encoding.
        It yields each line as a string.

        Args:
            None

        Returns:
            line: Yields each line of the file as a string.

        """
        if not self.encoding:
            self.encoding = detect_encoding(self.file)
        encoding: str = self.encoding
        with self.file.open("r", encoding=encoding) as f:
            yield from f.readlines()

    def generate_file_hash(self) -> str:
        """Generate a SHA-256 hash of the file content."""
        import hashlib

        hasher: HASH = hashlib.sha256()
        with self.file.open("rb") as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        self.file_hash = hasher.hexdigest()
        return self.file_hash


class ConfigModel:
    """Base model for configuration objects."""

    def to_dict(self) -> dict[str, str]:
        """Return a dictionary of the configuration for logging/debugging."""
        return {
            field_name: str(value) if value is not None else "None"
            for field_name, value in self.model_dump().items()
        }


class HashableModel(KPATBaseModel):
    """Base model for objects that can be hashed/uniquely identified."""

    def get_hash_identifier(self) -> str:
        """Generate a hash identifier for this model based on its content."""
        # Using the pydantic model_dump_json ensures consistent serialization
        # which can then be hashed for a unique representation
        model_json: str = self.model_dump_json(exclude={"system_id"})
        return hash_string(model_json)


class RegexPatterns(KPATBaseModel):
    """Generic configuration for regex-based data extraction and formatting."""

    patterns: dict[str, str]
    formatter: Callable[[dict[str, str]], str] | None = None


class StatsCollector:
    """Base class for statistics collection."""

    def __init__(self) -> None:
        """Initialize the stats collector."""
        self.counters: dict[str, int] = {}
        self.timers: dict[str, float] = {}

    def increment(self, counter_name: str, increment: int = 1) -> None:
        """Increment a named counter."""
        if counter_name not in self.counters:
            self.counters[counter_name] = 0
        self.counters[counter_name] += increment

    def get_counter(self, counter_name: str) -> int:
        """Get the value of a counter."""
        return self.counters.get(counter_name, 0)

    def record_time(self, timer_name: str, elapsed_time: float) -> None:
        """Record an elapsed time for a named timer."""
        if timer_name not in self.timers:
            self.timers[timer_name] = 0.0
        self.timers[timer_name] += elapsed_time

    def get_timer(self, timer_name: str) -> float:
        """Get the elapsed time for a timer."""
        return self.timers.get(timer_name, 0.0)
