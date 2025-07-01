"""
Parallel execution engine for search operations.

Provides multi-process execution capabilities to improve performance
when processing large numbers of files and search configurations.
"""

import contextlib
import multiprocessing as mp
import signal
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Any, NamedTuple

from kp_analysis_toolkit.process_scripts.models.results.base import SearchResults
from kp_analysis_toolkit.process_scripts.models.search.base import SearchConfig
from kp_analysis_toolkit.process_scripts.models.systems import Systems
from kp_analysis_toolkit.utils.rich_output import get_rich_output


class ProcessingContext(NamedTuple):
    """Context for processing futures with common parameters."""

    future_to_config: dict[object, SearchConfig]
    results: list[SearchResults]
    progress: object
    search_task: int
    max_name_width: int
    rich_output: object


class InterruptHandler:
    """Thread-safe interrupt handler for graceful cancellation."""

    def __init__(self, rich_output) -> None:  # noqa: ANN001
        self.interrupted = False
        self.force_terminate = False
        self.original_handler = None
        self.rich_output = rich_output
        self._lock = mp.Lock()

    def handle_interrupt(self, _signum: int, _frame) -> None:  # noqa: ANN001
        """Handle keyboard interrupt signal."""
        with self._lock:
            if not self.interrupted:
                self.interrupted = True
                self.rich_output.warning(
                    "⚠️  Interrupt received! Finishing current searches and cancelling remaining...",
                )
            elif not self.force_terminate:
                self.force_terminate = True
                self.rich_output.error(
                    "🛑 Force termination requested! Stopping immediately...",
                )
            else:
                # Restore default handler and re-raise
                signal.signal(signal.SIGINT, signal.SIG_DFL)
                import os

                os.kill(os.getpid(), signal.SIGINT)

    def setup(self) -> None:
        """Set up the interrupt handler."""
        with contextlib.suppress(ValueError, OSError):
            self.original_handler = signal.signal(signal.SIGINT, self.handle_interrupt)

    def cleanup(self) -> None:
        """Restore the original interrupt handler."""
        if self.original_handler is not None:
            with contextlib.suppress(ValueError, OSError):
                signal.signal(signal.SIGINT, self.original_handler)

    def is_interrupted(self) -> bool:
        """Check if an interrupt has been received."""
        with self._lock:
            return self.interrupted

    def should_force_terminate(self) -> bool:
        """Check if immediate termination was requested."""
        with self._lock:
            return self.force_terminate


def _process_completed_future(future: object, context: ProcessingContext) -> None:
    """Process a completed future and update progress."""
    search_config = context.future_to_config[future]
    try:
        result = future.result()
        context.results.append(result)
        config_name = getattr(search_config, "name", "Unknown")
        context.progress.update(
            context.search_task,
            advance=1,
            description=f"Completed: {config_name:<{context.max_name_width}}",
        )
    except (OSError, RuntimeError, ValueError) as exc:
        context.rich_output.error(f"Search config '{search_config.name}' failed: {exc}")
        context.progress.advance(context.search_task)


def _handle_cancellation(
    remaining_futures: set[object],
    context: ProcessingContext,
    interrupt_handler: InterruptHandler,
) -> int:
    """Cancel remaining futures and return count of successfully cancelled."""
    if not remaining_futures:
        return 0

    context.rich_output.info(
        f"Cancelling {len(remaining_futures)} remaining searches...",
    )
    cancelled_count = 0
    running_futures = []

    # First pass: try to cancel pending futures
    for future in remaining_futures:
        if future.cancel():
            cancelled_count += 1
            search_config = context.future_to_config[future]
            config_name = getattr(search_config, "name", "Unknown")
            context.progress.update(
                context.search_task,
                advance=1,
                description=f"Cancelled: {config_name:<{context.max_name_width}}",
            )
        else:
            # Future is already running, can't be cancelled
            running_futures.append(future)

    if running_futures:
        context.rich_output.warning(
            f"⏳ Waiting for {len(running_futures)} running searches to complete...",
        )
        context.rich_output.info(
            "💡 Press CTRL-C again to force immediate termination (may lose data)",
        )

        # Wait for running futures with progress updates and force termination check
        for future in running_futures:
            if interrupt_handler.should_force_terminate():
                context.rich_output.warning(
                    "🛑 Force termination - abandoning remaining searches",
                )
                # Mark remaining as cancelled for progress tracking
                for remaining_future in running_futures[
                    running_futures.index(future) :
                ]:
                    search_config = context.future_to_config[remaining_future]
                    config_name = getattr(search_config, "name", "Unknown")
                    context.progress.update(
                        context.search_task,
                        advance=1,
                        description=f"Terminated: {config_name:<{context.max_name_width}}",
                    )
                break

            search_config = context.future_to_config[future]
            config_name = getattr(search_config, "name", "Unknown")

            try:
                # Wait for the running future to complete
                future.result()
                context.progress.update(
                    context.search_task,
                    advance=1,
                    description=f"Completed: {config_name:<{context.max_name_width}}",
                )
            except (OSError, RuntimeError, ValueError) as exc:
                context.rich_output.error(
                    f"Search config '{config_name}' failed: {exc}",
                )
                context.progress.advance(context.search_task)

    return cancelled_count


def _execute_search_loop(
    executor: ProcessPoolExecutor,
    search_configs: list[SearchConfig],
    systems: list[Systems],
    interrupt_handler: InterruptHandler,
    context: ProcessingContext,
) -> None:
    """Execute the main search loop with timeout-based polling for responsiveness."""
    # Submit all search configuration tasks
    future_to_config = {
        executor.submit(_execute_search_wrapper, search_config, systems): search_config
        for search_config in search_configs
    }
    # Update context with the mapping
    context = context._replace(future_to_config=future_to_config)

    # Main loop with timeout-based polling for responsiveness
    remaining_futures = set(future_to_config.keys())

    while remaining_futures and not interrupt_handler.is_interrupted():
        try:
            # Short timeout allows frequent interrupt checking
            completed_futures = as_completed(remaining_futures, timeout=0.5)

            for future in completed_futures:
                if interrupt_handler.is_interrupted():
                    break

                remaining_futures.remove(future)
                _process_completed_future(future, context)

        except TimeoutError:
            # No futures completed in timeout period - allows interrupt checking
            continue

    # Handle cancellation of remaining futures if interrupted
    if interrupt_handler.is_interrupted():
        cancelled_count = _handle_cancellation(
            remaining_futures,
            context,
            interrupt_handler,
        )
        if cancelled_count > 0:
            context.rich_output.success(
                f"✅ Successfully cancelled {cancelled_count} pending searches",
            )


def search_configs_with_processes(
    search_configs: list[SearchConfig],
    systems: list[Systems],
    max_workers: int,
) -> list[SearchResults]:
    """
    Execute multiple search configurations in parallel using processes.

    Features responsive KeyboardInterrupt handling that allows immediate
    cancellation with CTRL-C while maintaining progress display.

    Args:
        search_configs: List of search configurations to execute
        systems: List of systems to search
        max_workers: Maximum number of workers to use

    Returns:
        List of SearchResults for all executed searches

    """
    if not search_configs:
        return []

    # Ensure max_workers doesn't exceed the number of search configs
    max_workers = min(max_workers, len(search_configs))

    # Calculate the maximum width needed for search config names for consistent formatting
    max_name_width = max(
        len(getattr(config, "name", "Unknown")) for config in search_configs
    )

    results: list[SearchResults] = []
    rich_output = get_rich_output()

    # Set up interrupt handling
    interrupt_handler = InterruptHandler(rich_output)
    interrupt_handler.setup()

    try:
        with rich_output.progress(
            show_eta=True,
            show_percentage=True,
            show_time_elapsed=True,
        ) as progress:
            # Add progress task for search configurations
            search_task = progress.add_task(
                f"Executing {len(search_configs)} search configurations",
                total=len(search_configs),
            )

            # Create processing context
            context = ProcessingContext(
                future_to_config={},
                results=results,
                progress=progress,
                search_task=search_task,
                max_name_width=max_name_width,
                rich_output=rich_output,
            )

            with ProcessPoolExecutor(max_workers=max_workers) as executor:
                _execute_search_loop(
                    executor,
                    search_configs,
                    systems,
                    interrupt_handler,
                    context,
                )

    finally:
        interrupt_handler.cleanup()

    if interrupt_handler.is_interrupted():
        rich_output.warning(
            f"⚠️  Search interrupted by user. Completed {len(results)} out of {len(search_configs)} searches.",
        )

    return results


def _execute_search_wrapper(
    search_config: SearchConfig,
    systems: list[Systems],
) -> SearchResults:
    """
    Wrapper function for executing search in multiprocess context.

    This function is needed because search_single_system and related functions
    need to be importable in the worker processes.

    Args:
        search_config: Search configuration to execute
        systems: List of systems to search

    Returns:
        SearchResults containing all matches found

    """
    from kp_analysis_toolkit.process_scripts.search_engine import execute_search

    return execute_search(search_config, systems)


def benchmark_sequential_execution(
    search_configs: list[SearchConfig],
    systems: list[Systems],
) -> dict[str, Any]:
    """
    Benchmark sequential execution of search configurations.

    Args:
        search_configs: List of search configurations to execute
        systems: List of systems to search

    Returns:
        Dictionary containing benchmark results

    """
    from kp_analysis_toolkit.process_scripts.search_engine import execute_search

    start_time = time.time()

    results = []
    for search_config in search_configs:
        result = execute_search(search_config, systems)
        results.append(result)

    end_time = time.time()
    execution_time = end_time - start_time

    # Calculate total matches
    total_matches = sum(len(result.results) for result in results)

    # Calculate matches per second (avoid division by zero)
    matches_per_second = total_matches / execution_time if execution_time > 0 else 0

    return {
        "execution_time": execution_time,
        "results": results,
        "search_configs": len(search_configs),
        "total_systems": len(systems),
        "total_searches": len(search_configs),
        "total_matches": total_matches,
        "matches_per_second": matches_per_second,
        "systems": len(systems),
        "max_workers": 1,
        "parallel_execution": False,
    }


def benchmark_parallel_execution(
    search_configs: list[SearchConfig],
    systems: list[Systems],
    max_workers: int,
) -> dict[str, Any]:
    """
    Benchmark parallel execution of search configurations using processes.

    Args:
        search_configs: List of search configurations to execute
        systems: List of systems to search
        max_workers: Maximum number of workers to use

    Returns:
        Dictionary containing benchmark results

    """
    start_time = time.time()

    results: list[SearchResults] = search_configs_with_processes(
        search_configs,
        systems,
        max_workers,
    )

    end_time = time.time()
    execution_time = end_time - start_time

    # Calculate total matches
    total_matches = sum(len(result.results) for result in results)

    return {
        "execution_time": execution_time,
        "results": results,
        "search_configs": len(search_configs),
        "total_systems": len(systems),
        "total_searches": len(search_configs),
        "total_matches": total_matches,
        "systems": len(systems),
        "max_workers": max_workers,
        "parallel_execution": True,
        "execution_mode": "processes",
    }


def get_optimal_worker_count(num_tasks: int, task_type: str = "mixed") -> int:
    """
    Calculate the optimal number of workers based on task type and available resources.

    Args:
        num_tasks: Number of tasks to execute
        task_type: Type of tasks ('io', 'cpu', or 'mixed')

    Returns:
        Optimal number of workers

    """
    cpu_count: int = mp.cpu_count()

    if task_type == "io":
        # For I/O-bound tasks, we can use more workers than CPU cores
        return min(num_tasks, cpu_count * 2)
    if task_type == "cpu":
        # For CPU-bound tasks, limit to CPU cores
        return min(num_tasks, cpu_count)

    # For mixed tasks, use CPU cores as the limit
    return min(num_tasks, cpu_count)
