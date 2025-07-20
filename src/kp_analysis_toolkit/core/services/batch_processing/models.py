# AI-GEN: claude-3.5-sonnet|2025-01-19|batch-processing-service|reviewed:yes
"""Models and data structures for batch processing operations."""

from __future__ import annotations

from collections.abc import Callable  # noqa: TC003
from enum import Enum
from pathlib import Path  # noqa: TC003
from typing import Any

from pydantic import Field

from kp_analysis_toolkit.models.base import KPATBaseModel


class ErrorHandlingStrategy(Enum):
    """Strategies for handling errors during batch processing."""

    FAIL_FAST = "fail_fast"  # Stop on first error
    CONTINUE_ON_ERROR = "continue_on_error"  # Log error and continue
    COLLECT_ERRORS = "collect_errors"  # Collect all errors and report at end


class BatchResult(KPATBaseModel):
    """Results from batch processing operation."""

    total_files: int = 0
    successful: int = 0
    failed: int = 0
    errors: list[tuple[Path, Exception]] = Field(default_factory=list)
    success_details: list[tuple[Path, str]] = Field(default_factory=list)

    def add_success(self, file_path: Path, message: str = "") -> None:
        """Record a successful file processing."""
        self.successful += 1
        if message:
            self.success_details.append((file_path, message))

    def add_failure(self, file_path: Path, error: Exception) -> None:
        """Record a failed file processing."""
        self.failed += 1
        self.errors.append((file_path, error))

    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.total_files == 0:
            return 0.0
        return (self.successful / self.total_files) * 100


class BatchProcessingConfig(KPATBaseModel):
    """Configuration for batch processing operations."""

    operation_description: str = "Processing files"
    progress_description: str = "Processing files..."
    error_handling: ErrorHandlingStrategy = ErrorHandlingStrategy.CONTINUE_ON_ERROR
    success_message_formatter: Callable[[Path, Any], str] | None = None


# Rebuild models to resolve forward references
BatchResult.model_rebuild()
BatchProcessingConfig.model_rebuild()
# END AI-GEN
