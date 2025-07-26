# AI-GEN: GitHub Copilot|2025-01-24|parallel-processing-init|reviewed:no
"""Parallel processing service package for dependency injection."""

from kp_analysis_toolkit.core.services.parallel_processing.executor_factory import (
    ProcessPoolExecutorFactory,
    ThreadPoolExecutorFactory,
)
from kp_analysis_toolkit.core.services.parallel_processing.interrupt_handler import (
    DefaultInterruptHandler,
)
from kp_analysis_toolkit.core.services.parallel_processing.progress_tracker import (
    DefaultProgressTracker,
)
from kp_analysis_toolkit.core.services.parallel_processing.protocols import (
    ExecutorFactory,
    InterruptHandler,
    ParallelProcessingService,
    ProgressTracker,
    TaskResult,
)
from kp_analysis_toolkit.core.services.parallel_processing.service import (
    DefaultParallelProcessingService,
)
from kp_analysis_toolkit.core.services.parallel_processing.task_result import (
    DefaultTaskResult,
)

__all__: list[str] = [
    "DefaultInterruptHandler",
    "DefaultParallelProcessingService",
    "DefaultProgressTracker",
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
