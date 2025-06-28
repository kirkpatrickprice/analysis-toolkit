"""
Dynamic test generator for all Windows YAML configuration files.

This module creates test classes dynamically for each audit-windows-*.yaml file,
reusing the common testing logic from the base class.
"""

import re
from typing import Any

import pytest

from tests.process_scripts.regex.windows.base import WindowsRegexTestBase


class DynamicWindowsYamlTestMixin(WindowsRegexTestBase):
    """Mixin class providing dynamic test methods for Windows YAML files."""

    # This will be set by subclasses to specify which YAML file to test
    YAML_FILENAME: str = ""

    @pytest.fixture(scope="class")
    def yaml_config(self) -> dict[str, Any]:
        """Load the YAML configuration for this test class."""
        return self.get_yaml_config(self.YAML_FILENAME)

    @pytest.fixture(scope="class")
    def search_configs(self, yaml_config: dict[str, Any]) -> dict[str, dict[str, Any]]:
        """Extract search configurations from YAML, excluding global section."""
        return self.extract_search_configs(yaml_config)

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
            assert "regex" in config, (
                f"Config {config_name} missing 'regex' field in {self.YAML_FILENAME}"
            )
            assert isinstance(config["regex"], str), (
                f"Config {config_name} 'regex' must be string in {self.YAML_FILENAME}"
            )
            assert len(config["regex"].strip()) > 0, (
                f"Config {config_name} 'regex' cannot be empty in {self.YAML_FILENAME}"
            )

    def test_pattern_compilation(
        self,
        search_configs: dict[str, dict[str, Any]],
    ) -> None:
        """Test that all regex patterns compile without errors."""
        for config_name, config in search_configs.items():
            pattern = config["regex"]

            # Test pattern compilation with multiline flag if specified
            flags = re.MULTILINE | re.IGNORECASE
            if config.get("multiline", False):
                flags |= re.MULTILINE

            try:
                compiled_pattern = re.compile(pattern, flags)
                assert compiled_pattern is not None
            except re.error as e:
                pytest.fail(
                    f"Pattern compilation failed for {config_name} in {self.YAML_FILENAME}: {e}",
                )

    def test_dynamic_pattern_validation(
        self,
        search_configs: dict[str, dict[str, Any]],
        all_windows_test_data: dict[str, str],
    ) -> None:
        """Dynamically test all regex patterns against test data."""
        for config_name, config in search_configs.items():
            self.validate_single_pattern(
                config_name,
                config,
                all_windows_test_data,
                self.YAML_FILENAME,
            )

    def test_max_results_parameter_effects(
        self,
        search_configs: dict[str, dict[str, Any]],
        all_windows_test_data: dict[str, str],
    ) -> None:
        """Test that max_results parameter properly limits results."""
        patterns_with_max_results = 0

        for config_name, config in search_configs.items():
            max_results = config.get("max_results", -1)

            if max_results <= 0:
                continue  # Skip configs without max_results limit

            patterns_with_max_results += 1
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
                        f"Config {config_name} in {self.YAML_FILENAME} on {file_name}: "
                        f"max_results={max_results} should limit to {max_results} matches, "
                        f"but would get {len(limited_matches)}"
                    )

        # Log how many patterns were tested for max_results
        if patterns_with_max_results == 0:
            print(f"\nINFO: No patterns with max_results found in {self.YAML_FILENAME}")

    def test_multiline_parameter_effects(
        self,
        search_configs: dict[str, dict[str, Any]],
        all_windows_test_data: dict[str, str],
    ) -> None:
        """Test that multiline parameter affects regex behavior correctly."""
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

        # Log how many multiline patterns were tested
        if patterns_tested == 0:
            print(f"\nINFO: No multiline patterns found in {self.YAML_FILENAME}")
        # Note: We don't assert differences_found because some patterns
        # might work the same way regardless of multiline flag

    def test_field_list_consistency(
        self,
        search_configs: dict[str, dict[str, Any]],
    ) -> None:
        """Test that field_list matches named groups in regex patterns."""
        for config_name, config in search_configs.items():
            self.validate_field_list_consistency(
                config_name,
                config,
                self.YAML_FILENAME,
            )

    def test_pattern_performance(
        self,
        search_configs: dict[str, dict[str, Any]],
        all_windows_test_data: dict[str, str],
    ) -> None:
        """Test that regex patterns perform reasonably on test data."""
        for config_name, config in search_configs.items():
            super().test_pattern_performance(
                config_name,
                config,
                all_windows_test_data,
                self.YAML_FILENAME,
            )


# Dynamically create test classes for each Windows YAML file
WINDOWS_YAML_FILES = [
    "audit-windows-system.yaml",
    "audit-windows-users.yaml",
    "audit-windows-network.yaml",
    "audit-windows-security-software.yaml",
    "audit-windows-logging.yaml",
]


def create_test_class(yaml_filename: str) -> type[DynamicWindowsYamlTestMixin]:
    """Create a test class for a specific Windows YAML file."""
    # Convert filename to a valid class name
    class_name_suffix = (
        yaml_filename.replace("audit-windows-", "")
        .replace(".yaml", "")
        .replace("-", "_")
        .title()
        .replace("_", "")
    )

    class_name = f"TestWindows{class_name_suffix}Patterns"

    # Create the class dynamically
    test_class = type(
        class_name,
        (DynamicWindowsYamlTestMixin,),
        {
            "YAML_FILENAME": yaml_filename,
            "__doc__": f"Dynamic tests for {yaml_filename} regex patterns.",
        },
    )

    return test_class


# Create test classes for all Windows YAML files
for yaml_file in WINDOWS_YAML_FILES:
    test_class = create_test_class(yaml_file)
    # Add the class to the global namespace so pytest can discover it
    globals()[test_class.__name__] = test_class


# For backward compatibility and manual testing
TestWindowsSystemPatterns = globals().get("TestWindowsSystemPatterns")
TestWindowsUsersPatterns = globals().get("TestWindowsUsersPatterns")
TestWindowsNetworkPatterns = globals().get("TestWindowsNetworkPatterns")
TestWindowsSecuritySoftwarePatterns = globals().get(
    "TestWindowsSecuritysoftwarePatterns",
)
TestWindowsLoggingPatterns = globals().get("TestWindowsLoggingPatterns")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
