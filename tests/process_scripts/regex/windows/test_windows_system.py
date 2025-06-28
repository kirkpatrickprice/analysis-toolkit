"""
Dynamically generated tests for audit-windows-system.yaml regex patterns.

This module automatically creates unit tests for each regex pattern defined
in the audit-windows-system.yaml configuration file, testing against real
Windows system data.

This implementation uses the new DynamicWindowsYamlTestMixin for consistency
with other Windows YAML test files.
"""

import pytest

from tests.process_scripts.regex.windows.test_all_windows_dynamic import (
    DynamicWindowsYamlTestMixin,
)


class TestWindowsSystemPatterns(DynamicWindowsYamlTestMixin):
    """Dynamic tests for audit-windows-system.yaml regex patterns."""

    YAML_FILENAME = "audit-windows-system.yaml"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
