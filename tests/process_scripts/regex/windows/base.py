"""
Base test utilities for Windows YAML regex pattern testing.

Provides common fixtures, utilities, and base classes for testing
regex patterns across all Windows YAML configuration files.
"""

import re
from pathlib import Path
from typing import Any

import pytest


class WindowsRegexTestBase:
    """Base class for Windows YAML regex pattern tests."""

    @pytest.fixture
    def windows_test_files(self) -> dict[str, Path]:
        """Get all Windows test data files."""
        test_dir: Path = (
            Path(__file__).parent.parent.parent.parent.parent
            / "testdata"
            / "process_scripts"
            / "windows"
        )

        return {
            "windows10pro": test_dir / "windows10pro-cb19044-kp0.4.7.txt",
            "windows11": test_dir / "windows11-0.4.8.txt",
            "windows2016": test_dir / "windows2016-cb14393-kp0.4.4-1.txt",
            "windows2022": test_dir / "windows2022-cb20348-kp0.4.7.txt",
        }

    @pytest.fixture
    def all_windows_test_data(
        self,
        windows_test_files: dict[str, Path],
    ) -> dict[str, str]:
        """Load content from all Windows test data files."""
        test_data = {}
        for name, file_path in windows_test_files.items():
            if file_path.exists():
                test_data[name] = file_path.read_text(encoding="utf-8")
            else:
                pytest.skip(f"Test file {file_path} not found")
        return test_data

    def validate_regex_pattern(
        self,
        pattern: str | re.Pattern,
        test_data: str,
        expected_groups: list[str] | None = None,
        min_matches: int = 0,
        max_matches: int | None = None,
    ) -> list[re.Match]:
        """
        Validate a regex pattern against test data.

        Args:
            pattern: Regex pattern string or compiled pattern
            test_data: Test data to search in
            expected_groups: List of expected named groups
            min_matches: Minimum number of matches expected
            max_matches: Maximum number of matches expected (None = unlimited)

        Returns:
            List of regex matches found

        """
        if isinstance(pattern, str):
            compiled_pattern = re.compile(pattern, re.MULTILINE)
        else:
            compiled_pattern = pattern

        matches = list(compiled_pattern.finditer(test_data))

        # Validate match count
        assert len(matches) >= min_matches, (
            f"Expected at least {min_matches} matches, got {len(matches)}"
        )
        if max_matches is not None:
            assert len(matches) <= max_matches, (
                f"Expected at most {max_matches} matches, got {len(matches)}"
            )

        # Validate expected groups exist in pattern
        if expected_groups and matches:
            first_match = matches[0]
            available_groups = set(first_match.groupdict().keys())
            expected_set = set(expected_groups)
            missing_groups = expected_set - available_groups
            assert not missing_groups, f"Missing expected groups: {missing_groups}"

        return matches

    def extract_named_groups(self, matches: list[re.Match]) -> dict[str, Any]:
        """
        Extract all named groups from regex matches.

        Args:
            matches: List of regex matches

        Returns:
            Dictionary with all extracted named group values

        """
        extracted_data = {}
        for match in matches:
            for key, value in match.groupdict().items():
                if value is not None:
                    extracted_data[key] = value.strip()
        return extracted_data

    def _test_pattern_against_all_files(
        self,
        pattern: str | re.Pattern,
        all_test_data: dict[str, str],
        expected_groups: list[str] | None = None,
        *,
        require_matches_in_all_files: bool = False,
    ) -> dict[str, list[re.Match]]:
        """
        Test a regex pattern against all test data files.

        Args:
            pattern: Regex pattern to test
            all_test_data: Dictionary of test data by file name
            expected_groups: Expected named groups in the pattern
            require_matches_in_all_files: Whether pattern must match in all files

        Returns:
            Dictionary of matches by file name

        """
        all_matches = {}
        files_with_matches = 0

        for file_name, test_data in all_test_data.items():
            matches = self.validate_regex_pattern(
                pattern=pattern,
                test_data=test_data,
                expected_groups=expected_groups,
                min_matches=0,  # Don't require matches in individual files
            )
            all_matches[file_name] = matches
            if matches:
                files_with_matches += 1

        if require_matches_in_all_files:
            assert files_with_matches == len(all_test_data), (
                f"Pattern should match in all {len(all_test_data)} files, but only matched in {files_with_matches}"
            )
        else:
            # At least one file should have matches for the pattern to be valid
            assert files_with_matches > 0, (
                "Pattern should match in at least one test file"
            )

        return all_matches

    def assert_field_values(  # noqa: PLR0913
        self,
        extracted_data: dict[str, Any],
        field_name: str,
        *,
        expected_value: str | None = None,
        expected_type: type | None = None,
        allowed_values: list[str] | None = None,
        regex_pattern: str | None = None,
    ) -> None:
        """
        Assert properties of extracted field values.

        Args:
            extracted_data: Dictionary of extracted field data
            field_name: Name of field to validate
            expected_value: Exact value expected (if any)
            expected_type: Expected type of value
            allowed_values: List of allowed values
            regex_pattern: Regex pattern the value should match

        """
        assert field_name in extracted_data, (
            f"Field '{field_name}' not found in extracted data"
        )

        value = extracted_data[field_name]

        if expected_value is not None:
            assert value == expected_value, (
                f"Field '{field_name}' expected '{expected_value}', got '{value}'"
            )

        if expected_type is not None:
            if expected_type is int:
                assert value.isdigit(), (
                    f"Field '{field_name}' should be numeric, got '{value}'"
                )
            elif expected_type is str:
                assert isinstance(value, str), (
                    f"Field '{field_name}' should be string, got {type(value)}"
                )

        if allowed_values is not None:
            assert value in allowed_values, (
                f"Field '{field_name}' value '{value}' not in allowed values {allowed_values}"
            )

        if regex_pattern is not None:
            pattern = re.compile(regex_pattern)
            assert pattern.match(value), (
                f"Field '{field_name}' value '{value}' doesn't match pattern '{regex_pattern}'"
            )
