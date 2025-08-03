"""YAML parser implementation for search configurations."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

import yaml

if TYPE_CHECKING:
    from pathlib import Path


class PyYamlParser:
    """Standard YAML parser implementation using PyYAML."""

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
            with file_path.open("r", encoding="utf-8") as file:
                data = yaml.safe_load(file)
                return data if data is not None else {}
        except yaml.YAMLError as e:
            msg = f"Failed to parse YAML file {file_path}: {e}"
            raise ValueError(msg) from e
        except Exception as e:
            msg = f"Failed to read YAML file {file_path}: {e}"
            raise ValueError(msg) from e

    def validate_yaml_structure(self, data: dict[str, str | bool | float]) -> bool:
        """
        Validate basic YAML structure for search configurations.

        Args:
            data: Parsed YAML data to validate

        Returns:
            True if structure is valid, False otherwise

        """
        if not isinstance(data, dict):
            return False

        return self._validate_all_sections(data)

    def _validate_all_sections(self, data: dict[str, str | bool | float]) -> bool:
        """Validate all sections in the YAML data."""
        for key, value in data.items():
            if not self._validate_section(key, value):
                return False
        return True

    def _validate_section(self, key: str, value: str | bool | float) -> bool:
        """Validate a single section of the YAML data."""
        if key == "global":
            return self._validate_global_section(value)
        if key.startswith("include_"):
            return self._validate_include_section(value)
        return self._validate_search_section(value)

    def _validate_global_section(self, value: str | bool | float) -> bool:
        """Validate global configuration section."""
        return isinstance(value, dict)

    def _validate_include_section(self, value: str | bool | float) -> bool:
        """Validate include configuration section."""
        if not isinstance(value, dict) or "files" not in value:
            return False
        return isinstance(value["files"], list)

    def _validate_search_section(self, value: str | bool | float) -> bool:
        """Validate search configuration section."""
        if not isinstance(value, dict):
            return False

        # Must have 'regex' field
        if "regex" not in value:
            return False

        # Validate regex pattern if present
        return self._validate_regex_pattern(value["regex"])

    def _validate_regex_pattern(self, regex: str) -> bool:
        """Validate that the regex pattern is compilable."""
        try:
            re.compile(regex)
            return True
        except re.error:
            return False
