"""
Centralized dependency injection state management for backward compatibility.

This module provides shared utilities for managing DI integration state
across legacy utility modules that need to maintain backward compatibility
while supporting the new DI-based service architecture.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Generic

if TYPE_CHECKING:
    from collections.abc import Callable

from kp_analysis_toolkit.core.services.file_processing import FileProcessingService
from kp_analysis_toolkit.models.types import T


class DIState(Generic[T]):
    """
    Centralized state management for dependency injection integration.

    This class provides a standardized way to manage DI state across
    backward compatibility modules.
    """

    def __init__(self) -> None:
        """Initialize the DI state."""
        self.enabled = False
        self.service: T | None = None

    def get_service(self) -> T | None:
        """
        Get the injected service if available.

        Returns:
            The injected service instance or None if not set

        """
        if not self.enabled or self.service is None:
            return None
        return self.service

    def set_service(self, service: T) -> None:
        """
        Set the service for DI integration.

        Args:
            service: The service instance to inject

        """
        self.service = service
        self.enabled = True

    def clear_service(self) -> None:
        """Clear the DI integration state."""
        self.enabled = False
        self.service = None

    def is_enabled(self) -> bool:
        """
        Check if DI integration is enabled.

        Returns:
            True if DI is enabled and service is set, False otherwise

        """
        return self.enabled and self.service is not None


class FileProcessingDIState(DIState[FileProcessingService]):
    """
    Specialized DI state for file processing service integration.

    This provides type-safe access to the file processing service
    for backward compatibility modules.
    """


def create_file_processing_di_manager() -> tuple[
    FileProcessingDIState,
    Callable[[], FileProcessingService | None],
    Callable[[FileProcessingService], None],
    Callable[[], None],
]:
    """
    Create a complete DI management setup for file processing service.

    Returns:
        A tuple containing:
        - The DI state instance
        - A getter function for the service
        - A setter function for the service
        - A clear function for the service

    """
    di_state = FileProcessingDIState()

    def get_service() -> FileProcessingService | None:
        return di_state.get_service()

    def set_service(service: FileProcessingService) -> None:
        di_state.set_service(service)

    def clear_service() -> None:
        di_state.clear_service()

    return di_state, get_service, set_service, clear_service
