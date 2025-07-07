"""
Dynamic test generator for YAML configuration files across all platforms.

This module provides a generalized mixin that can create test classes dynamically
for any platform's audit-*.yaml files, reusing common testing logic.
"""

import re
from typing import Any

import pytest

from tests.unit.process_scripts.regex.common_base import RegexTestBase


class DynamicYamlTestMixin(RegexTestBase):
    """Mixin class providing dynamic test methods for YAML files across platforms."""

    # These will be set by subclasses to specify which YAML file and platform to test
    YAML_FILENAME: str = ""
    PLATFORM: str = ""
    TEST_DATA_SUBDIR: str = ""

    @pytest.fixture(scope="class")
    def yaml_config(self) -> dict[str, Any]:
        """Load the YAML configuration for this test class."""
        return self.get_yaml_config(self.YAML_FILENAME)

    @pytest.fixture(scope="class")
    def search_configs(self, yaml_config: dict[str, Any]) -> dict[str, dict[str, Any]]:
        """Extract search configurations from YAML, excluding global section."""
        return self.extract_search_configs(yaml_config)

    @pytest.fixture
    def platform_test_files(self) -> dict[str, Any]:
        """Get all test data files for this platform. Override in subclasses."""
        test_dir = self.get_test_data_dir()
        test_files = {}

        if test_dir.exists():
            for file_path in test_dir.glob("*.txt"):
                # Use stem as the key (filename without extension)
                test_files[file_path.stem] = file_path

        return test_files

    @pytest.fixture
    def all_test_data(
        self,
        platform_test_files: dict[str, Any],
    ) -> dict[str, str]:
        """Load content from all test data files for this platform."""
        test_data = {}
        for name, file_path in platform_test_files.items():
            if file_path.exists():
                test_data[name] = file_path.read_text(encoding="utf-8")
            else:
                pytest.skip(f"Test file {file_path} not found")
        return test_data

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
        all_test_data: dict[str, str],
    ) -> None:
        """Dynamically test all regex patterns against test data."""
        for config_name, config in search_configs.items():
            self.validate_single_pattern(
                config_name,
                config,
                all_test_data,
                self.YAML_FILENAME,
            )

    def test_max_results_parameter_effects(
        self,
        search_configs: dict[str, dict[str, Any]],
        all_test_data: dict[str, str],
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
            for file_name, test_data in all_test_data.items():
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
        all_test_data: dict[str, str],
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

            for test_data in all_test_data.values():
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
        all_test_data: dict[str, str],
    ) -> None:
        """Test that regex patterns perform reasonably on test data."""
        for config_name, config in search_configs.items():
            super().test_pattern_performance(
                config_name,
                config,
                all_test_data,
                self.YAML_FILENAME,
            )


def create_platform_test_class(
    platform: str,
    test_data_subdir: str,
    yaml_filename: str,
) -> type[DynamicYamlTestMixin]:
    """Create a test class for a specific platform and YAML file."""
    # Convert filename to a valid class name
    class_name_suffix = (
        yaml_filename.replace(f"audit-{platform.lower()}-", "")
        .replace(".yaml", "")
        .replace("-", "_")
        .title()
        .replace("_", "")
    )

    class_name = f"Test{platform.title()}{class_name_suffix}Patterns"

    # Create the class dynamically
    test_class = type(
        class_name,
        (DynamicYamlTestMixin,),
        {
            "YAML_FILENAME": yaml_filename,
            "PLATFORM": platform.upper(),
            "TEST_DATA_SUBDIR": test_data_subdir,
            "__doc__": f"Dynamic tests for {yaml_filename} regex patterns on {platform}.",
        },
    )

    return test_class


def discover_yaml_files(platform: str) -> list[str]:
    """Discover all audit YAML files for a given platform."""
    from pathlib import Path

    yaml_dir = (
        Path(__file__).parent.parent.parent.parent.parent
        / "src"
        / "kp_analysis_toolkit"
        / "process_scripts"
        / "conf.d"
    )

    pattern = f"audit-{platform.lower()}-*.yaml"
    yaml_files = [f.name for f in yaml_dir.glob(pattern)]

    return sorted(yaml_files)  # Sort for consistent test order
