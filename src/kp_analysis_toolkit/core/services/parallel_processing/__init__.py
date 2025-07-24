# AI-GEN: GitHub Copilot|2025-01-24|parallel-processing-init|reviewed:no
"""Parallel processing service package for dependency injection."""

from .executor_factory import ProcessPoolExecutorFactory, ThreadPoolExecutorFactory
from .protocols import (
    ExecutorFactory,
    InterruptHandler,
    ParallelProcessingService,
    ProgressTracker,
    TaskResult,
)
from .task_result import DefaultTaskResult

__all__ = [
    "DefaultTaskResult",
    "ExecutorFactory",
    "InterruptHandler",
    "ParallelProcessingService",
    "ProcessPoolExecutorFactory",
    "ProgressTracker",
    "TaskResult",
    "ThreadPoolExecutorFactory",
]
# END AI-GEN
