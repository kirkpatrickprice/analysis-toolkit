"""
Dynamic test generator for all Windows YAML configuration files.

This module creates test classes dynamically for each audit-windows-*.yaml file,
reusing the common testing logic from the generalized base classes.
"""

from pathlib import Path

import pytest

from tests.unit.process_scripts.regex.dynamic_test_generator import (
    DynamicYamlTestMixin,
    create_platform_test_class,
    discover_yaml_files,
)


class WindowsSpecificTestMixin(DynamicYamlTestMixin):
    """Windows-specific test mixin that extends the common functionality."""

    PLATFORM = "WINDOWS"
    TEST_DATA_SUBDIR = "windows"

    @pytest.fixture
    def platform_test_files(self) -> dict[str, Path]:
        """Get all Windows test data files with specific naming."""
        test_dir = self.get_test_data_dir()

        return {
            "windows10pro": test_dir / "windows10pro-cb19044-kp0.4.7.txt",
            "windows11": test_dir / "windows11-0.4.8.txt",
            "windows2016": test_dir / "windows2016-cb14393-kp0.4.4-1.txt",
            "windows2022": test_dir / "windows2022-cb20348-kp0.4.7.txt",
        }


# Alias for backward compatibility
DynamicWindowsYamlTestMixin = WindowsSpecificTestMixin


# Discover and create test classes for all Windows YAML files
WINDOWS_YAML_FILES = discover_yaml_files("windows")

for yaml_file in WINDOWS_YAML_FILES:
    test_class = create_platform_test_class("windows", "windows", yaml_file)

    # Override with Windows-specific mixin if needed
    enhanced_class = type(
        test_class.__name__,
        (WindowsSpecificTestMixin,),
        {
            "YAML_FILENAME": yaml_file,
            "PLATFORM": "WINDOWS",
            "TEST_DATA_SUBDIR": "windows",
            "__doc__": f"Dynamic tests for {yaml_file} regex patterns on Windows.",
        },
    )

    # Add the class to the global namespace so pytest can discover it
    globals()[enhanced_class.__name__] = enhanced_class


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

