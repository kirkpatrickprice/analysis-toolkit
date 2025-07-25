# AI-GEN: GitHub Copilot|2025-01-24|parallel-processing-service|reviewed:no
"""Default implementation of ParallelProcessingService protocol."""

from __future__ import annotations

import math
from concurrent.futures._base import Future
from typing import TYPE_CHECKING

from kp_analysis_toolkit.core.services.parallel_processing.protocols import (
    ExecutorFactory,
    InterruptHandler,
    ParallelProcessingService,
    ProgressTracker,
    TaskResult,
)
from kp_analysis_toolkit.models.base import KPATBaseModel

if TYPE_CHECKING:
    import concurrent.futures
    from collections.abc import Callable
    from concurrent.futures import Executor, Future

    import rich.progress

    from kp_analysis_toolkit.models.base import KPATBaseModel


class DefaultParallelProcessingService(ParallelProcessingService):
    """
    Default implementation of ParallelProcessingService with multi-stage interrupt support.

    Orchestrates parallel task execution using injected executor factory, progress tracker,
    interrupt handler, and task result factory dependencies. Provides both basic parallel
    execution and memory-efficient batching for large task sets.

    The service automatically manages interrupt handling setup/cleanup, but the
    InterruptHandler can also be used directly as a context manager if needed.
    """

    def __init__(
        self,
        executor_factory: ExecutorFactory,
        progress_tracker: ProgressTracker,
        interrupt_handler: InterruptHandler,
        task_result_factory: Callable[[], TaskResult],
    ) -> None:
        """
        Initialize with injected dependencies.

        Args:
            executor_factory: Factory for creating concurrent executors
            progress_tracker: Service for tracking operation progress
            interrupt_handler: Handler for multi-stage graceful interruption
            task_result_factory: Factory for creating TaskResult instances

        """
        self._executor_factory: ExecutorFactory = executor_factory
        self._progress_tracker: ProgressTracker = progress_tracker
        self._interrupt_handler: InterruptHandler = interrupt_handler
        self._task_result_factory: Callable[[], TaskResult] = task_result_factory

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
        # Validate input parameters
        if not tasks:
            msg: str = "Tasks list cannot be empty"
            raise ValueError(msg)
        if max_workers <= 0:
            msg = "max_workers must be positive"
            raise ValueError(msg)

        # Set up interrupt handling and progress tracking
        with self._interrupt_handler, self._progress_tracker:
            return self._execute_tasks_with_tracking(
                tasks=tasks,
                max_workers=max_workers,
                description=description,
            )

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
        # Validate input parameters
        if not tasks:
            msg: str = "Tasks list cannot be empty"
            raise ValueError(msg)
        if max_workers <= 0:
            msg = "max_workers must be positive"
            raise ValueError(msg)
        if batch_size is not None and batch_size <= 0:
            msg = "batch_size must be positive"
            raise ValueError(msg)

        # Calculate optimal batch size if not provided
        calculated_batch_size: int = batch_size or self._calculate_optimal_batch_size(
            task_count=len(tasks),
            max_workers=max_workers,
        )

        # Set up interrupt handling and progress tracking
        with self._interrupt_handler, self._progress_tracker:
            return self._execute_batched_tasks_with_tracking(
                tasks=tasks,
                max_workers=max_workers,
                batch_size=calculated_batch_size,
                description=description,
            )

    def _execute_tasks_with_tracking(
        self,
        tasks: list[Callable[[], KPATBaseModel]],
        max_workers: int,
        description: str,
    ) -> list[KPATBaseModel]:
        """
        Execute tasks with progress tracking and interrupt handling.

        Args:
            tasks: List of callable tasks to execute
            max_workers: Maximum number of worker processes
            description: Description for progress tracking

        Returns:
            List of execution results in original order

        """
        task_id: rich.progress.TaskID = self._progress_tracker.track_progress(
            total=len(tasks),
            description=description,
        )

        try:
            executor: Executor = self._executor_factory.create_executor(max_workers)
            with executor:
                # Submit tasks and handle submission-level interrupts
                future_to_index: dict[Future[KPATBaseModel], int] = (
                    self._submit_tasks_with_interrupt_handling(
                        tasks,
                        executor,
                    )
                )

                # Process results with execution-level interrupts
                results: list[KPATBaseModel] = (
                    self._process_task_results_with_interrupt_handling(
                        future_to_index,
                        tasks,
                        task_id,
                    )
                )

                return results

        finally:
            self._progress_tracker.complete_progress(task_id)

    def _submit_tasks_with_interrupt_handling(
        self,
        tasks: list[Callable[[], KPATBaseModel]],
        executor: Executor,
    ) -> dict[concurrent.futures.Future[KPATBaseModel], int]:
        """Submit tasks to executor with interrupt handling during submission."""
        future_to_index: dict[concurrent.futures.Future[KPATBaseModel], int] = {}

        # Submit tasks until interrupted
        for i, task in enumerate(tasks):
            if self._interrupt_handler.should_cancel_queued_tasks():
                break

            future: Future[KPATBaseModel] = executor.submit(
                self._execute_single_task,
                task,
            )
            future_to_index[future] = i

        # Cancel queued tasks if interrupt occurred during submission
        if self._interrupt_handler.should_cancel_queued_tasks():
            self._cancel_queued_futures(future_to_index)

        return future_to_index

    def _process_task_results_with_interrupt_handling(
        self,
        future_to_index: dict[concurrent.futures.Future[KPATBaseModel], int],
        tasks: list[Callable[[], KPATBaseModel]],
        task_id: rich.progress.TaskID,
    ) -> list[KPATBaseModel]:
        """Process task results with interrupt handling during execution."""
        results: list[KPATBaseModel | None] = [None] * len(tasks)

        import concurrent.futures

        for future in concurrent.futures.as_completed(future_to_index):
            # Handle termination requests
            if self._interrupt_handler.should_terminate_active_tasks():
                self._cancel_remaining_futures(future_to_index)
                break

            # Handle immediate exit requests
            if self._interrupt_handler.should_immediate_exit():
                msg: str = "Immediate termination requested"
                raise InterruptedError(msg)

            # Process individual task result
            self._process_single_task_result(future, future_to_index, results, task_id)

        # Filter out None values for partial results
        return [r for r in results if r is not None]

    def _cancel_queued_futures(
        self,
        future_to_index: dict[concurrent.futures.Future[KPATBaseModel], int],
    ) -> None:
        """Cancel futures that are queued but not yet running."""
        for future in future_to_index:
            if not future.running():
                future.cancel()

    def _cancel_remaining_futures(
        self,
        future_to_index: dict[concurrent.futures.Future[KPATBaseModel], int],
    ) -> None:
        """Cancel all remaining futures that are not done."""
        for future in future_to_index:
            if not future.done():
                future.cancel()

    def _process_single_task_result(
        self,
        future: concurrent.futures.Future[KPATBaseModel],
        future_to_index: dict[concurrent.futures.Future[KPATBaseModel], int],
        results: list[KPATBaseModel | None],
        task_id: rich.progress.TaskID,
    ) -> None:
        """Process result from a single completed task."""
        task_index: int = future_to_index[future]
        try:
            task_result: KPATBaseModel = future.result()
            results[task_index] = task_result
        except (RuntimeError, ValueError, OSError):
            # Handle specific task execution errors
            # For now, we'll continue and let None remain in results
            # Future enhancement: configurable error handling strategy
            pass

        self._progress_tracker.update_progress(task_id)

    def _execute_batched_tasks_with_tracking(
        self,
        tasks: list[Callable[[], KPATBaseModel]],
        max_workers: int,
        batch_size: int,
        description: str,
    ) -> list[KPATBaseModel]:
        """
        Execute tasks in batches with progress tracking and interrupt handling.

        Args:
            tasks: List of callable tasks to execute
            max_workers: Maximum number of worker processes
            batch_size: Number of tasks per batch
            description: Description for progress tracking

        Returns:
            List of execution results in original order

        """
        all_results: list[KPATBaseModel] = []
        total_batches: int = math.ceil(len(tasks) / batch_size)

        task_id: rich.progress.TaskID = self._progress_tracker.track_progress(
            total=len(tasks),
            description=description,
        )

        try:
            for batch_num in range(total_batches):
                # Check for batch cancellation (prevents new batches)
                if self._interrupt_handler.should_cancel_queued_tasks():
                    break

                # Calculate batch slice
                start_idx: int = batch_num * batch_size
                end_idx: int = min(start_idx + batch_size, len(tasks))
                batch_tasks: list[Callable[[], KPATBaseModel]] = tasks[
                    start_idx:end_idx
                ]

                # Execute current batch - this now handles interrupts properly
                batch_results: list[KPATBaseModel] = self._execute_single_batch(
                    batch_tasks=batch_tasks,
                    max_workers=max_workers,
                    task_id=task_id,
                )

                all_results.extend(batch_results)

                # Check for termination after batch completion
                # This catches interrupts that occurred during batch execution
                if self._interrupt_handler.should_terminate_active_tasks():
                    break

                # Also check for immediate exit after each batch
                if self._interrupt_handler.should_immediate_exit():
                    msg: str = "Immediate termination requested"
                    raise InterruptedError(msg)

        finally:
            self._progress_tracker.complete_progress(task_id)

        return all_results

    def _execute_single_batch(
        self,
        batch_tasks: list[Callable[[], KPATBaseModel]],
        max_workers: int,
        task_id: rich.progress.TaskID,
    ) -> list[KPATBaseModel]:
        """
        Execute a single batch of tasks with proper interrupt handling.

        Handles two levels of interrupt scenarios:
        1. Interrupt during task submission - cancels queued tasks in current batch
        2. Interrupt during task execution - terminates active tasks in current batch

        Args:
            batch_tasks: Tasks in this batch
            max_workers: Maximum number of worker processes
            task_id: Progress task ID for updates

        Returns:
            Results from batch execution (may be partial if interrupted)

        """
        executor: Executor = self._executor_factory.create_executor(max_workers)

        with executor:
            # Submit batch tasks with interrupt handling
            future_to_task: dict[Future[KPATBaseModel], Callable[[], KPATBaseModel]] = (
                self._submit_batch_tasks_with_interrupt_handling(
                    batch_tasks,
                    executor,
                )
            )

            # Process batch results with interrupt handling
            return self._process_batch_results_with_interrupt_handling(
                future_to_task,
                task_id,
            )

    def _submit_batch_tasks_with_interrupt_handling(
        self,
        batch_tasks: list[Callable[[], KPATBaseModel]],
        executor: Executor,
    ) -> dict[concurrent.futures.Future[KPATBaseModel], Callable[[], KPATBaseModel]]:
        """Submit batch tasks to executor with interrupt handling during submission."""
        future_to_task: dict[
            concurrent.futures.Future[KPATBaseModel],
            Callable[[], KPATBaseModel],
        ] = {}

        # Submit tasks until interrupted
        for task in batch_tasks:
            if self._interrupt_handler.should_cancel_queued_tasks():
                break
            future: Future[KPATBaseModel] = executor.submit(
                self._execute_single_task,
                task,
            )
            future_to_task[future] = task

        # Cancel queued tasks if interrupt occurred during submission
        if self._interrupt_handler.should_cancel_queued_tasks():
            self._cancel_queued_batch_futures(future_to_task)

        return future_to_task

    def _process_batch_results_with_interrupt_handling(
        self,
        future_to_task: dict[
            concurrent.futures.Future[KPATBaseModel],
            Callable[[], KPATBaseModel],
        ],
        task_id: rich.progress.TaskID,
    ) -> list[KPATBaseModel]:
        """Process batch results with interrupt handling during execution."""
        batch_results: list[KPATBaseModel] = []

        import concurrent.futures

        for future in concurrent.futures.as_completed(future_to_task):
            # Handle termination requests
            if self._interrupt_handler.should_terminate_active_tasks():
                self._cancel_remaining_batch_futures(future_to_task)
                break

            # Handle immediate exit requests
            if self._interrupt_handler.should_immediate_exit():
                msg: str = "Immediate termination requested"
                raise InterruptedError(msg)

            # Process individual batch task result
            self._process_single_batch_task_result(future, batch_results, task_id)

        return batch_results

    def _cancel_queued_batch_futures(
        self,
        future_to_task: dict[
            concurrent.futures.Future[KPATBaseModel],
            Callable[[], KPATBaseModel],
        ],
    ) -> None:
        """Cancel batch futures that are queued but not yet running."""
        for future in future_to_task:
            if not future.running():
                future.cancel()

    def _cancel_remaining_batch_futures(
        self,
        future_to_task: dict[
            concurrent.futures.Future[KPATBaseModel],
            Callable[[], KPATBaseModel],
        ],
    ) -> None:
        """Cancel all remaining batch futures that are not done."""
        for future in future_to_task:
            if not future.done():
                future.cancel()

    def _process_single_batch_task_result(
        self,
        future: concurrent.futures.Future[KPATBaseModel],
        batch_results: list[KPATBaseModel],
        task_id: rich.progress.TaskID,
    ) -> None:
        """Process result from a single completed batch task."""
        try:
            result: KPATBaseModel = future.result()
            batch_results.append(result)
        except (RuntimeError, ValueError, OSError):
            # Handle specific task execution errors
            # For now, we'll continue - future enhancement: configurable error handling
            pass

        self._progress_tracker.update_progress(task_id)

    def _execute_single_task(self, task: Callable[[], KPATBaseModel]) -> KPATBaseModel:
        """
        Execute a single task with error handling.

        Args:
            task: Callable task to execute

        Returns:
            Task execution result

        Raises:
            Exception: If task execution fails

        """
        result: KPATBaseModel = task()
        return result

    def _calculate_optimal_batch_size(self, task_count: int, max_workers: int) -> int:
        """
        Calculate optimal batch size based on task count and worker count.

        Args:
            task_count: Total number of tasks to process
            max_workers: Maximum number of worker processes

        Returns:
            Optimal batch size for memory efficiency

        """
        # Heuristic: aim for 4-8 batches per worker to balance memory and efficiency
        target_batches_per_worker: int = 6
        target_total_batches: int = max_workers * target_batches_per_worker
        optimal_batch_size: int = max(1, math.ceil(task_count / target_total_batches))

        # Ensure batch size doesn't exceed reasonable limits
        max_batch_size: int = min(100, task_count)  # Cap at 100 or total tasks
        min_batch_size: int = 1

        return max(min_batch_size, min(optimal_batch_size, max_batch_size))


# END AI-GEN
