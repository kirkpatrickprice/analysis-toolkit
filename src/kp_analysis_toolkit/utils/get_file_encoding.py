"""
File encoding detection utilities for the KP Analysis Toolkit.

This module provides both legacy direct encoding detection functionality and
dependency injection integration for file processing services.
"""

from pathlib import Path
from typing import TYPE_CHECKING

from charset_normalizer import CharsetMatch, from_path

from kp_analysis_toolkit.utils.di_state import create_file_processing_di_manager
from kp_analysis_toolkit.utils.rich_output import warning

if TYPE_CHECKING:
    from kp_analysis_toolkit.core.services.file_processing import FileProcessingService


# Global DI state manager
_di_manager, _get_service, _set_service, _clear_service = (
    create_file_processing_di_manager()
)


def _get_file_processing_service() -> object | None:
    """Get the file processing service if DI is available."""
    return _get_service()


def _set_file_processing_service(service: object) -> None:
    """Set the file processing service for DI integration."""
    _set_service(service)  # type: ignore[arg-type]


class ChardetEncodingDetector:
    """Encoding detector using charset-normalizer for DI integration."""

    def detect_encoding(self, file_path: Path) -> str | None:
        """
        Detect the encoding of a file using charset-normalizer.

        Args:
            file_path: Path to the file to analyze

        Returns:
            The detected encoding name, or None if detection fails

        """
        return detect_encoding(file_path)


def detect_encoding(file_path: str | Path) -> str | None:
    """
    Attempt to detect the encoding of the file.

    This function supports dependency injection when available, falling back to
    direct implementation for backward compatibility.

    Args:
        file_path (str | Path): The path to the file whose encoding is to be detected.

    Returns:
        str | None: The detected encoding of the file, or None if detection fails.
                   None indicates the file should be skipped.

    """
    # Convert to Path if needed
    if isinstance(file_path, str):
        file_path = Path(file_path)

    # Try to use DI-based file processing service first
    file_service = _get_file_processing_service()
    if file_service is not None:
        try:
            # Use the DI-based encoding detector
            return file_service.detect_encoding(file_path)  # type: ignore[attr-defined]
        except (AttributeError, OSError, Exception):  # noqa: S110
            # Fall back to direct implementation if DI fails
            # Common failures: service lacks method, file issues, etc.
            pass

    # Direct implementation fallback
    try:
        result: CharsetMatch | None = from_path(file_path).best()
    except (OSError, Exception):
        # Handle file access errors and charset_normalizer exceptions
        warning(f"Skipping file due to encoding detection failure: {file_path}")
        return None
    else:
        if result is not None:
            return result.encoding

        # Log the file that will be skipped due to encoding detection failure
        warning(f"Skipping file due to encoding detection failure: {file_path}")
        return None


# Dependency injection integration
def set_file_processing_service(service: "FileProcessingService") -> None:
    """
    Set the file processing service for dependency injection integration.

    This allows the detect_encoding function to use the DI-based file processing
    service when available, while maintaining backward compatibility.

    Args:
        service: The file processing service instance

    """
    _set_file_processing_service(service)


def get_file_processing_service() -> object | None:
    """
    Get the current file processing service if DI is enabled.

    Returns:
        The file processing service instance or None if not set

    """
    return _get_file_processing_service()


def clear_file_processing_service() -> None:
    """Clear the file processing service DI integration."""
    _clear_service()


def get_di_state() -> object:
    """
    Get the DI state for compatibility with test expectations.

    Returns:
        The DI state manager instance

    """
    return _di_manager
