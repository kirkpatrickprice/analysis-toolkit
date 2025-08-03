"""YAML parser implementation for search configurations."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

import yaml

if TYPE_CHECKING:
    from pathlib import Path

    from kp_analysis_toolkit.core.services.file_processing.service import (
        FileProcessingService,
    )


class PyYamlParser:
    """Standard YAML parser implementation using PyYAML."""

    def __init__(self, file_processing: FileProcessingService) -> None:
        """Initialize with core file processing service."""
        self.file_processing: FileProcessingService = file_processing

    def load_yaml(self, file_path: Path) -> dict[str, str | bool | float]:
        """
        Load YAML file and return parsed data as dictionary.

        Args:
            file_path: Path to the YAML file to load

        Returns:
            Dictionary containing parsed YAML data

        Raises:
            ValueError: If file cannot be loaded or parsed
            FileNotFoundError: If file doesn't exist

        """
        if not file_path.exists():
            msg = f"YAML file not found: {file_path}"
            raise FileNotFoundError(msg)

        try:
            encoding: str = self.file_processing.detect_encoding(file_path)
            with file_path.open("r", encoding=encoding) as file:
                data = yaml.safe_load(file)
                return data if data is not None else {}
        except yaml.YAMLError as e:
            msg = f"Failed to parse YAML file {file_path}: {e}"
            raise ValueError(msg) from e
        except Exception as e:
            msg = f"Failed to read YAML file {file_path}: {e}"
            raise ValueError(msg) from e

    def validate_yaml_structure(
        self,
        data: dict[str, str | bool | float],
    ) -> None:
        """
        Validate basic YAML structure for search configurations with detailed error messages.

        Args:
            data: Parsed YAML data to validate

        Raises:
            TypeError: If data type is incorrect
            ValueError: If structure is invalid, with specific details about what's wrong

        """
        if not isinstance(data, dict):
            msg = "YAML data must be a dictionary"
            raise TypeError(msg)

        self._validate_all_sections(data)

    def _validate_all_sections(
        self,
        data: dict[str, str | bool | float],
    ) -> None:
        """Validate all sections in the YAML data with detailed error messages."""
        for key, value in data.items():
            try:
                self._validate_section(key, value)
            except (ValueError, TypeError) as e:
                msg = f"Validation failed for section '{key}': {e}"
                raise ValueError(msg) from e

    def _validate_section(self, key: str, value: str | bool | float) -> None:
        """Validate a single section of the YAML data with detailed error messages."""
        if key == "global":
            self._validate_global_section(value)
        elif key.startswith("include_"):
            self._validate_include_section(value)
        else:
            self._validate_search_section(value)

    def _validate_global_section(self, value: str | bool | float) -> None:
        """Validate global configuration section with detailed error messages."""
        if not isinstance(value, dict):
            msg = "Global section must be a dictionary"
            raise TypeError(msg)

    def _validate_include_section(self, value: str | bool | float) -> None:
        """Validate include configuration section with detailed error messages."""
        if not isinstance(value, dict):
            msg = "Include section must be a dictionary"
            raise TypeError(msg)

        if "files" not in value:
            msg = "Include section must contain a 'files' key"
            raise ValueError(msg)

        if not isinstance(value["files"], list):
            msg = "Include section 'files' must be a list"
            raise TypeError(msg)

    def _validate_search_section(self, value: str | bool | float) -> None:
        """Validate search configuration section with detailed error messages."""
        if not isinstance(value, dict):
            msg = "Search section must be a dictionary"
            raise TypeError(msg)

        # Must-have fields
        required_fields: list[str] = [
            "regex",
            "excel_sheet_name",
            "comment",
            "keywords",
        ]

        missing_fields: list[str] = []
        for field in required_fields:
            if field not in value:
                missing_fields.append(field)

        if missing_fields:
            fields_str = ", ".join(f"'{field}'" for field in missing_fields)
            msg = f"Search section is missing required fields: {fields_str}"
            raise ValueError(msg)

        # Validate regex pattern
        try:
            self._validate_regex_pattern(value["regex"])
        except ValueError as e:
            msg = f"Invalid regex pattern: {e}"
            raise ValueError(msg) from e

    def _validate_regex_pattern(self, regex: str) -> None:
        """Validate that the regex pattern is compilable with detailed error messages."""
        if not isinstance(regex, str):
            msg = f"Regex pattern must be a string, got {type(regex).__name__}"
            raise TypeError(msg)

        try:
            re.compile(regex)
        except re.error as e:
            msg = f"Invalid regex pattern '{regex}': {e}"
            raise ValueError(msg) from e
