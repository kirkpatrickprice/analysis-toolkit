"""
Dynamic test generator for all Linux YAML configuration files.

This module creates test classes dynamically for each audit-linux-*.yaml file,
reusing the common testing logic from the generalized base classes.
"""

from pathlib import Path

import pytest

from tests.unit.process_scripts.regex.dynamic_test_generator import (
    DynamicYamlTestMixin,
    create_platform_test_class,
    discover_yaml_files,
)


class LinuxSpecificTestMixin(DynamicYamlTestMixin):
    """Linux-specific test mixin that extends the common functionality."""

    PLATFORM = "LINUX"
    TEST_DATA_SUBDIR = "linux"

    @pytest.fixture
    def platform_test_files(self) -> dict[str, Path]:
        """Get all Linux test data files with specific naming."""
        test_dir = self.get_test_data_dir()

        return {
            "oracle9": test_dir / "oracle9-0.6.21.txt",
            "rhel86": test_dir / "rhel86-kp0.6.16-1.txt",
            "ubuntu2204": test_dir / "ubuntu-22.04-0.6.22.txt",
        }


# Discover and create test classes for all Linux YAML files
LINUX_YAML_FILES = discover_yaml_files("linux")

for yaml_file in LINUX_YAML_FILES:
    test_class = create_platform_test_class("linux", "linux", yaml_file)

    # Override with Linux-specific mixin if needed
    enhanced_class = type(
        test_class.__name__,
        (LinuxSpecificTestMixin,),
        {
            "YAML_FILENAME": yaml_file,
            "PLATFORM": "LINUX",
            "TEST_DATA_SUBDIR": "linux",
            "__doc__": f"Dynamic tests for {yaml_file} regex patterns on Linux.",
        },
    )

    # Add the class to the global namespace so pytest can discover it
    globals()[enhanced_class.__name__] = enhanced_class


# For backward compatibility and manual testing
TestLinuxSystemPatterns = globals().get("TestLinuxSystemPatterns")
TestLinuxUsersPatterns = globals().get("TestLinuxUsersPatterns")
TestLinuxNetworkPatterns = globals().get("TestLinuxNetworkPatterns")
TestLinuxSshPatterns = globals().get("TestLinuxSshPatterns")
TestLinuxLoggingPatterns = globals().get("TestLinuxLoggingPatterns")
TestLinuxServicesPatterns = globals().get("TestLinuxServicesPatterns")
TestLinuxSecToolsPatterns = globals().get("TestLinuxSectoolsPatterns")
TestLinuxWorldfilesPatterns = globals().get("TestLinuxWorldfilesPatterns")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

