# AI-GEN: GitHub Copilot|2025-01-25|parallel-processing-fixtures|reviewed:no
"""Parallel processing test fixtures for the KP Analysis Toolkit."""

from __future__ import annotations

import concurrent.futures
from typing import TYPE_CHECKING, Any
from unittest.mock import MagicMock, Mock

import pytest
import rich.progress

if TYPE_CHECKING:
    from collections.abc import Callable, Generator

    from kp_analysis_toolkit.core.services.parallel_processing.interrupt_handler import (
        DefaultInterruptHandler,
    )
    from kp_analysis_toolkit.core.services.parallel_processing.progress_tracker import (
        DefaultProgressTracker,
    )


# =============================================================================
# EXECUTOR FACTORY FIXTURES
# =============================================================================


@pytest.fixture
def mock_process_pool_executor() -> MagicMock:
    """Create a mock ProcessPoolExecutor for testing."""
    executor: MagicMock = MagicMock(spec=concurrent.futures.ProcessPoolExecutor)

    # Setup context manager behavior
    executor.__enter__.return_value = executor
    executor.__exit__.return_value = None

    # Setup default submission behavior
    mock_future: MagicMock = MagicMock(spec=concurrent.futures.Future)
    mock_future.result.return_value = "mock_result"
    executor.submit.return_value = mock_future

    return executor


@pytest.fixture
def mock_thread_pool_executor() -> MagicMock:
    """Create a mock ThreadPoolExecutor for testing."""
    executor: MagicMock = MagicMock(spec=concurrent.futures.ThreadPoolExecutor)

    # Setup context manager behavior
    executor.__enter__.return_value = executor
    executor.__exit__.return_value = None

    # Setup default submission behavior
    mock_future: MagicMock = MagicMock(spec=concurrent.futures.Future)
    mock_future.result.return_value = "mock_result"
    executor.submit.return_value = mock_future

    return executor


@pytest.fixture
def mock_process_pool_executor_factory(
    mock_process_pool_executor: MagicMock,
) -> MagicMock:
    """Create a mock ProcessPoolExecutorFactory for testing."""
    from kp_analysis_toolkit.core.services.parallel_processing.protocols import (
        ExecutorFactory,
    )

    factory: MagicMock = Mock(spec=ExecutorFactory)
    factory.create_executor.return_value = mock_process_pool_executor

    return factory


@pytest.fixture
def mock_thread_pool_executor_factory(
    mock_thread_pool_executor: MagicMock,
) -> MagicMock:
    """Create a mock ThreadPoolExecutorFactory for testing."""
    from kp_analysis_toolkit.core.services.parallel_processing.protocols import (
        ExecutorFactory,
    )

    factory: MagicMock = Mock(spec=ExecutorFactory)
    factory.create_executor.return_value = mock_thread_pool_executor

    return factory


# =============================================================================
# PROGRESS TRACKING FIXTURES
# =============================================================================


@pytest.fixture
def mock_task_id() -> rich.progress.TaskID:
    """Create a mock TaskID for progress tracking tests."""
    return rich.progress.TaskID(1)


@pytest.fixture
def mock_progress_context() -> MagicMock:
    """Create a mock Progress context manager for testing."""
    progress: MagicMock = MagicMock(spec=rich.progress.Progress)

    # Setup context manager behavior
    progress.__enter__.return_value = progress
    progress.__exit__.return_value = None

    # Setup task management
    progress.add_task.return_value = rich.progress.TaskID(1)
    progress.update.return_value = None
    mock_task: MagicMock = MagicMock()
    mock_task.total = 100
    progress.tasks = {rich.progress.TaskID(1): mock_task}

    return progress


@pytest.fixture
def mock_progress_tracker() -> MagicMock:
    """Create a mock ProgressTracker for testing."""
    from kp_analysis_toolkit.core.services.parallel_processing.protocols import (
        ProgressTracker,
    )

    tracker: MagicMock = Mock(spec=ProgressTracker)

    # Setup context manager behavior
    tracker.__enter__.return_value = tracker
    tracker.__exit__.return_value = None

    # Setup default behaviors
    tracker.track_progress.return_value = rich.progress.TaskID(1)
    tracker.update_progress.return_value = None
    tracker.complete_progress.return_value = None

    return tracker


# =============================================================================
# INTERRUPT HANDLING FIXTURES
# =============================================================================


@pytest.fixture
def mock_interrupt_handler() -> MagicMock:
    """Create a mock InterruptHandler for testing."""
    from kp_analysis_toolkit.core.services.parallel_processing.protocols import (
        InterruptHandler,
    )

    handler: MagicMock = Mock(spec=InterruptHandler)

    # Setup context manager behavior
    handler.__enter__.return_value = handler
    handler.__exit__.return_value = None

    # Setup default interrupt state (no interruption)
    handler.is_interrupted.return_value = False
    handler.get_interrupt_stage.return_value = 0
    handler.should_cancel_queued_tasks.return_value = False
    handler.should_terminate_active_tasks.return_value = False
    handler.should_immediate_exit.return_value = False

    # Setup methods
    handler.setup.return_value = None
    handler.cleanup.return_value = None
    handler.handle_interrupt_stage.return_value = None

    return handler


@pytest.fixture
def mock_signal_handler() -> Generator[MagicMock, Any, None]:
    """Create a mock signal handler for testing interrupt scenarios."""
    from unittest.mock import patch

    with patch("signal.signal") as mock_signal:
        mock_signal.return_value = None
        yield mock_signal


# =============================================================================
# TASK AND RESULT FIXTURES
# =============================================================================


@pytest.fixture
def sample_kpat_model() -> MagicMock:
    """Create a sample KPATBaseModel instance for testing."""
    from kp_analysis_toolkit.models.base import KPATBaseModel

    model = MagicMock(spec=KPATBaseModel)
    model.model_dump.return_value = {"test": "data"}
    model.model_validate.return_value = model

    return model


@pytest.fixture
def mock_task_result_success(sample_kpat_model: MagicMock) -> MagicMock:
    """Create a mock successful TaskResult for testing."""
    from kp_analysis_toolkit.core.services.parallel_processing.protocols import (
        TaskResult,
    )

    result: MagicMock = Mock(spec=TaskResult)
    result.success = True
    result.error = None
    result.result = sample_kpat_model

    return result


@pytest.fixture
def mock_task_result_failure() -> MagicMock:
    """Create a mock failed TaskResult for testing."""
    from kp_analysis_toolkit.core.services.parallel_processing.protocols import (
        TaskResult,
    )

    result: MagicMock = Mock(spec=TaskResult)
    result.success = False
    result.error = Exception("Test error")

    # Should raise ValueError when accessing result on failed task
    def raise_error() -> None:
        msg: str = "Cannot access result when task failed"
        raise ValueError(msg)

    result.result = property(lambda _: raise_error())

    return result


@pytest.fixture
def mock_callable_tasks(sample_kpat_model: MagicMock) -> list[Callable[[], MagicMock]]:
    """Create a list of mock callable tasks for testing."""

    def create_mock_task(return_value: MagicMock) -> Callable[[], MagicMock]:
        def mock_task() -> MagicMock:
            return return_value

        return mock_task

    return [
        create_mock_task(sample_kpat_model),
        create_mock_task(sample_kpat_model),
        create_mock_task(sample_kpat_model),
    ]


@pytest.fixture
def mock_task_result_factory(
    mock_task_result_success: MagicMock,
) -> Callable[[], MagicMock]:
    """Create a mock task result factory for testing."""

    def factory() -> MagicMock:
        return mock_task_result_success

    return factory


# =============================================================================
# SERVICE INTEGRATION FIXTURES
# =============================================================================


@pytest.fixture
def mock_parallel_processing_service() -> MagicMock:
    """Create a mock ParallelProcessingService for testing."""
    from kp_analysis_toolkit.core.services.parallel_processing.protocols import (
        ParallelProcessingService,
    )

    service: MagicMock = Mock(spec=ParallelProcessingService)

    # Setup default behaviors
    service.execute_in_parallel.return_value = []
    service.execute_with_batching.return_value = []

    return service


@pytest.fixture
def parallel_processing_dependencies(
    mock_process_pool_executor_factory: MagicMock,
    mock_progress_tracker: MagicMock,
    mock_interrupt_handler: MagicMock,
    mock_task_result_factory: Callable[[], MagicMock],
) -> dict[str, MagicMock | Callable[[], MagicMock]]:
    """
    Create a complete set of parallel processing dependencies for testing.

    Returns a dictionary with all the dependencies needed to construct
    a DefaultParallelProcessingService for integration testing.
    """
    return {
        "executor_factory": mock_process_pool_executor_factory,
        "progress_tracker": mock_progress_tracker,
        "interrupt_handler": mock_interrupt_handler,
        "task_result_factory": mock_task_result_factory,
    }


# =============================================================================
# EXCEPTION FIXTURES
# =============================================================================


@pytest.fixture
def os_error_executor_factory() -> MagicMock:
    """Create an ExecutorFactory that raises OSError for testing error handling."""
    from kp_analysis_toolkit.core.services.parallel_processing.protocols import (
        ExecutorFactory,
    )

    factory: MagicMock = Mock(spec=ExecutorFactory)
    factory.create_executor.side_effect = OSError("System resources insufficient")

    return factory


@pytest.fixture
def value_error_executor_factory() -> MagicMock:
    """Create an ExecutorFactory that raises ValueError for testing validation."""
    from kp_analysis_toolkit.core.services.parallel_processing.protocols import (
        ExecutorFactory,
    )

    factory: MagicMock = Mock(spec=ExecutorFactory)
    factory.create_executor.side_effect = ValueError("Invalid max_workers")

    return factory


# =============================================================================
# PROGRESS TRACKER IMPLEMENTATION FIXTURES
# =============================================================================


@pytest.fixture
def mock_rich_progress_context() -> MagicMock:
    """Create a mock Rich Progress context for testing DefaultProgressTracker."""
    progress_context: MagicMock = MagicMock()
    progress_context.__enter__.return_value = progress_context
    progress_context.__exit__.return_value = None

    # Mock progress.add_task() to return a consistent task ID
    # Accept both positional and keyword arguments
    def mock_add_task(*_args: str, **_kwargs: int) -> rich.progress.TaskID:
        task_id = rich.progress.TaskID(1)
        # Add task to tasks dict for tracking
        mock_task = MagicMock()
        mock_task.total = _kwargs.get("total", 100)
        progress_context.tasks[task_id] = mock_task
        return task_id

    progress_context.add_task.side_effect = mock_add_task

    # Mock progress.tasks property for task access
    progress_context.tasks = {}

    return progress_context


@pytest.fixture
def mock_rich_output_service(mock_rich_progress_context: MagicMock) -> MagicMock:
    """Create a mock RichOutputService for testing progress tracker and interrupt handler."""
    from kp_analysis_toolkit.core.services.rich_output import RichOutputService

    service: MagicMock = Mock(spec=RichOutputService)

    # Mock progress context creation
    service.progress.return_value = mock_rich_progress_context

    # Mock output methods
    service.info.return_value = None
    service.warning.return_value = None
    service.error.return_value = None

    return service


@pytest.fixture
def default_progress_tracker(
    mock_rich_output_service: MagicMock,
) -> DefaultProgressTracker:
    """Create a DefaultProgressTracker instance for testing."""
    from kp_analysis_toolkit.core.services.parallel_processing.progress_tracker import (
        DefaultProgressTracker,
    )

    return DefaultProgressTracker(mock_rich_output_service)


# =============================================================================
# INTERRUPT HANDLER IMPLEMENTATION FIXTURES
# =============================================================================


@pytest.fixture
def mock_signal_module() -> Generator[MagicMock, Any, None]:
    """Create a mock signal module for testing interrupt handler."""
    from unittest.mock import patch

    with patch(
        "kp_analysis_toolkit.core.services.parallel_processing.interrupt_handler.signal",
    ) as mock_signal:
        # Mock signal handlers
        mock_signal.SIGINT = 2
        mock_signal.SIGTERM = 15
        mock_signal.signal.return_value = None

        yield mock_signal


@pytest.fixture
def mock_sys_exit() -> Generator[MagicMock, Any, None]:
    """Create a mock sys.exit for testing interrupt handler immediate exit."""
    from unittest.mock import patch

    with patch("sys.exit") as mock_exit:
        yield mock_exit


@pytest.fixture
def default_interrupt_handler(
    mock_rich_output_service: MagicMock,
) -> DefaultInterruptHandler:
    """Create a DefaultInterruptHandler instance for testing."""
    from kp_analysis_toolkit.core.services.parallel_processing.interrupt_handler import (
        DefaultInterruptHandler,
    )

    return DefaultInterruptHandler(mock_rich_output_service)


# =============================================================================
# INTERRUPT STAGE FIXTURES
# =============================================================================


@pytest.fixture
def interrupt_stage_no_interrupt() -> int:
    """Return the constant for no interrupt stage."""
    return 0


@pytest.fixture
def interrupt_stage_cancel_queued() -> int:
    """Return the constant for cancel queued tasks stage."""
    return 1


@pytest.fixture
def interrupt_stage_terminate_active() -> int:
    """Return the constant for terminate active tasks stage."""
    return 2


@pytest.fixture
def interrupt_stage_immediate_exit() -> int:
    """Return the constant for immediate exit stage."""
    return 3


# =============================================================================
# TASK ID FIXTURES
# =============================================================================


@pytest.fixture
def valid_task_id() -> rich.progress.TaskID:
    """Create a valid TaskID for testing."""
    return rich.progress.TaskID(1)


@pytest.fixture
def invalid_task_id() -> rich.progress.TaskID:
    """Create an invalid TaskID for testing."""
    return rich.progress.TaskID(999)


@pytest.fixture
def task_id() -> rich.progress.TaskID:
    """Create a TaskID for testing (alias for valid_task_id)."""
    return rich.progress.TaskID(1)


@pytest.fixture
def other_task_id() -> rich.progress.TaskID:
    """Create another TaskID for testing multiple tasks."""
    return rich.progress.TaskID(2)


# END AI-GEN
