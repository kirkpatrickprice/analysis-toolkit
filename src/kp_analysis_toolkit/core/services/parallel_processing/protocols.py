# AI-GEN: GitHub Copilot|2025-01-24|parallel-processing-protocols|reviewed:no
"""Protocol definitions for parallel processing services."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, Self

if TYPE_CHECKING:
    import concurrent.futures
    from collections.abc import Callable
    from types import TracebackType

    import rich.progress

    from kp_analysis_toolkit.models.base import KPATBaseModel


class ExecutorFactory(Protocol):
    """Protocol for creating concurrent execution contexts."""

    def create_executor(self, max_workers: int) -> concurrent.futures.Executor:
        """
        Create a configured executor for parallel processing.

        Args:
            max_workers: Maximum number of worker processes/threads

        Returns:
            Configured executor instance ready for task submission

        Raises:
            ValueError: If max_workers is invalid (<= 0)
            OSError: If system resources are insufficient for executor creation

        """
        ...


class ProgressTracker(Protocol):
    """
    Protocol for tracking progress across parallel operations.

    Can be used standalone with:
    tracker.track_progress() to create progress tasks
    tracker.update_progress() to update progress
    tracker.complete_progress() to mark tasks complete

    Can be used as a context manager for automatic cleanup:
        with progress_tracker:
            # progress operations here
            # cleanup happens automatically
    """

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
        ...

    def update_progress(self, task_id: rich.progress.TaskID, advance: int = 1) -> None:
        """
        Update progress for a tracked task.

        Args:
            task_id: Task ID returned from track_progress
            advance: Number of tasks completed (default: 1)

        Raises:
            ValueError: If task_id is invalid or advance is negative

        """
        ...

    def complete_progress(self, task_id: rich.progress.TaskID) -> None:
        """
        Mark a progress task as completed.

        Args:
            task_id: Task ID to mark as completed

        Raises:
            ValueError: If task_id is invalid

        """
        ...

    def __enter__(self) -> Self:
        """
        Context manager entry - sets up progress tracking.

        Returns:
            Self for use in context manager

        Raises:
            RuntimeError: If progress tracking cannot be initialized

        """
        ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool | None:
        """
        Context manager exit - ensures progress cleanup happens.

        Cleans up any active progress contexts and tasks regardless of
        whether an exception occurred. Does not suppress exceptions.

        Args:
            exc_type: Exception type if an exception occurred
            exc_val: Exception value if an exception occurred
            exc_tb: Exception traceback if an exception occurred

        Returns:
            None (does not suppress exceptions)

        """
        ...


class InterruptHandler(Protocol):
    """
    Protocol for handling multi-stage graceful interruption of parallel operations.

    Implements a three-stage interrupt handling strategy:
    1. First CTRL-C: Cancel queued tasks, finish active tasks
    2. Second CTRL-C: Terminate active tasks, return partial results
    3. Third CTRL-C: Immediate termination with no cleanup

    Can be used standalone with:
    setup() to configure signal handlers and shared state
    # parallel operations here
    cleanup() to restore original handlers and clean up state

    Can be used as a context manager for automatic setup/cleanup:
        with interrupt_handler:
            # parallel operations here
            # cleanup happens automatically
    """

    def setup(self) -> None:
        """
        Set up multi-stage interrupt handling for parallel operations.

        Configures signal handlers (SIGINT/SIGTERM) and shared state for
        coordinating interruption across process boundaries. Suppresses
        Python's default KeyboardInterrupt traceback handling.

        Raises:
            OSError: If signal handlers cannot be configured

        """
        ...

    def cleanup(self) -> None:
        """
        Clean up interrupt handling resources.

        Restores original signal handlers and cleans up shared state.
        Should be called after parallel operations complete, regardless
        of completion status.

        """
        ...

    def __enter__(self) -> Self:
        """
        Context manager entry - sets up interrupt handling.

        Returns:
            Self for use in context manager

        Raises:
            OSError: If signal handlers cannot be configured

        """
        ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool | None:
        """
        Context manager exit - ensures cleanup happens.

        Calls cleanup() regardless of whether an exception occurred.
        Does not suppress exceptions (returns None/False).

        Args:
            exc_type: Exception type if an exception occurred
            exc_val: Exception value if an exception occurred
            exc_tb: Exception traceback if an exception occurred

        Returns:
            None (does not suppress exceptions)

        """
        ...

    def is_interrupted(self) -> bool:
        """
        Check if any stage of interruption has been requested.

        Returns:
            True if interruption has been requested at any stage, False otherwise

        """
        ...

    def get_interrupt_stage(self) -> int:
        """
        Get the current interrupt stage.

        Returns:
            0: No interrupt requested
            1: First CTRL-C - Cancel queued tasks, finish active, return available results
            2: Second CTRL-C - Terminate active tasks, return partial results
            3: Third CTRL-C - Immediate termination, no cleanup

        """
        ...

    def should_cancel_queued_tasks(self) -> bool:
        """
        Check if queued tasks should be cancelled.

        Returns:
            True if interrupt stage >= 1 (cancel queued tasks)

        """
        ...

    def should_terminate_active_tasks(self) -> bool:
        """
        Check if active tasks should be terminated.

        Returns:
            True if interrupt stage >= 2 (terminate active tasks)

        """
        ...

    def should_immediate_exit(self) -> bool:
        """
        Check if immediate exit without cleanup is requested.

        Returns:
            True if interrupt stage >= 3 (immediate termination)

        """
        ...

    def handle_interrupt_stage(self, stage: int) -> None:
        """
        Handle user communication for interrupt stage transitions.

        Displays appropriate messages to user about interrupt behavior:
        - Stage 1: "Cancelling queued tasks. Press CTRL-C again to terminate active jobs."
        - Stage 2: "Cancelling active tasks. Press CTRL-C again to terminate immediately."
        - Stage 3: Immediate exit without message

        Args:
            stage: The interrupt stage being entered (1, 2, or 3)

        """
        ...


class TaskResult(Protocol):
    """Protocol for results returned from parallel task execution."""

    @property
    def success(self) -> bool:
        """Whether the task completed successfully."""
        ...

    @property
    def error(self) -> Exception | None:
        """Error that occurred during task execution, if any."""
        ...

    @property
    def result(self) -> KPATBaseModel:
        """Result data from successful task execution as a validated Pydantic model."""
        ...


class ParallelProcessingService(Protocol):
    """
    Protocol for the main parallel processing service with multi-stage interrupt support.

    The service automatically manages interrupt handling setup/cleanup, but the
    InterruptHandler can also be used directly as a context manager if needed.
    """

    def execute_in_parallel(
        self,
        tasks: list[Callable[[], KPATBaseModel]],
        max_workers: int,
        description: str = "Processing...",
    ) -> list[KPATBaseModel]:
        """
        Execute callable tasks in parallel with progress tracking and multi-stage interruption.

        This is the primary method for parallel execution. Use this for:
        - Search engine operations (multiple search configs)
        - Excel export operations (multiple OS-specific exports)
        - Any CPU-bound tasks that can run independently

        Supports graceful interruption with three stages:
        1. First CTRL-C: Cancel queued tasks, complete active tasks
        2. Second CTRL-C: Terminate active tasks, return partial results
        3. Third CTRL-C: Immediate termination without cleanup

        Args:
            tasks: List of callable tasks that take no arguments and return KPATBaseModel results
            max_workers: Maximum number of worker processes
            description: Description for progress tracking

        Returns:
            List of KPATBaseModel results from task execution in original order.
            May contain partial results if interrupted at stage 1 or 2.

        Raises:
            ValueError: If tasks list is empty or max_workers is invalid
            InterruptedError: If execution is interrupted at stage 3 (immediate termination)
            Exception: If error handling strategy requires failure propagation

        """
        ...

    def execute_with_batching(
        self,
        tasks: list[Callable[[], KPATBaseModel]],
        max_workers: int,
        batch_size: int | None = None,
        description: str = "Processing...",
    ) -> list[KPATBaseModel]:
        """
        Execute large numbers of tasks in parallel with memory-efficient batching.

        Use this method when:
        - Processing thousands of files that would exceed memory if all queued
        - Tasks that might create large intermediate objects
        - Need to limit memory usage during parallel processing

        Processes tasks in smaller batches to prevent memory exhaustion while
        maintaining parallel efficiency.

        Supports graceful interruption with three stages:
        1. First CTRL-C: Cancel queued batches, complete active batch
        2. Second CTRL-C: Terminate active batch, return partial results
        3. Third CTRL-C: Immediate termination without cleanup

        Args:
            tasks: List of callable tasks that take no arguments and return KPATBaseModel results
            max_workers: Maximum number of worker processes
            batch_size: Number of tasks per batch (auto-calculated based on task count if None)
            description: Description for progress tracking

        Returns:
            List of KPATBaseModel results from task execution in original order.
            May contain partial results if interrupted at stage 1 or 2.

        Raises:
            ValueError: If parameters are invalid
            InterruptedError: If execution is interrupted at stage 3 (immediate termination)

        """
        ...


# END AI-GEN
