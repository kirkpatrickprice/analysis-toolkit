"""
Comprehensive test runner for all platform YAML configuration files.

This module provides a unified way to run regex pattern tests across
Windows, Linux, and macOS YAML configuration files.
"""

import pytest

from tests.process_scripts.regex.dynamic_test_generator import discover_yaml_files


def test_all_platforms() -> None:
    """Run tests for all audit configuration files to ensure comprehensive coverage."""
    # Since YAML files are now topic-based rather than platform-specific,
    # we test all audit YAML files once
    yaml_files = discover_yaml_files()

    print(f"\nAudit YAML files found ({len(yaml_files)}):")
    for yaml_file in yaml_files:
        print(f"  - {yaml_file}")

    print(f"\nTotal YAML files: {len(yaml_files)}")

    # Ensure we have YAML files
    assert len(yaml_files) > 0, "No audit YAML files found"

    # Verify we have some expected files
    expected_files = [
        "audit-network.yaml",
        "audit-remote-mgmt.yaml",
        "audit-crypto-policies.yaml",
    ]

    found_files = set(yaml_files)
    for expected_file in expected_files:
        assert expected_file in found_files, (
            f"Expected audit file {expected_file} not found"
        )


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
