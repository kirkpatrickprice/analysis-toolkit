# AI-GEN: GitHub Copilot|2025-01-27|parallel-processing-integration-fixtures|reviewed:no
"""
Integration test fixtures for parallel processing services.

These fixtures provide real implementations and timing scenarios for integration
testing, complementing the mocked fixtures in parallel_processing_fixtures.py.
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, Any
from unittest.mock import MagicMock

import pytest

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
from kp_analysis_toolkit.core.services.parallel_processing.service import (
    DefaultParallelProcessingService,
)
from kp_analysis_toolkit.core.services.parallel_processing.task_result import (
    DefaultTaskResult,
)
from kp_analysis_toolkit.models.base import KPATBaseModel

if TYPE_CHECKING:
    from collections.abc import Callable


# =============================================================================
# PICKLABLE TEST MODEL FOR PROCESS POOL TESTING
# =============================================================================


class PicklableTestModel(KPATBaseModel):
    """A simple picklable model for process pool testing."""

    task_id: int
    result_data: dict[str, Any]

    def model_dump(self, **_kwargs: object) -> dict[str, Any]:
        """Return the result data for testing."""
        return self.result_data


# =============================================================================
# MODULE-LEVEL PICKLABLE TASK FUNCTIONS
# =============================================================================


def cpu_intensive_task_function(task_id: int) -> PicklableTestModel:
    """CPU-intensive task function that can be pickled for process pool."""
    cpu_work_iterations: int = 100000
    total: int = 0
    for i in range(cpu_work_iterations):
        total += i * i

    return PicklableTestModel(
        task_id=task_id,
        result_data={
            "task_id": task_id,
            "cpu_result": total,
            "work_type": "cpu_intensive",
        },
    )


def io_intensive_task_function(task_id: int) -> PicklableTestModel:
    """I/O-intensive task function that can be pickled for process pool."""
    io_sleep_duration: float = 0.05
    time.sleep(io_sleep_duration)

    return PicklableTestModel(
        task_id=task_id,
        result_data={
            "task_id": task_id,
            "io_duration": io_sleep_duration,
            "work_type": "io_intensive",
        },
    )


# Process-pool compatible task wrapper functions
def cpu_task_0() -> PicklableTestModel:
    """CPU task 0 for process pool testing."""
    return cpu_intensive_task_function(0)


def cpu_task_1() -> PicklableTestModel:
    """CPU task 1 for process pool testing."""
    return cpu_intensive_task_function(1)


def cpu_task_2() -> PicklableTestModel:
    """CPU task 2 for process pool testing."""
    return cpu_intensive_task_function(2)


def cpu_task_3() -> PicklableTestModel:
    """CPU task 3 for process pool testing."""
    return cpu_intensive_task_function(3)


def io_task_0() -> PicklableTestModel:
    """I/O task 0 for process pool testing."""
    return io_intensive_task_function(0)


def io_task_1() -> PicklableTestModel:
    """I/O task 1 for process pool testing."""
    return io_intensive_task_function(1)


def io_task_2() -> PicklableTestModel:
    """I/O task 2 for process pool testing."""
    return io_intensive_task_function(2)


def io_task_3() -> PicklableTestModel:
    """I/O task 3 for process pool testing."""
    return io_intensive_task_function(3)


def io_task_4() -> PicklableTestModel:
    """I/O task 4 for process pool testing."""
    return io_intensive_task_function(4)


def io_task_5() -> PicklableTestModel:
    """I/O task 5 for process pool testing."""
    return io_intensive_task_function(5)


# =============================================================================
# REAL IMPLEMENTATION FIXTURES
# =============================================================================


@pytest.fixture
def real_thread_executor_factory() -> ThreadPoolExecutorFactory:
    """Create a real executor factory using ThreadPoolExecutor for integration tests."""
    return ThreadPoolExecutorFactory()


@pytest.fixture
def real_process_executor_factory() -> ProcessPoolExecutorFactory:
    """Create a real executor factory using ProcessPoolExecutor for integration tests."""
    return ProcessPoolExecutorFactory()


@pytest.fixture
def mock_rich_output_for_integration() -> MagicMock:
    """Create a mock RichOutputService optimized for integration tests."""
    from kp_analysis_toolkit.core.services.rich_output import RichOutputService

    service: MagicMock = MagicMock(spec=RichOutputService)

    # Create a functioning progress context that works with real implementations
    progress_context: MagicMock = MagicMock()
    progress_context.__enter__ = MagicMock(return_value=progress_context)
    progress_context.__exit__ = MagicMock(return_value=None)
    progress_context.add_task = MagicMock(return_value=1)
    progress_context.update = MagicMock()
    progress_context.tasks = {1: MagicMock(total=100)}

    service.progress.return_value = progress_context
    service.info.return_value = None
    service.warning.return_value = None
    service.error.return_value = None

    return service


@pytest.fixture
def real_progress_tracker(
    mock_rich_output_for_integration: MagicMock,
) -> DefaultProgressTracker:
    """Create a real progress tracker for integration tests."""
    return DefaultProgressTracker(mock_rich_output_for_integration)


@pytest.fixture
def real_interrupt_handler(
    mock_rich_output_for_integration: MagicMock,
) -> DefaultInterruptHandler:
    """Create a real interrupt handler for integration tests."""
    return DefaultInterruptHandler(mock_rich_output_for_integration)


@pytest.fixture
def real_task_result_factory() -> Callable[[], DefaultTaskResult]:
    """Create a real task result factory for integration tests."""

    def factory() -> DefaultTaskResult:
        # Create a mock result for successful task completion
        mock_result: MagicMock = MagicMock(spec=KPATBaseModel)
        mock_result.model_dump.return_value = {"factory_test": "success"}
        return DefaultTaskResult(success=True, result=mock_result)

    return factory


@pytest.fixture
def real_parallel_processing_service_thread(
    real_thread_executor_factory: ThreadPoolExecutorFactory,
    real_progress_tracker: DefaultProgressTracker,
    real_interrupt_handler: DefaultInterruptHandler,
    real_task_result_factory: Callable[[], DefaultTaskResult],
) -> DefaultParallelProcessingService:
    """Create a real parallel processing service with ThreadPoolExecutor."""
    return DefaultParallelProcessingService(
        executor_factory=real_thread_executor_factory,
        progress_tracker=real_progress_tracker,
        interrupt_handler=real_interrupt_handler,
        task_result_factory=real_task_result_factory,
    )


@pytest.fixture
def real_parallel_processing_service_process(
    real_process_executor_factory: ProcessPoolExecutorFactory,
    real_progress_tracker: DefaultProgressTracker,
    real_interrupt_handler: DefaultInterruptHandler,
    real_task_result_factory: Callable[[], DefaultTaskResult],
) -> DefaultParallelProcessingService:
    """Create a real parallel processing service with ProcessPoolExecutor."""
    return DefaultParallelProcessingService(
        executor_factory=real_process_executor_factory,
        progress_tracker=real_progress_tracker,
        interrupt_handler=real_interrupt_handler,
        task_result_factory=real_task_result_factory,
    )


# =============================================================================
# INTEGRATION TEST TASK FIXTURES
# =============================================================================


@pytest.fixture
def sample_integration_model() -> KPATBaseModel:
    """Create a sample KPATBaseModel for integration testing."""
    model: MagicMock = MagicMock(spec=KPATBaseModel)
    model.model_dump.return_value = {"integration_test": "data"}
    return model


@pytest.fixture
def fast_integration_tasks() -> list[Callable[[], KPATBaseModel]]:
    """Create fast-executing tasks for integration testing."""
    # Performance constants
    fast_task_delay: float = 0.01
    fast_task_count: int = 5

    def create_fast_task(task_id: int) -> Callable[[], KPATBaseModel]:
        def task() -> KPATBaseModel:
            # Small delay to simulate work but keep tests fast
            time.sleep(fast_task_delay)
            result: MagicMock = MagicMock(spec=KPATBaseModel)
            result.model_dump.return_value = {"task_id": task_id, "result": "completed"}
            return result

        return task

    return [create_fast_task(i) for i in range(fast_task_count)]


@pytest.fixture
def slow_integration_tasks() -> list[Callable[[], KPATBaseModel]]:
    """Create slower tasks for interrupt testing scenarios."""
    # Performance constants
    slow_task_delay: float = 0.1
    slow_task_count: int = 10

    def create_slow_task(task_id: int) -> Callable[[], KPATBaseModel]:
        def task() -> KPATBaseModel:
            # Longer delay to allow interrupt scenarios
            time.sleep(slow_task_delay)
            result: MagicMock = MagicMock(spec=KPATBaseModel)
            result.model_dump.return_value = {
                "task_id": task_id,
                "result": "slow_completed",
            }
            return result

        return task

    return [create_slow_task(i) for i in range(slow_task_count)]


@pytest.fixture
def mixed_duration_integration_tasks() -> list[Callable[[], KPATBaseModel]]:
    """Create tasks with mixed execution times for realistic testing."""

    def create_variable_task(
        duration: float,
        task_id: int,
    ) -> Callable[[], KPATBaseModel]:
        def task() -> KPATBaseModel:
            time.sleep(duration)
            result: MagicMock = MagicMock(spec=KPATBaseModel)
            result.model_dump.return_value = {
                "task_id": task_id,
                "duration": duration,
                "result": "variable_completed",
            }
            return result

        return task

    # Mix of fast and slower tasks for realistic workload simulation
    durations: list[float] = [0.01, 0.05, 0.02, 0.03, 0.01, 0.04, 0.02, 0.01]
    return [create_variable_task(dur, i) for i, dur in enumerate(durations)]


@pytest.fixture
def large_task_batch_integration() -> list[Callable[[], KPATBaseModel]]:
    """Create a large batch of tasks for batching integration tests."""
    # Batch constants
    batch_task_delay: float = 0.001
    large_batch_size: int = 100

    def create_batch_task(task_id: int) -> Callable[[], KPATBaseModel]:
        def task() -> KPATBaseModel:
            # Very fast tasks for large batches to keep tests responsive
            time.sleep(batch_task_delay)
            result: MagicMock = MagicMock(spec=KPATBaseModel)
            result.model_dump.return_value = {"batch_task_id": task_id}
            return result

        return task

    return [create_batch_task(i) for i in range(large_batch_size)]


@pytest.fixture
def cpu_intensive_tasks() -> list[Callable[[], KPATBaseModel]]:
    """Create CPU-intensive tasks for process pool testing."""
    # Use module-level functions that are directly picklable
    return [cpu_task_0, cpu_task_1, cpu_task_2, cpu_task_3]


@pytest.fixture
def io_intensive_tasks() -> list[Callable[[], KPATBaseModel]]:
    """Create I/O-intensive tasks for thread pool testing."""
    # Use module-level functions that are directly picklable
    return [io_task_0, io_task_1, io_task_2, io_task_3, io_task_4, io_task_5]


# =============================================================================
# ERROR SCENARIO FIXTURES FOR INTEGRATION TESTS
# =============================================================================


@pytest.fixture
def mixed_success_failure_tasks() -> list[Callable[[], KPATBaseModel]]:
    """Create a mix of successful and failing tasks for error handling tests."""

    def create_success_task(task_id: int) -> Callable[[], KPATBaseModel]:
        def task() -> KPATBaseModel:
            time.sleep(0.01)  # Small delay for realism
            result: MagicMock = MagicMock(spec=KPATBaseModel)
            result.model_dump.return_value = {"task_id": task_id, "status": "success"}
            return result

        return task

    def create_failure_task(task_id: int) -> Callable[[], KPATBaseModel]:
        def task() -> KPATBaseModel:
            time.sleep(0.01)  # Small delay before failing
            error_msg: str = f"Task {task_id} failed during execution"
            raise RuntimeError(error_msg)

        return task

    # Mix of success and failure tasks
    tasks: list[Callable[[], KPATBaseModel]] = [
        create_success_task(0),
        create_failure_task(1),
        create_success_task(2),
        create_failure_task(3),
        create_success_task(4),
    ]
    return tasks


@pytest.fixture
def all_failing_tasks() -> list[Callable[[], KPATBaseModel]]:
    """Create tasks that all fail for comprehensive error handling tests."""
    # Error constants
    failing_task_count: int = 3

    def create_failing_task(task_id: int) -> Callable[[], KPATBaseModel]:
        def task() -> KPATBaseModel:
            error_msg: str = f"All tasks are failing - task {task_id}"
            raise ValueError(error_msg)

        return task

    return [create_failing_task(i) for i in range(failing_task_count)]


@pytest.fixture
def timeout_prone_tasks() -> list[Callable[[], KPATBaseModel]]:
    """Create tasks prone to timeout for timeout handling tests."""
    # Timeout constants
    timeout_delay: float = 2.0  # Long enough to potentially timeout
    timeout_task_count: int = 2

    def create_timeout_task(task_id: int) -> Callable[[], KPATBaseModel]:
        def task() -> KPATBaseModel:
            # Simulate a task that might timeout
            time.sleep(timeout_delay)
            result: MagicMock = MagicMock(spec=KPATBaseModel)
            result.model_dump.return_value = {
                "task_id": task_id,
                "delay": timeout_delay,
                "status": "completed_after_delay",
            }
            return result

        return task

    return [create_timeout_task(i) for i in range(timeout_task_count)]


# =============================================================================
# PERFORMANCE TESTING FIXTURES
# =============================================================================


@pytest.fixture
def sequential_benchmark_tasks() -> list[Callable[[], KPATBaseModel]]:
    """Create tasks for sequential vs parallel performance comparison."""
    # Benchmark constants
    benchmark_delay: float = 0.1
    benchmark_task_count: int = 8

    def create_benchmark_task(task_id: int) -> Callable[[], KPATBaseModel]:
        def task() -> KPATBaseModel:
            # Consistent delay for fair performance comparison
            time.sleep(benchmark_delay)
            result: MagicMock = MagicMock(spec=KPATBaseModel)
            result.model_dump.return_value = {
                "task_id": task_id,
                "benchmark_delay": benchmark_delay,
                "execution_type": "benchmark",
            }
            return result

        return task

    return [create_benchmark_task(i) for i in range(benchmark_task_count)]


# =============================================================================
# BATCHING TEST FIXTURES
# =============================================================================


@pytest.fixture
def small_batch_tasks() -> list[Callable[[], KPATBaseModel]]:
    """Create a small number of tasks for batch size testing."""
    # Small batch constants
    small_batch_count: int = 3

    def create_small_batch_task(task_id: int) -> Callable[[], KPATBaseModel]:
        def task() -> KPATBaseModel:
            time.sleep(0.01)
            result: MagicMock = MagicMock(spec=KPATBaseModel)
            result.model_dump.return_value = {
                "task_id": task_id,
                "batch_type": "small",
            }
            return result

        return task

    return [create_small_batch_task(i) for i in range(small_batch_count)]


@pytest.fixture
def variable_batch_sizes() -> list[int]:
    """Provide various batch sizes for batching integration tests."""
    return [1, 5, 10, 25, 50]


@pytest.fixture
def variable_worker_counts() -> list[int]:
    """Provide various worker counts for concurrency integration tests."""
    return [1, 2, 4, 8]


# =============================================================================
# INTEGRATION TEST CONSTANTS
# =============================================================================


@pytest.fixture
def performance_thresholds() -> dict[str, float]:
    """Performance thresholds for integration test assertions."""
    return {
        "min_parallel_improvement_ratio": 1.5,  # Parallel should be 50% faster
        "max_acceptable_execution_time": 5.0,  # Tests should complete in 5 seconds
        "fast_task_max_time": 1.0,  # Fast tasks should finish quickly
        "sequential_timeout": 10.0,  # Sequential fallback timeout
    }


# END AI-GEN
