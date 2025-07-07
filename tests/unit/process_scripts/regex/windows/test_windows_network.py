"""
Dynamically generated tests for audit-windows-network.yaml regex patterns.

This module automatically creates unit tests for each regex pattern defined
in the audit-windows-network.yaml configuration file, testing against real
Windows system data.
"""

import pytest

from tests.unit.process_scripts.regex.windows.test_all_windows_dynamic import (
    DynamicWindowsYamlTestMixin,
)


class TestWindowsNetworkPatterns(DynamicWindowsYamlTestMixin):
    """Dynamic tests for audit-windows-network.yaml regex patterns."""

    YAML_FILENAME = "audit-windows-network.yaml"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

