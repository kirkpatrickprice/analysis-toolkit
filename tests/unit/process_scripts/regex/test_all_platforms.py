"""
Comprehensive test runner for all platform YAML configuration files.

This module provides a unified way to run regex pattern tests across
Windows, Linux, and macOS YAML configuration files.
"""

import pytest

from tests.unit.process_scripts.regex.dynamic_test_generator import discover_yaml_files


def test_all_platforms() -> None:
    """Run tests for all platforms to ensure comprehensive coverage."""
    platforms = ["windows", "linux", "macos"]

    total_yaml_files = 0

    for platform in platforms:
        yaml_files = discover_yaml_files(platform)
        total_yaml_files += len(yaml_files)
        print(f"\n{platform.title()} YAML files ({len(yaml_files)}):")
        for yaml_file in yaml_files:
            print(f"  - {yaml_file}")

    print(f"\nTotal YAML files across all platforms: {total_yaml_files}")

    # Ensure we have YAML files for each platform
    assert total_yaml_files > 0, "No YAML files found across any platform"

    for platform in platforms:
        yaml_files = discover_yaml_files(platform)
        assert len(yaml_files) > 0, f"No YAML files found for {platform}"


if __name__ == "__main__":
    # Run the comprehensive test
    test_all_platforms()

    # Run tests for all platforms
    test_patterns = [
        "tests/process_scripts/regex/windows/test_all_windows_dynamic.py",
        "tests/process_scripts/regex/linux/test_all_linux_dynamic.py",
        "tests/process_scripts/regex/macos/test_all_macos_dynamic.py",
    ]

    print("\nRunning comprehensive tests across all platforms...")
    pytest.main(["-v", *test_patterns])

