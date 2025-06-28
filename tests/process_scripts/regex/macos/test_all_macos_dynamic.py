"""
Dynamic test generator for all macOS YAML configuration files.

This module creates test classes dynamically for each audit-macos-*.yaml file,
reusing the common testing logic from the generalized base classes.
"""

from pathlib import Path

import pytest

from tests.process_scripts.regex.dynamic_test_generator import (
    DynamicYamlTestMixin,
    create_platform_test_class,
    discover_yaml_files,
)


class MacOSSpecificTestMixin(DynamicYamlTestMixin):
    """macOS-specific test mixin that extends the common functionality."""

    PLATFORM = "MACOS"
    TEST_DATA_SUBDIR = "macos"

    @pytest.fixture
    def platform_test_files(self) -> dict[str, Path]:
        """Get all macOS test data files with specific naming."""
        test_dir = self.get_test_data_dir()

        return {
            "macos1331": test_dir / "macos-13.3.1-kp0.1.0.txt",
            "macos1341": test_dir / "macos-13.4.1-kp0.1.0.txt",
        }


# Discover and create test classes for all macOS YAML files
MACOS_YAML_FILES = discover_yaml_files("macos")

for yaml_file in MACOS_YAML_FILES:
    test_class = create_platform_test_class("macos", "macos", yaml_file)

    # Override with macOS-specific mixin if needed
    enhanced_class = type(
        test_class.__name__,
        (MacOSSpecificTestMixin,),
        {
            "YAML_FILENAME": yaml_file,
            "PLATFORM": "MACOS",
            "TEST_DATA_SUBDIR": "macos",
            "__doc__": f"Dynamic tests for {yaml_file} regex patterns on macOS.",
        },
    )

    # Add the class to the global namespace so pytest can discover it
    globals()[enhanced_class.__name__] = enhanced_class


# For backward compatibility and manual testing
TestMacosSystemPatterns = globals().get("TestMacosSystemPatterns")
TestMacosUsersPatterns = globals().get("TestMacosUsersPatterns")
TestMacosNetworkPatterns = globals().get("TestMacosNetworkPatterns")
TestMacosLoggingPatterns = globals().get("TestMacosLoggingPatterns")
TestMacosWorldfilesPatterns = globals().get("TestMacosWorldfilesPatterns")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
