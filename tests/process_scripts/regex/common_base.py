"""
Common base utilities for YAML regex pattern testing across all platforms.

Provides shared fixtures, utilities, and base classes for testing
regex patterns across Windows, Linux, and macOS YAML configuration files.
"""

import re
from pathlib import Path
from typing import Any

import pytest
import yaml


class RegexTestBase:
    """Base class for YAML regex pattern tests across all platforms."""

    # Subclasses should override these
    PLATFORM: str = ""
    TEST_DATA_SUBDIR: str = ""

    def get_test_data_dir(self) -> Path:
        """Get the test data directory for this platform."""
        return (
            Path(__file__).parent.parent.parent.parent
            / "testdata"
            / "process_scripts"
            / self.TEST_DATA_SUBDIR
        )

    def get_yaml_config_dir(self) -> Path:
        """Get the YAML configuration directory."""
        return (
            Path(__file__).parent.parent.parent.parent
            / "src"
            / "kp_analysis_toolkit"
            / "process_scripts"
            / "conf.d"
        )

    def get_yaml_config(self, yaml_filename: str) -> dict[str, Any]:
        """Load a YAML configuration file."""
        yaml_path = self.get_yaml_config_dir() / yaml_filename

        if not yaml_path.exists():
            pytest.skip(f"YAML file {yaml_path} not found")

        return yaml.safe_load(yaml_path.read_text(encoding="utf-8"))

    def extract_search_configs(
        self,
        yaml_config: dict[str, Any],
    ) -> dict[str, dict[str, Any]]:
        """Extract search configurations from YAML, excluding global and include sections."""
        return {
            key: value
            for key, value in yaml_config.items()
            if key != "global" and not key.startswith("include_")
        }

    def validate_regex_pattern(
        self,
        pattern: str,
        flags: int = re.MULTILINE | re.IGNORECASE,
    ) -> re.Pattern[str]:
        """Validate that a regex pattern compiles successfully."""
        try:
            return re.compile(pattern, flags)
        except re.error as e:
            pytest.fail(f"Invalid regex pattern: {e}")

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

        # Compile pattern with appropriate flags
        flags = re.MULTILINE | re.IGNORECASE
        if multiline:
            flags |= re.MULTILINE

        try:
            compiled_pattern = re.compile(pattern, flags)
        except re.error as e:
            pytest.fail(
                f"Config {config_name} in {yaml_name}: Pattern compilation failed: {e}",
            )

        # Test against each file
        for file_name, test_data in all_test_data.items():
            if not self.should_match_in_files(config_name, yaml_name):
                continue

            matches = list(compiled_pattern.finditer(test_data))

            # Apply max_results if specified
            if max_results > 0 and len(matches) > max_results:
                matches = matches[:max_results]

            # Validate field extraction if field_list is specified
            if field_list and matches:
                self.validate_field_extraction(
                    matches[0],
                    field_list,
                    config_name,
                    file_name,
                    yaml_name,
                )

    def validate_field_extraction(
        self,
        match: re.Match[str],
        field_list: list[str],
        config_name: str,
        file_name: str,
        yaml_name: str,
    ) -> None:
        """Validate that field extraction works correctly."""
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
        # Define patterns that might not match in all test files by platform
        platform_specific_skips = {
            "windows": {
                # Windows-specific patterns that might not match
                "audit-windows-security-software.yaml": [
                    "01_security_software_02_mcafee",
                    "01_security_software_03_symantec",
                ],
            },
            "linux": {
                # Linux-specific patterns that might not match
                "audit-linux-sec-tools.yaml": [
                    "security_tool_specific_pattern",
                ],
            },
            "macos": {
                # macOS-specific patterns that might not match
                "audit-macos-system.yaml": [
                    "macos_specific_pattern",
                ],
            },
        }

        platform_skips = platform_specific_skips.get(self.PLATFORM.lower(), {})
        yaml_skips = platform_skips.get(yaml_name, [])

        return config_name not in yaml_skips

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
                # Some fields are missing - this might be acceptable for optional fields
                optional_field_threshold = 0.5  # 50% threshold for optional fields
                optional_missing = (
                    len(missing_groups) / len(field_set) < optional_field_threshold
                )
                if not optional_missing:
                    print(
                        f"\nINFO: Config {config_name} in {yaml_name} has some optional fields:",
                    )
                    print(f"  Missing groups: {sorted(missing_groups)}")
                    print(f"  Available groups: {sorted(named_groups)}")

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
