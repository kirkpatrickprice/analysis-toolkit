"""
Dynamically generated tests for audit-windows-users.yaml regex patterns.

This module automatically creates unit tests for each regex pattern defined
in the audit-windows-users.yaml configuration file, testing against real
Windows system data.
"""

import pytest

from tests.process_scripts.regex.windows.test_all_windows_dynamic import (
    DynamicWindowsYamlTestMixin,
)


class TestWindowsUsersPatterns(DynamicWindowsYamlTestMixin):
    """Dynamic tests for audit-windows-users.yaml regex patterns."""

    YAML_FILENAME = "audit-windows-users.yaml"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
