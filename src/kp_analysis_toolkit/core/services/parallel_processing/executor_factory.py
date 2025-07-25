# AI-GEN: GitHub Copilot|2025-01-24|executor-factory-impl|reviewed:no
"""Concrete implementation of ExecutorFactory for creating process pool executors."""

from __future__ import annotations

import concurrent.futures

from kp_analysis_toolkit.core.services.parallel_processing.protocols import (
    ExecutorFactory,
)


class ProcessPoolExecutorFactory(ExecutorFactory):
    """Factory for creating ProcessPoolExecutor instances optimized for CPU-bound tasks."""

    def create_executor(self, max_workers: int) -> concurrent.futures.Executor:
        """
        Create a ProcessPoolExecutor configured for parallel processing.

        Args:
            max_workers: Maximum number of worker processes

        Returns:
            Configured ProcessPoolExecutor instance ready for task submission

        Raises:
            ValueError: If max_workers is invalid (<= 0)
            OSError: If system resources are insufficient for executor creation

        """
        if max_workers <= 0:
            msg: str = f"max_workers must be greater than 0, got {max_workers}"
            raise ValueError(msg)

        try:
            # Create ProcessPoolExecutor with the specified number of workers
            # ProcessPoolExecutor is ideal for CPU-bound tasks like:
            # - Search engine operations (regex processing)
            # - Excel export operations (data serialization)
            # - Any computation-heavy tasks that benefit from process isolation
            return concurrent.futures.ProcessPoolExecutor(
                max_workers=max_workers,
                # Use spawn method for better isolation and cross-platform compatibility
                mp_context=None,  # Use default multiprocessing context
            )
        except OSError as e:
            error_msg: str = (
                f"Failed to create ProcessPoolExecutor with {max_workers} workers: {e}"
            )
            raise OSError(error_msg) from e


class ThreadPoolExecutorFactory(ExecutorFactory):
    """Factory for creating ThreadPoolExecutor instances optimized for I/O-bound tasks."""

    def create_executor(self, max_workers: int) -> concurrent.futures.Executor:
        """
        Create a ThreadPoolExecutor configured for parallel processing.

        Args:
            max_workers: Maximum number of worker threads

        Returns:
            Configured ThreadPoolExecutor instance ready for task submission

        Raises:
            ValueError: If max_workers is invalid (<= 0)
            OSError: If system resources are insufficient for executor creation

        """
        if max_workers <= 0:
            msg: str = f"max_workers must be greater than 0, got {max_workers}"
            raise ValueError(msg)

        try:
            # Create ThreadPoolExecutor with the specified number of workers
            # ThreadPoolExecutor is ideal for I/O-bound tasks like:
            # - File reading/writing operations
            # - Network requests
            # - Database operations
            return concurrent.futures.ThreadPoolExecutor(
                max_workers=max_workers,
                thread_name_prefix="kpat-worker",
            )
        except OSError as e:
            error_msg: str = (
                f"Failed to create ThreadPoolExecutor with {max_workers} workers: {e}"
            )
            raise OSError(error_msg) from e


# END AI-GEN
