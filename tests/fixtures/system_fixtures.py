"""System and OS mock fixtures for testing."""

from unittest.mock import Mock

import pytest

from kp_analysis_toolkit.process_scripts.models.results.system import Systems
from kp_analysis_toolkit.process_scripts.models.types.enums import (
    OSFamilyType,
    ProducerType,
)


@pytest.fixture
def mock_linux_system() -> Systems:
    """Create a mock Linux Systems object for testing."""
    system: Systems = Mock(spec=Systems)
    system.system_name = "test-linux-system"
    system.os_family = OSFamilyType.LINUX
    system.producer = ProducerType.KPNIXAUDIT
    system.producer_version = "1.0.0"
    system.file = Mock()
    system.file.name = "test-system.log"
    return system


@pytest.fixture
def mock_windows_system() -> Systems:
    """Create a mock Windows Systems object for testing."""
    system: Systems = Mock(spec=Systems)
    system.system_name = "test-windows-system"
    system.os_family = OSFamilyType.WINDOWS
    system.producer = ProducerType.KPWINAUDIT
    system.producer_version = "1.0.0"
    system.file = Mock()
    system.file.name = "test-system.log"
    return system
