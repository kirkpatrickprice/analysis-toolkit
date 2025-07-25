# AI-GEN: GitHub Copilot|2025-01-24|parallel-processing-progress-tracker|reviewed:no
"""Concrete implementation of ProgressTracker protocol using Rich Output Service."""

from __future__ import annotations

from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from types import TracebackType

    import rich.progress

    from kp_analysis_toolkit.core.services.rich_output import RichOutputService

from kp_analysis_toolkit.core.services.parallel_processing.protocols import (
    ProgressTracker,
)


class DefaultProgressTracker(ProgressTracker):
    """
    Default implementation of ProgressTracker using Rich Output Service.

    Provides progress tracking for parallel operations by wrapping the RichOutputService
    progress functionality with validation and error handling suitable for parallel processing.
    """

    def __init__(self, rich_output: RichOutputService) -> None:
        """
        Initialize with Rich Output Service dependency.

        Args:
            rich_output: Rich output service for progress display

        """
        self._rich_output = rich_output
        self._active_progress: rich.progress.Progress | None = None
        self._active_tasks: dict[rich.progress.TaskID, str] = {}

    def track_progress(self, total: int, description: str) -> rich.progress.TaskID:
        """
        Create and track a progress task for parallel operations.

        Args:
            total: Total number of tasks to be processed
            description: Human-readable description of the operation

        Returns:
            Task ID for updating progress during execution

        Raises:
            ValueError: If total is invalid (<= 0)

        """
        if total <= 0:
            error_msg: str = f"Total must be greater than 0, got {total}"
            raise ValueError(error_msg)

        if not description.strip():
            error_msg = "Description cannot be empty"
            raise ValueError(error_msg)

        # Create progress context if not already active
        if self._active_progress is None:
            # Start a new progress context
            progress_context = self._rich_output.progress(
                show_eta=True,
                show_percentage=True,
                show_time_elapsed=True,
            )
            self._active_progress = progress_context.__enter__()

        # Add task to active progress
        task_id: rich.progress.TaskID = self._active_progress.add_task(
            description, total=total
        )
        self._active_tasks[task_id] = description

        return task_id

    def update_progress(self, task_id: rich.progress.TaskID, advance: int = 1) -> None:
        """
        Update progress for a tracked task.

        Args:
            task_id: Task ID returned from track_progress
            advance: Number of tasks completed (default: 1)

        Raises:
            ValueError: If task_id is invalid or advance is negative

        """
        if advance < 0:
            error_msg: str = f"Advance must be non-negative, got {advance}"
            raise ValueError(error_msg)

        if task_id not in self._active_tasks:
            error_msg = f"Invalid task ID: {task_id}"
            raise ValueError(error_msg)

        if self._active_progress is None:
            error_msg = "No active progress context"
            raise ValueError(error_msg)

        # Update progress
        self._active_progress.update(task_id, advance=advance)

    def complete_progress(self, task_id: rich.progress.TaskID) -> None:
        """
        Mark a progress task as completed.

        Args:
            task_id: Task ID to mark as completed

        Raises:
            ValueError: If task_id is invalid

        """
        if task_id not in self._active_tasks:
            error_msg: str = f"Invalid task ID: {task_id}"
            raise ValueError(error_msg)

        if self._active_progress is None:
            progress_error_msg: str = "No active progress context"
            raise ValueError(progress_error_msg)

        # Complete the task by setting it to 100%
        # We'll use the public tasks property rather than accessing private members
        self._active_progress.update(
            task_id,
            completed=self._active_progress.tasks[task_id].total,
        )

        # Remove from active tasks
        del self._active_tasks[task_id]

        # Clean up progress context if no more tasks
        if not self._active_tasks and self._active_progress is not None:
            self._active_progress.__exit__(None, None, None)
            self._active_progress = None

    def __enter__(self) -> Self:
        """
        Context manager entry for automatic progress cleanup.

        Returns:
            Self for use in context manager

        """
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """
        Context manager exit - ensures progress cleanup.

        Cleans up any active progress contexts and tasks.

        Args:
            exc_type: Exception type if an exception occurred
            exc_val: Exception value if an exception occurred
            exc_tb: Exception traceback if an exception occurred

        """
        # Clean up any remaining active progress
        if self._active_progress is not None:
            try:
                self._active_progress.__exit__(exc_type, exc_val, exc_tb)
            except (RuntimeError, AttributeError):
                # Ignore specific cleanup errors to avoid masking original exceptions
                # RuntimeError: progress may have been closed already
                # AttributeError: progress context may be in invalid state
                pass
            finally:
                self._active_progress = None
                self._active_tasks.clear()


# END AI-GEN
