# AI-GEN: CopilotChat|2025-07-31|KPAT-ListSystems|reviewed:no
"""Mixin classes for process scripts models."""

from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Import types only when type checking to avoid circular imports
    from kp_analysis_toolkit.process_scripts.models.types import SysFilterValueType


class EnumStrMixin:
    """Mixin to add case-insensitive string matching to Enum classes."""

    @classmethod
    def _missing_(cls, value: str) -> Enum:
        """
        Handle case when a value doesn't match any enum member.

        This allows for case-insensitive matching when creating enum values from strings.
        Example: MyEnum("windows") will match MyEnum.WINDOWS even though the case differs.

        Args:
            value: The string value to search for

        Returns:
            The matching enum member

        Raises:
            ValueError: If no case-insensitive match is found

        """
        for member in cls:
            if member.value.lower() == value.lower():
                return member
        msg = f"{value!r} is not a valid {cls.__name__}"
        raise ValueError(msg)


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
        value: "SysFilterValueType",
        comp_op: str,
        *,
        collection_allowed: bool = True,
    ) -> "SysFilterValueType":
        """Validate filter value based on comparison operator."""
        if not collection_allowed and isinstance(value, list | set):
            message: str = f"Operator '{comp_op}' cannot be used with collection values"
            raise ValueError(message)

        if collection_allowed and not isinstance(value, list | set):
            message: str = f"Operator '{comp_op}' requires a collection value"
            raise ValueError(message)

        return value


# END AI-GEN
