"""Fixtures for dependency injection (DI) environment and state management."""

from collections.abc import Generator
from typing import Any
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def isolated_di_env() -> Generator[None, Any, None]:
    """
    Isolate dependency injection state for testing.

    This fixture ensures that DI state changes in tests don't affect other tests
    by clearing any existing DI state before and after the test.
    """
    # Clear any existing DI state before test
    try:
        from kp_analysis_toolkit.utils.excel_utils import clear_excel_export_service
        from kp_analysis_toolkit.utils.get_file_encoding import (
            clear_file_processing_service,
        )

        clear_excel_export_service()
        clear_file_processing_service()
    except (ImportError, AttributeError):
        # DI state utilities may not be fully implemented yet
        pass

    try:
        yield
    finally:
        # Clear DI state after test
        try:
            from kp_analysis_toolkit.utils.excel_utils import clear_excel_export_service
            from kp_analysis_toolkit.utils.get_file_encoding import (
                clear_file_processing_service,
            )

            clear_excel_export_service()
            clear_file_processing_service()
        except (ImportError, AttributeError):
            # DI state utilities may not be fully implemented yet
            pass


@pytest.fixture
def mock_di_state() -> Generator[dict[str, MagicMock], Any, None]:
    """
    Mock DI state for testing file processing service integration.

    This fixture provides a mock DI state that can be configured for different
    test scenarios involving dependency injection.
    """
    # Create a mock service
    mock_service = MagicMock()
    mock_service.detect_encoding.return_value = "utf-8"
    mock_service.generate_hash.return_value = "mock_hash_value"
    mock_service.process_file.return_value = {
        "encoding": "utf-8",
        "hash": "mock_hash_value",
        "path": "mock_path",
    }

    # Mock the DI state getter functions
    with (
        patch(
            "kp_analysis_toolkit.utils.get_file_encoding._get_file_processing_service",
        ) as mock_encoding_getter,
        patch(
            "kp_analysis_toolkit.utils.hash_generator._get_file_processing_service",
        ) as mock_hash_getter,
    ):
        # Configure mocks to return the service
        mock_encoding_getter.return_value = mock_service
        mock_hash_getter.return_value = mock_service

        yield {
            "service": mock_service,
            "encoding_getter": mock_encoding_getter,
            "hash_getter": mock_hash_getter,
        }


@pytest.fixture
def di_initialized() -> Generator[None, Any, None]:
    """
    Initialize dependency injection for tests that need it.

    This fixture ensures DI is properly initialized and cleaned up.
    """
    from kp_analysis_toolkit.core.containers.application import (
        initialize_dependency_injection,
    )

    # Initialize DI with test-friendly settings
    initialize_dependency_injection(verbose=False, quiet=True)

    try:
        yield
    finally:
        # Clean up DI state if needed
        try:
            from kp_analysis_toolkit.core.containers.application import container

            # Reset container state
            container.reset_singletons()
        except (ImportError, AttributeError):
            # Container reset may not be available
            pass


@pytest.fixture
def container_initialized() -> Generator[None, Any, None]:
    """
    Initialize DI container with proper configuration for container testing.

    This fixture is specifically for tests that need to examine container
    behavior, wiring, and configuration. It ensures the container is properly
    configured before testing container-specific functionality.
    """
    from kp_analysis_toolkit.core.containers.application import (
        initialize_dependency_injection,
    )

    # Initialize with explicit configuration for container testing
    initialize_dependency_injection(
        verbose=False,
        quiet=True,
        console_width=120,
        force_terminal=True,
        stderr_enabled=True,
    )

    try:
        yield
    finally:
        # Clean up container state
        try:
            from kp_analysis_toolkit.core.containers.application import container

            container.reset_singletons()
        except (ImportError, AttributeError):
            pass
