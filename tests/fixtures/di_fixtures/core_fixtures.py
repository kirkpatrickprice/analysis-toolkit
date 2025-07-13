"""Core dependency injection fixtures for testing."""

from typing import TYPE_CHECKING
from unittest.mock import MagicMock, Mock

import pytest

from kp_analysis_toolkit.core.containers.application import (
    initialize_dependency_injection,
)

if TYPE_CHECKING:
    from kp_analysis_toolkit.core.containers.core import CoreContainer


# =============================================================================
# DEPENDENCY INJECTION FIXTURES
# =============================================================================


@pytest.fixture
def initialized_container() -> None:
    """Initialize the dependency injection container for tests."""
    # Initialize the container with default test values
    initialize_dependency_injection(
        verbose=False,
        quiet=False,
        console_width=120,
        force_terminal=True,
        stderr_enabled=True,
    )


@pytest.fixture
def mock_core_container() -> MagicMock:
    """Create a mock CoreContainer for testing file processing integration."""
    from kp_analysis_toolkit.core.containers.core import CoreContainer

    container = Mock(spec=CoreContainer)
    mock_config = MagicMock()
    mock_rich_output = MagicMock()

    # Setup configuration mock
    mock_config.verbose.from_value = Mock()
    mock_config.quiet.from_value = Mock()
    mock_config.console_width.from_value = Mock()
    mock_config.force_terminal.from_value = Mock()
    mock_config.stderr_enabled.from_value = Mock()

    # Setup property access
    mock_config.verbose.return_value = False
    mock_config.quiet.return_value = False
    mock_config.console_width.return_value = 120
    mock_config.force_terminal.return_value = True
    mock_config.stderr_enabled.return_value = True

    # Setup rich output
    mock_rich_output.verbose = False
    mock_rich_output.quiet = False

    container.config = mock_config
    container.rich_output.return_value = mock_rich_output

    return container


@pytest.fixture
def mock_di_container() -> MagicMock:
    """
    Mock dependency injection container for testing.

    Returns a mock container that can be used for testing DI functionality
    without requiring actual DI initialization.
    """
    mock_container = MagicMock()
    mock_service = MagicMock()

    # Setup default behavior
    mock_container.file_processing_service.return_value = mock_service
    mock_container.encoding_detector.return_value = MagicMock()
    mock_container.hash_generator.return_value = MagicMock()
    mock_container.file_validator.return_value = MagicMock()

    return mock_container


@pytest.fixture
def real_core_container() -> "CoreContainer":
    """
    Create a real CoreContainer for dependency injection tests.

    This fixture provides a properly configured CoreContainer instance
    that can be used for testing actual DI behavior without mocks.
    """
    from kp_analysis_toolkit.core.containers.core import CoreContainer

    container = CoreContainer()

    # Configure with sensible defaults for testing
    container.config.verbose.from_value(False)
    container.config.quiet.from_value(False)
    container.config.console_width.from_value(120)
    container.config.force_terminal.from_value(True)
    container.config.stderr_enabled.from_value(True)

    return container
