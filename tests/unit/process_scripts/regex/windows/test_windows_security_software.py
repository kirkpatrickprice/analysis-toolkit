"""
Dynamically generated tests for audit-windows-security-software.yaml regex patterns.

This module automatically creates unit tests for each regex pattern defined
in the audit-windows-security-software.yaml configuration file, testing against real
Windows system data.
"""

import pytest

from tests.unit.process_scripts.regex.windows.test_all_windows_dynamic import (
    DynamicWindowsYamlTestMixin,
)


class TestWindowsSecuritySoftwarePatterns(DynamicWindowsYamlTestMixin):
    """Dynamic tests for audit-windows-security-software.yaml regex patterns."""

    YAML_FILENAME = "audit-windows-security-software.yaml"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

