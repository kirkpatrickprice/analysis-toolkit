from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

from kp_analysis_toolkit.utils.rich_output import RichOutput

if TYPE_CHECKING:
    import concurrent.futures
    from collections.abc import Callable

    import rich.progress

    from kp_analysis_toolkit.utils.rich_output import RichOutput


class ExecutorFactory(Protocol):
    """Protocol for executor factory."""

    def create_executor(self, max_workers: int) -> concurrent.futures.Executor: ...


class ProgressTracker(Protocol):
    """Protocol for progress tracking."""

    def track_progress(self, total: int, description: str) -> rich.progress.TaskID: ...


class InterruptHandler(Protocol):
    """Protocol for interrupt handling."""

    def setup(self) -> None: ...
    def cleanup(self) -> None: ...
    def is_interrupted(self) -> bool: ...


class ParallelProcessingService:
    """Service for parallel processing operations."""

    def __init__(
        self,
        executor_factory: ExecutorFactory,
        progress_tracker: ProgressTracker,
        interrupt_handler: InterruptHandler,
        rich_output: RichOutput,
    ) -> None:
        self.executor_factory: ExecutorFactory = executor_factory
        self.progress_tracker: ProgressTracker = progress_tracker
        self.interrupt_handler: InterruptHandler = interrupt_handler
        self.rich_output: RichOutput = rich_output

    def execute_in_parallel(
        self,
        tasks: list[Callable],
        max_workers: int,
        description: str = "Processing...",
    ) -> None:
        """Generic parallel execution with progress tracking."""
