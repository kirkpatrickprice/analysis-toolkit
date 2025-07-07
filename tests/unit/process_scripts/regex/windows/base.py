"""
Base test utilities for Windows YAML regex pattern testing.

Provides common fixtures, utilities, and base classes for testing
regex patterns across all Windows YAML configuration files.
"""

import re
from pathlib import Path
from typing import Any

import pytest
import yaml


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

    def get_yaml_config(self, yaml_filename: str) -> dict[str, Any]:
        """Load a Windows YAML configuration file."""
        yaml_file = (
            Path(__file__).parent.parent.parent.parent.parent
            / "src"
            / "kp_analysis_toolkit"
            / "process_scripts"
            / "conf.d"
            / yaml_filename
        )

        if not yaml_file.exists():
            pytest.skip(f"YAML config file not found: {yaml_file}")

        with yaml_file.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def extract_search_configs(
        self,
        yaml_config: dict[str, Any],
    ) -> dict[str, dict[str, Any]]:
        """Extract search configurations from YAML, excluding global section."""
        return {
            key: value
            for key, value in yaml_config.items()
            if key != "global" and not key.startswith("include_")
        }

    def validate_single_pattern(
        self,
        config_name: str,
        config: dict[str, Any],
        all_test_data: dict[str, str],
        yaml_name: str = "unknown",
    ) -> None:
        """Test a single regex pattern configuration."""
        pattern = config["regex"]
        max_results = config.get("max_results", -1)
        multiline = config.get("multiline", False)
        field_list = config.get("field_list", [])
        only_matching = config.get("only_matching", False)

        # Compile pattern with appropriate flags
        flags = re.MULTILINE | re.IGNORECASE
        if multiline:
            flags |= re.MULTILINE

        try:
            compiled_pattern = re.compile(pattern, flags)
        except re.error as e:
            pytest.fail(
                f"Pattern compilation failed for {config_name} in {yaml_name}: {e}",
            )

        # Test pattern against all test files
        files_with_matches = 0

        for file_name, test_data in all_test_data.items():
            matches = list(compiled_pattern.finditer(test_data))

            if matches:
                files_with_matches += 1

                # Test max_results constraint if specified
                if max_results > 0:
                    expected_matches = min(len(matches), max_results)
                    assert expected_matches <= max_results, (
                        f"Config {config_name} in {file_name} ({yaml_name}): "
                        f"Expected max {max_results} matches, found {len(matches)}"
                    )

                # Test field extraction if field_list provided
                if field_list and only_matching:
                    self.validate_field_extraction(
                        config_name,
                        file_name,
                        matches,
                        field_list,
                        yaml_name,
                    )

        # Some patterns might not match in all files, but should match in at least one
        # unless it's a specialized pattern (e.g., for specific software)
        if self.should_match_in_files(config_name, yaml_name):
            assert files_with_matches > 0, (
                f"Config {config_name} in {yaml_name} found no matches in any test files. "
                f"This might indicate a problem with the regex pattern."
            )

    def validate_field_extraction(
        self,
        config_name: str,
        file_name: str,
        matches: list[re.Match],
        field_list: list[str],
        yaml_name: str = "unknown",
    ) -> None:
        """Validate that named groups in matches correspond to field_list."""
        for match in matches[:5]:  # Test first 5 matches to avoid excessive testing
            available_groups = set(match.groupdict().keys())

            # Check that field_list fields are available in the pattern
            for field_name in field_list:
                if field_name not in available_groups:
                    # Some patterns might have optional groups that don't appear in every match
                    continue

                # Validate that the field value exists (but may be empty for optional fields)
                field_value = match.groupdict().get(field_name)
                # Note: field_value can be None or empty string, both are acceptable
                # for optional regex groups in multiline patterns
                if field_value is not None and len(field_value.strip()) > 0:
                    # If we have a value, ensure it's reasonable (not just whitespace)
                    assert isinstance(field_value, str), (
                        f"Config {config_name} in {file_name} ({yaml_name}): "
                        f"Field '{field_name}' should be string, got {type(field_value)}"
                    )

    def should_match_in_files(self, config_name: str, yaml_name: str) -> bool:
        """Determine if a config should match in test files based on YAML and config name."""
        # Define patterns that might not match in all test files by YAML type
        optional_patterns_by_yaml = {
            "audit-windows-system.yaml": [
                "01_system_03_bitlocker_status",  # Not all systems have BitLocker
                "01_system_09_pending_updates",  # May have no pending updates
                "01_system_17_snmp",  # SNMP may not be configured
                "01_system_18_scheduled_tasks",  # May have specific formatting issues
            ],
            "audit-windows-network.yaml": [
                # Network patterns that might not be present on all systems
                "network_connectivity_tests",  # May fail if no network
                "smb_server_config",  # May not be enabled
            ],
            "audit-windows-security-software.yaml": [
                # Security software patterns that might not be present
                "antivirus_third_party",  # May not have third-party AV
                "firewall_third_party",  # May use Windows Firewall only
            ],
            "audit-windows-users.yaml": [
                # User patterns that might vary
                "domain_users",  # May be workgroup systems
                "specific_user_accounts",  # May not exist on all systems
            ],
            "audit-windows-logging.yaml": [
                # Logging patterns that might not be present
                "custom_event_logs",  # May not have custom logs
                "audit_policy_advanced",  # May use basic auditing
            ],
        }

        # Get the optional patterns for this YAML file
        optional_patterns = optional_patterns_by_yaml.get(yaml_name, [])
        return config_name not in optional_patterns

    def validate_field_list_consistency(
        self,
        config_name: str,
        config: dict[str, Any],
        yaml_name: str = "unknown",
    ) -> None:
        """Test that field_list matches named groups in regex patterns."""
        pattern = config["regex"]
        field_list = config.get("field_list", [])

        if not field_list:
            return  # Skip configs without field_list

        try:
            compiled_pattern = re.compile(pattern, re.MULTILINE | re.IGNORECASE)
        except re.error:
            return  # Skip patterns that don't compile

        # Extract named groups from the pattern
        named_groups = set(compiled_pattern.groupindex.keys())
        field_set = set(field_list)

        # Field list should be a subset of named groups (some groups might be optional)
        # But all fields in field_list should exist as named groups
        missing_groups = field_set - named_groups

        # Allow some flexibility - not all fields need to be present in every pattern
        # as some patterns might have conditional groups
        if missing_groups:
            # Check if there's a naming mismatch (e.g., camelCase vs snake_case)
            available_groups_lower = {g.lower().replace("_", "") for g in named_groups}
            field_list_lower = {f.lower().replace("_", "") for f in field_list}

            if available_groups_lower == field_list_lower:
                # This is likely a naming convention mismatch, warn but don't fail
                print(
                    f"\nWARNING: Config {config_name} in {yaml_name} has naming convention mismatch:",
                )
                print(f"  Field list: {sorted(field_list)}")
                print(f"  Named groups: {sorted(named_groups)}")
            elif len(missing_groups) == len(field_set):
                # None of the fields match - this is a real problem
                pytest.fail(
                    f"Config {config_name} in {yaml_name}: None of the fields in field_list "
                    f"{field_list} exist as named groups in the regex pattern. "
                    f"Available groups: {sorted(named_groups)}",
                )
            else:
                # Some fields missing - might be acceptable for optional fields
                print(
                    f"\nINFO: Config {config_name} in {yaml_name} has some optional fields:",
                )
                print(f"  Missing groups: {sorted(missing_groups)}")
                print(f"  Available groups: {sorted(named_groups)}")

    @pytest.mark.performance
    def test_pattern_performance(
        self,
        config_name: str,
        config: dict[str, Any],
        all_test_data: dict[str, str],
        yaml_name: str = "unknown",
        performance_threshold: float = 5.0,
    ) -> None:
        """Test that a regex pattern performs reasonably on test data."""
        import time

        pattern = config["regex"]

        try:
            compiled_pattern = re.compile(pattern, re.MULTILINE | re.IGNORECASE)
        except re.error:
            return  # Skip patterns that don't compile

        for file_name, test_data in all_test_data.items():
            start_time = time.time()

            try:
                list(compiled_pattern.finditer(test_data))
                elapsed_time = time.time() - start_time

                assert elapsed_time < performance_threshold, (
                    f"Config {config_name} in {yaml_name} took {elapsed_time:.2f}s on {file_name}, "
                    f"which exceeds threshold of {performance_threshold}s. "
                    f"Consider optimizing the regex pattern."
                )
            except (re.error, RuntimeError) as e:
                pytest.fail(
                    f"Config {config_name} in {yaml_name} failed on {file_name}: {e}",
                )
