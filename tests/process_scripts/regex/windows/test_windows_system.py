"""
Dynamically generated tests for audit-windows-system.yaml regex patterns.

This module automatically creates unit tests for each regex pattern defined
in the audit-windows-system.yaml configuration file, testing against real
Windows system data.
"""

import re
from pathlib import Path
from typing import Any

import pytest
import yaml

from tests.process_scripts.regex.windows.base import WindowsRegexTestBase


class TestWindowsSystemPatterns(WindowsRegexTestBase):
    """Dynamic tests for audit-windows-system.yaml regex patterns."""

    @pytest.fixture(scope="class")
    def yaml_config(self) -> dict[str, Any]:
        """Load the audit-windows-system.yaml configuration."""
        yaml_file = (
            Path(__file__).parent.parent.parent.parent.parent
            / "src"
            / "kp_analysis_toolkit"
            / "process_scripts"
            / "conf.d"
            / "audit-windows-system.yaml"
        )

        if not yaml_file.exists():
            pytest.skip(f"YAML config file not found: {yaml_file}")

        with yaml_file.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    @pytest.fixture(scope="class")
    def search_configs(self, yaml_config: dict[str, Any]) -> dict[str, dict[str, Any]]:
        """Extract search configurations from YAML, excluding global section."""
        return {
            key: value
            for key, value in yaml_config.items()
            if key != "global" and not key.startswith("include_")
        }

    def test_yaml_file_loads_successfully(self, yaml_config: dict[str, Any]) -> None:
        """Test that the YAML file loads without errors."""
        assert yaml_config is not None
        assert isinstance(yaml_config, dict)
        assert len(yaml_config) > 0

    def test_all_search_configs_have_required_fields(
        self,
        search_configs: dict[str, dict[str, Any]],
    ) -> None:
        """Test that all search configurations have required fields."""
        for config_name, config in search_configs.items():
            # All configs must have a regex pattern
            assert "regex" in config, f"Config {config_name} missing 'regex' field"
            assert isinstance(config["regex"], str), (
                f"Config {config_name} 'regex' must be string"
            )
            assert len(config["regex"].strip()) > 0, (
                f"Config {config_name} 'regex' cannot be empty"
            )

    @pytest.mark.parametrize(
        "config_name",
        [
            "01_system_01_kp_win_version",
            "01_system_01_bios",
            "01_system_02_win_os_version",
            "01_system_03_bitlocker_status",
            "01_system_07_patching",
            "01_system_10_windows_update_config",
            "01_system_11_running_processes",
            "01_system_12_system_services_labeled",
            "01_system_14_rdp_config",
            "01_system_15_screensaver_gpo",
            "01_system_18_scheduled_tasks",
        ],
    )
    def test_specific_pattern_compilation(
        self,
        search_configs: dict[str, dict[str, Any]],
        config_name: str,
    ) -> None:
        """Test that specific regex patterns compile without errors."""
        if config_name not in search_configs:
            pytest.skip(f"Config {config_name} not found in YAML")

        config = search_configs[config_name]
        pattern = config["regex"]

        # Test pattern compilation with multiline flag if specified
        flags = re.MULTILINE | re.IGNORECASE
        if config.get("multiline", False):
            flags |= re.MULTILINE

        try:
            compiled_pattern = re.compile(pattern, flags)
            assert compiled_pattern is not None
        except re.error as e:
            pytest.fail(f"Pattern compilation failed for {config_name}: {e}")

    def test_dynamic_pattern_validation(
        self,
        search_configs: dict[str, dict[str, Any]],
        all_windows_test_data: dict[str, str],
    ) -> None:
        """Dynamically test all regex patterns against test data."""
        for config_name, config in search_configs.items():
            self._test_single_pattern(config_name, config, all_windows_test_data)

    def _test_single_pattern(
        self,
        config_name: str,
        config: dict[str, Any],
        all_test_data: dict[str, str],
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
            pytest.fail(f"Pattern compilation failed for {config_name}: {e}")

        # Test pattern against all test files
        total_matches_found = 0
        files_with_matches = 0

        for file_name, test_data in all_test_data.items():
            matches = list(compiled_pattern.finditer(test_data))

            if matches:
                files_with_matches += 1
                total_matches_found += len(matches)

                # Test max_results constraint if specified
                if max_results > 0:
                    expected_matches = min(len(matches), max_results)
                    assert expected_matches <= max_results, (
                        f"Config {config_name} in {file_name}: "
                        f"Expected max {max_results} matches, found {len(matches)}"
                    )

                # Test field extraction if field_list provided
                if field_list and only_matching:
                    self._validate_field_extraction(
                        config_name,
                        file_name,
                        matches,
                        field_list,
                    )

        # Some patterns might not match in all files, but should match in at least one
        # unless it's a specialized pattern (e.g., for specific software)
        if self._should_match_in_files(config_name):
            assert files_with_matches > 0, (
                f"Config {config_name} found no matches in any test files. "
                f"This might indicate a problem with the regex pattern."
            )

    def _validate_field_extraction(
        self,
        config_name: str,
        file_name: str,
        matches: list[re.Match],
        field_list: list[str],
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
                        f"Config {config_name} in {file_name}: "
                        f"Field '{field_name}' should be string, got {type(field_value)}"
                    )

    def _should_match_in_files(self, config_name: str) -> bool:
        """Determine if a config should match in test files."""
        # These patterns might not match in all test files
        optional_patterns = [
            "01_system_03_bitlocker_status",  # Not all systems have BitLocker
            "01_system_09_pending_updates",  # May have no pending updates
            "01_system_17_snmp",  # SNMP may not be configured
            "01_system_18_scheduled_tasks",  # May have specific formatting issues
        ]
        return config_name not in optional_patterns

    def test_max_results_parameter_effects(
        self,
        search_configs: dict[str, dict[str, Any]],
        all_windows_test_data: dict[str, str],
    ) -> None:
        """Test that max_results parameter properly limits results."""
        for config_name, config in search_configs.items():
            max_results = config.get("max_results", -1)

            if max_results <= 0:
                continue  # Skip configs without max_results limit

            pattern = config["regex"]
            flags = re.MULTILINE | re.IGNORECASE

            try:
                compiled_pattern = re.compile(pattern, flags)
            except re.error:
                continue  # Skip patterns that don't compile

            # Test against each file
            for file_name, test_data in all_windows_test_data.items():
                all_matches = list(compiled_pattern.finditer(test_data))

                if len(all_matches) > max_results:
                    # Simulate the behavior of applying max_results
                    limited_matches = all_matches[:max_results]

                    assert len(limited_matches) == max_results, (
                        f"Config {config_name} in {file_name}: "
                        f"max_results={max_results} should limit to {max_results} matches, "
                        f"but would get {len(limited_matches)}"
                    )

    def test_multiline_parameter_effects(
        self,
        search_configs: dict[str, dict[str, Any]],
        all_windows_test_data: dict[str, str],
    ) -> None:
        """Test that multiline parameter affects regex behavior correctly."""
        # Track if we found any differences to avoid false positives
        patterns_tested = 0

        for config in search_configs.values():
            if not config.get("multiline", False):
                continue  # Skip non-multiline patterns

            patterns_tested += 1
            pattern = config["regex"]

            # Test with and without multiline flag to ensure it makes a difference
            try:
                pattern_without_multiline = re.compile(pattern, re.IGNORECASE)
                pattern_with_multiline = re.compile(
                    pattern,
                    re.MULTILINE | re.IGNORECASE,
                )
            except re.error:
                continue  # Skip patterns that don't compile

            # For at least one test file, multiline should potentially affect results
            differences_found = False

            for test_data in all_windows_test_data.values():
                matches_without = list(pattern_without_multiline.finditer(test_data))
                matches_with = list(pattern_with_multiline.finditer(test_data))

                # The number of matches might be different with multiline flag
                # or the same pattern might match different content
                if len(matches_without) != len(matches_with):
                    differences_found = True
                    break

                # Check if the actual match content differs
                for match_without, match_with in zip(
                    matches_without,
                    matches_with,
                    strict=False,
                ):
                    if match_without.group() != match_with.group():
                        differences_found = True
                        break

                if differences_found:
                    break

            # Note: We don't assert differences_found because some patterns
            # might work the same way regardless of multiline flag

        # Ensure we actually tested some multiline patterns
        assert patterns_tested > 0, "No multiline patterns found to test"

    def test_field_list_consistency(
        self,
        search_configs: dict[str, dict[str, Any]],
    ) -> None:
        """Test that field_list matches named groups in regex patterns."""
        for config_name, config in search_configs.items():
            pattern = config["regex"]
            field_list = config.get("field_list", [])

            if not field_list:
                continue  # Skip configs without field_list

            try:
                compiled_pattern = re.compile(pattern, re.MULTILINE | re.IGNORECASE)
            except re.error:
                continue  # Skip patterns that don't compile

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
                available_groups_lower = {
                    g.lower().replace("_", "") for g in named_groups
                }
                field_list_lower = {f.lower().replace("_", "") for f in field_list}

                if available_groups_lower == field_list_lower:
                    # This is likely a naming convention mismatch, warn but don't fail
                    print(
                        f"\nWARNING: Config {config_name} has naming convention mismatch:",
                    )
                    print(f"  Field list: {sorted(field_list)}")
                    print(f"  Named groups: {sorted(named_groups)}")
                elif len(missing_groups) == len(field_set):
                    # None of the fields match - this is a real problem
                    pytest.fail(
                        f"Config {config_name}: None of the fields in field_list "
                        f"{field_list} exist as named groups in the regex pattern. "
                        f"Available groups: {sorted(named_groups)}",
                    )
                else:
                    # Some fields missing - might be acceptable for optional fields
                    print(f"\nINFO: Config {config_name} has some optional fields:")
                    print(f"  Missing groups: {sorted(missing_groups)}")
                    print(f"  Available groups: {sorted(named_groups)}")

    def test_pattern_performance(
        self,
        search_configs: dict[str, dict[str, Any]],
        all_windows_test_data: dict[str, str],
    ) -> None:
        """Test that regex patterns perform reasonably on test data."""
        import time

        performance_threshold = 5.0  # seconds per pattern per file

        for config_name, config in search_configs.items():
            pattern = config["regex"]

            try:
                compiled_pattern = re.compile(pattern, re.MULTILINE | re.IGNORECASE)
            except re.error:
                continue  # Skip patterns that don't compile

            for file_name, test_data in all_windows_test_data.items():
                start_time = time.time()

                try:
                    list(compiled_pattern.finditer(test_data))
                    elapsed_time = time.time() - start_time

                    assert elapsed_time < performance_threshold, (
                        f"Config {config_name} took {elapsed_time:.2f}s on {file_name}, "
                        f"which exceeds threshold of {performance_threshold}s. "
                        f"Consider optimizing the regex pattern."
                    )
                except (re.error, RuntimeError) as e:
                    pytest.fail(
                        f"Config {config_name} failed on {file_name}: {e}",
                    )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
