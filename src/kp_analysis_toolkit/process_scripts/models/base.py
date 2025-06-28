"""Base classes and utilities for the KPAT Process Scripts models."""

from collections.abc import Callable, Generator
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING

from pydantic import ConfigDict, field_validator

from kp_analysis_toolkit.models.base import KPATBaseModel
from kp_analysis_toolkit.process_scripts.models.types import SysFilterValueType
from kp_analysis_toolkit.utils.get_file_encoding import detect_encoding
from kp_analysis_toolkit.utils.hash_generator import hash_string

if TYPE_CHECKING:
    from _hashlib import HASH


class EnumStrMixin:
    """Mixin to add case-insensitive string matching to Enum classes."""

    @classmethod
    def _missing_(cls, value: str) -> Enum:
        """
        Handle case when a value doesn't match any enum member.

        This allows for case-insensitive matching when creating enum values from strings.
        Example: MyEnum("windows") will match MyEnum.WINDOWS even though the case differs.

        Args:
            value: The value that didn't match any enum member

        Returns:
            The matching enum value (case-insensitive)

        Raises:
            ValueError: If no case-insensitive match is found

        """
        if isinstance(value, str):
            # Try case-insensitive matching
            for enum_value in cls:
                if value.lower() == enum_value.value.lower():
                    return enum_value

        # If no match was found
        valid_values: str = ", ".join(str(e.value) for e in cls)
        message: str = f"Invalid value '{value}'. Valid values are: {valid_values}"
        raise ValueError(message)


class PathValidationMixin:
    """Mixin providing path validation methods."""

    @classmethod
    def validate_path_exists(cls, path: Path | str) -> Path:
        """Validate that a path exists and return its absolute path."""
        if isinstance(path, str):
            path = Path(path)

        if not path.exists():
            message: str = f"Path {path} does not exist"
            raise ValueError(message)
        return path.absolute()

    @classmethod
    def validate_file_exists(cls, file: Path | str) -> Path:
        """Validate that a file exists and return its absolute path."""
        path: Path = cls.validate_path_exists(file)
        if not path.is_file():
            message: str = f"Path {path} is not a file"
            raise ValueError(message)
        return path

    @classmethod
    def validate_directory_exists(cls, dir_path: Path | str) -> Path:
        """Validate that a directory exists and return its absolute path."""
        path: Path = cls.validate_path_exists(dir_path)
        if not path.is_dir():
            message: str = f"Path {path} is not a directory"
            raise ValueError(message)
        return path


class ValidationMixin:
    """Mixin providing common validation methods."""

    @classmethod
    def validate_positive_integer(
        cls,
        value: int,
        *,
        allow_neg_one: bool = False,
    ) -> int:
        """Validate that a value is a positive integer."""
        if allow_neg_one and value == -1:
            return value

        if value <= 0:
            message: str = f"Value {value} must be a positive integer"
            raise ValueError(message)
        return value

    @classmethod
    def validate_non_empty_string(cls, value: str | None) -> str | None:
        """Validate that a string is not empty if provided."""
        if value is not None and value.strip() == "":
            message: str = "String cannot be empty"
            raise ValueError(message)
        return value

    @classmethod
    def validate_sys_filter_value(
        cls,
        value: SysFilterValueType,
        comp_op: str,
        *,
        collection_allowed: bool = True,
    ) -> SysFilterValueType:
        """Validate filter value based on comparison operator."""
        if not collection_allowed and isinstance(value, list | set):
            message: str = f"Operator '{comp_op}' cannot be used with collection values"
            raise ValueError(message)

        if collection_allowed and not isinstance(value, list | set):
            message: str = f"Operator '{comp_op}' requires a collection value"
            raise ValueError(message)

        return value


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
