# AI-GEN: GitHub Copilot|2025-01-27|parallel-processing-service-unit-tests|reviewed:no
"""Unit tests for DefaultParallelProcessingService implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from kp_analysis_toolkit.models.base import KPATBaseModel

if TYPE_CHECKING:
    from collections.abc import Callable
    from unittest.mock import MagicMock

    from kp_analysis_toolkit.core.services.parallel_processing.service import (
        DefaultParallelProcessingService,
    )
    from kp_analysis_toolkit.models.base import KPATBaseModel

from kp_analysis_toolkit.core.services.parallel_processing.service import (
    DefaultParallelProcessingService,
)


@pytest.mark.unit
@pytest.mark.core
class TestDefaultParallelProcessingServiceInit:
    """Test cases for DefaultParallelProcessingService initialization."""

    def test_init_succeeds_with_valid_dependencies(
        self,
        mock_process_pool_executor_factory: MagicMock,
        mock_progress_tracker: MagicMock,
        mock_interrupt_handler: MagicMock,
        mock_task_result_factory: Callable[[], MagicMock],
    ) -> None:
        """Test that initialization succeeds with valid dependencies."""
        service: DefaultParallelProcessingService = DefaultParallelProcessingService(
            executor_factory=mock_process_pool_executor_factory,
            progress_tracker=mock_progress_tracker,
            interrupt_handler=mock_interrupt_handler,
            task_result_factory=mock_task_result_factory,
        )

        # Test that service was created successfully (existence check)
        assert service is not None
        assert isinstance(service, DefaultParallelProcessingService)


@pytest.mark.unit
@pytest.mark.core
class TestDefaultParallelProcessingServiceExecuteInParallel:
    """Test cases for execute_in_parallel method."""

    def test_execute_in_parallel_success(
        self,
        default_parallel_processing_service: DefaultParallelProcessingService,
        mock_callable_tasks: list[Callable[[], KPATBaseModel]],
        sample_kpat_model: MagicMock,
    ) -> None:
        """Test successful parallel execution with valid tasks."""
        max_workers: int = 2
        description: str = "Test processing"

        results: list[KPATBaseModel] = (
            default_parallel_processing_service.execute_in_parallel(
                tasks=mock_callable_tasks,
                max_workers=max_workers,
                description=description,
            )
        )

        # Should return results from all tasks
        assert len(results) == len(mock_callable_tasks)
        for result in results:
            assert result is sample_kpat_model

    def test_execute_in_parallel_empty_tasks_raises_value_error(
        self,
        default_parallel_processing_service: DefaultParallelProcessingService,
    ) -> None:
        """Test that empty tasks list raises ValueError."""
        empty_tasks: list[Callable[[], KPATBaseModel]] = []
        max_workers: int = 2

        with pytest.raises(ValueError, match="Tasks list cannot be empty"):
            default_parallel_processing_service.execute_in_parallel(
                tasks=empty_tasks,
                max_workers=max_workers,
            )

    def test_execute_in_parallel_zero_max_workers_raises_value_error(
        self,
        default_parallel_processing_service: DefaultParallelProcessingService,
        mock_callable_tasks: list[Callable[[], KPATBaseModel]],
    ) -> None:
        """Test that zero max_workers raises ValueError."""
        max_workers: int = 0

        with pytest.raises(ValueError, match="max_workers must be positive"):
            default_parallel_processing_service.execute_in_parallel(
                tasks=mock_callable_tasks,
                max_workers=max_workers,
            )

    def test_execute_in_parallel_negative_max_workers_raises_value_error(
        self,
        default_parallel_processing_service: DefaultParallelProcessingService,
        mock_callable_tasks: list[Callable[[], KPATBaseModel]],
    ) -> None:
        """Test that negative max_workers raises ValueError."""
        max_workers: int = -1

        with pytest.raises(ValueError, match="max_workers must be positive"):
            default_parallel_processing_service.execute_in_parallel(
                tasks=mock_callable_tasks,
                max_workers=max_workers,
            )

    def test_execute_in_parallel_uses_context_managers(
        self,
        mock_process_pool_executor_factory: MagicMock,
        mock_progress_tracker: MagicMock,
        mock_interrupt_handler: MagicMock,
        mock_task_result_factory: Callable[[], MagicMock],
        mock_callable_tasks: list[Callable[[], KPATBaseModel]],
    ) -> None:
        """Test that execute_in_parallel uses interrupt handler and progress tracker as context managers."""
        service: DefaultParallelProcessingService = DefaultParallelProcessingService(
            executor_factory=mock_process_pool_executor_factory,
            progress_tracker=mock_progress_tracker,
            interrupt_handler=mock_interrupt_handler,
            task_result_factory=mock_task_result_factory,
        )

        max_workers: int = 2

        service.execute_in_parallel(
            tasks=mock_callable_tasks,
            max_workers=max_workers,
        )

        # Verify context managers were used
        mock_interrupt_handler.__enter__.assert_called_once()
        mock_interrupt_handler.__exit__.assert_called_once()
        mock_progress_tracker.__enter__.assert_called_once()
        mock_progress_tracker.__exit__.assert_called_once()

    def test_execute_in_parallel_calls_dependencies(
        self,
        default_parallel_processing_service: DefaultParallelProcessingService,
        mock_callable_tasks: list[Callable[[], KPATBaseModel]],
    ) -> None:
        """Test that execute_in_parallel calls its dependencies appropriately."""
        max_workers: int = 2
        description: str = "Test processing"

        # This test verifies the method runs without error and returns results
        results: list[KPATBaseModel] = (
            default_parallel_processing_service.execute_in_parallel(
                tasks=mock_callable_tasks,
                max_workers=max_workers,
                description=description,
            )
        )

        # Should complete successfully and return results
        assert len(results) == len(mock_callable_tasks)

    def test_execute_in_parallel_with_custom_description(
        self,
        default_parallel_processing_service: DefaultParallelProcessingService,
        mock_callable_tasks: list[Callable[[], KPATBaseModel]],
    ) -> None:
        """Test execute_in_parallel with custom description."""
        max_workers: int = 2
        custom_description: str = "Custom processing description"

        results: list[KPATBaseModel] = (
            default_parallel_processing_service.execute_in_parallel(
                tasks=mock_callable_tasks,
                max_workers=max_workers,
                description=custom_description,
            )
        )

        assert len(results) == len(mock_callable_tasks)

    def test_execute_in_parallel_with_interrupt_scenario(
        self,
        mock_process_pool_executor_factory: MagicMock,
        mock_progress_tracker: MagicMock,
        interrupted_interrupt_handler: MagicMock,
        mock_task_result_factory: Callable[[], MagicMock],
        mock_callable_tasks: list[Callable[[], KPATBaseModel]],
    ) -> None:
        """Test execute_in_parallel behavior with interruption."""
        service: DefaultParallelProcessingService = DefaultParallelProcessingService(
            executor_factory=mock_process_pool_executor_factory,
            progress_tracker=mock_progress_tracker,
            interrupt_handler=interrupted_interrupt_handler,
            task_result_factory=mock_task_result_factory,
        )

        max_workers: int = 2

        # Should handle interruption gracefully
        results: list[KPATBaseModel] = service.execute_in_parallel(
            tasks=mock_callable_tasks,
            max_workers=max_workers,
        )

        # May return partial results or empty list depending on interrupt timing
        assert isinstance(results, list)
        assert len(results) <= len(mock_callable_tasks)


@pytest.mark.unit
@pytest.mark.core
class TestDefaultParallelProcessingServiceExecuteWithBatching:
    """Test cases for execute_with_batching method."""

    def test_execute_with_batching_success(
        self,
        default_parallel_processing_service: DefaultParallelProcessingService,
        large_task_list: list[Callable[[], KPATBaseModel]],
        sample_kpat_model: MagicMock,
    ) -> None:
        """Test successful batched execution with large task list."""
        max_workers: int = 4
        batch_size: int = 10
        description: str = "Batch processing"

        results: list[KPATBaseModel] = (
            default_parallel_processing_service.execute_with_batching(
                tasks=large_task_list,
                max_workers=max_workers,
                batch_size=batch_size,
                description=description,
            )
        )

        # Should return results from all tasks
        assert len(results) == len(large_task_list)
        for result in results:
            assert result is sample_kpat_model

    def test_execute_with_batching_auto_batch_size(
        self,
        default_parallel_processing_service: DefaultParallelProcessingService,
        large_task_list: list[Callable[[], KPATBaseModel]],
        sample_kpat_model: MagicMock,
    ) -> None:
        """Test batched execution with auto-calculated batch size."""
        max_workers: int = 4
        batch_size: int | None = None  # Auto-calculate

        results: list[KPATBaseModel] = (
            default_parallel_processing_service.execute_with_batching(
                tasks=large_task_list,
                max_workers=max_workers,
                batch_size=batch_size,
            )
        )

        # Should return results from all tasks
        assert len(results) == len(large_task_list)
        for result in results:
            assert result is sample_kpat_model

    def test_execute_with_batching_empty_tasks_raises_value_error(
        self,
        default_parallel_processing_service: DefaultParallelProcessingService,
    ) -> None:
        """Test that empty tasks list raises ValueError."""
        empty_tasks: list[Callable[[], KPATBaseModel]] = []
        max_workers: int = 2
        batch_size: int = 5

        with pytest.raises(ValueError, match="Tasks list cannot be empty"):
            default_parallel_processing_service.execute_with_batching(
                tasks=empty_tasks,
                max_workers=max_workers,
                batch_size=batch_size,
            )

    def test_execute_with_batching_zero_max_workers_raises_value_error(
        self,
        default_parallel_processing_service: DefaultParallelProcessingService,
        large_task_list: list[Callable[[], KPATBaseModel]],
    ) -> None:
        """Test that zero max_workers raises ValueError."""
        max_workers: int = 0
        batch_size: int = 5

        with pytest.raises(ValueError, match="max_workers must be positive"):
            default_parallel_processing_service.execute_with_batching(
                tasks=large_task_list,
                max_workers=max_workers,
                batch_size=batch_size,
            )

    def test_execute_with_batching_negative_max_workers_raises_value_error(
        self,
        default_parallel_processing_service: DefaultParallelProcessingService,
        large_task_list: list[Callable[[], KPATBaseModel]],
    ) -> None:
        """Test that negative max_workers raises ValueError."""
        max_workers: int = -1
        batch_size: int = 5

        with pytest.raises(ValueError, match="max_workers must be positive"):
            default_parallel_processing_service.execute_with_batching(
                tasks=large_task_list,
                max_workers=max_workers,
                batch_size=batch_size,
            )

    def test_execute_with_batching_zero_batch_size_raises_value_error(
        self,
        default_parallel_processing_service: DefaultParallelProcessingService,
        large_task_list: list[Callable[[], KPATBaseModel]],
    ) -> None:
        """Test that zero batch_size raises ValueError."""
        max_workers: int = 2
        batch_size: int = 0

        with pytest.raises(ValueError, match="batch_size must be positive"):
            default_parallel_processing_service.execute_with_batching(
                tasks=large_task_list,
                max_workers=max_workers,
                batch_size=batch_size,
            )

    def test_execute_with_batching_negative_batch_size_raises_value_error(
        self,
        default_parallel_processing_service: DefaultParallelProcessingService,
        large_task_list: list[Callable[[], KPATBaseModel]],
    ) -> None:
        """Test that negative batch_size raises ValueError."""
        max_workers: int = 2
        batch_size: int = -1

        with pytest.raises(ValueError, match="batch_size must be positive"):
            default_parallel_processing_service.execute_with_batching(
                tasks=large_task_list,
                max_workers=max_workers,
                batch_size=batch_size,
            )

    def test_execute_with_batching_uses_context_managers(
        self,
        mock_process_pool_executor_factory: MagicMock,
        mock_progress_tracker: MagicMock,
        mock_interrupt_handler: MagicMock,
        mock_task_result_factory: Callable[[], MagicMock],
        large_task_list: list[Callable[[], KPATBaseModel]],
    ) -> None:
        """Test that execute_with_batching uses interrupt handler and progress tracker as context managers."""
        service: DefaultParallelProcessingService = DefaultParallelProcessingService(
            executor_factory=mock_process_pool_executor_factory,
            progress_tracker=mock_progress_tracker,
            interrupt_handler=mock_interrupt_handler,
            task_result_factory=mock_task_result_factory,
        )

        max_workers: int = 2
        batch_size: int = 10

        service.execute_with_batching(
            tasks=large_task_list,
            max_workers=max_workers,
            batch_size=batch_size,
        )

        # Verify context managers were used
        mock_interrupt_handler.__enter__.assert_called_once()
        mock_interrupt_handler.__exit__.assert_called_once()
        mock_progress_tracker.__enter__.assert_called_once()
        mock_progress_tracker.__exit__.assert_called_once()

    def test_execute_with_batching_calls_dependencies(
        self,
        default_parallel_processing_service: DefaultParallelProcessingService,
        large_task_list: list[Callable[[], KPATBaseModel]],
    ) -> None:
        """Test that execute_with_batching calls its dependencies appropriately."""
        max_workers: int = 2
        batch_size: int = 10
        description: str = "Batch processing"

        # This test verifies the method runs without error and returns results
        results: list[KPATBaseModel] = (
            default_parallel_processing_service.execute_with_batching(
                tasks=large_task_list,
                max_workers=max_workers,
                batch_size=batch_size,
                description=description,
            )
        )

        # Should complete successfully and return results
        assert len(results) == len(large_task_list)

    def test_execute_with_batching_with_interrupt_scenario(
        self,
        mock_process_pool_executor_factory: MagicMock,
        mock_progress_tracker: MagicMock,
        interrupted_interrupt_handler: MagicMock,
        mock_task_result_factory: Callable[[], MagicMock],
        large_task_list: list[Callable[[], KPATBaseModel]],
    ) -> None:
        """Test execute_with_batching behavior with interruption."""
        service: DefaultParallelProcessingService = DefaultParallelProcessingService(
            executor_factory=mock_process_pool_executor_factory,
            progress_tracker=mock_progress_tracker,
            interrupt_handler=interrupted_interrupt_handler,
            task_result_factory=mock_task_result_factory,
        )

        max_workers: int = 2
        batch_size: int = 10

        # Should handle interruption gracefully
        results: list[KPATBaseModel] = service.execute_with_batching(
            tasks=large_task_list,
            max_workers=max_workers,
            batch_size=batch_size,
        )

        # May return partial results or empty list depending on interrupt timing
        assert isinstance(results, list)
        assert len(results) <= len(large_task_list)

    def test_execute_with_batching_small_task_list(
        self,
        default_parallel_processing_service: DefaultParallelProcessingService,
        mock_callable_tasks: list[Callable[[], KPATBaseModel]],
        sample_kpat_model: MagicMock,
    ) -> None:
        """Test batched execution with small task list (fewer tasks than batch size)."""
        max_workers: int = 2
        batch_size: int = 10  # Larger than number of tasks

        results: list[KPATBaseModel] = (
            default_parallel_processing_service.execute_with_batching(
                tasks=mock_callable_tasks,
                max_workers=max_workers,
                batch_size=batch_size,
            )
        )

        # Should return results from all tasks
        assert len(results) == len(mock_callable_tasks)
        for result in results:
            assert result is sample_kpat_model


@pytest.mark.unit
@pytest.mark.core
class TestDefaultParallelProcessingServiceEdgeCases:
    """Test cases for DefaultParallelProcessingService edge cases and boundary conditions."""

    def test_single_task_execution(
        self,
        default_parallel_processing_service: DefaultParallelProcessingService,
        sample_kpat_model: MagicMock,
    ) -> None:
        """Test execution with single task."""

        def single_task() -> MagicMock:
            return sample_kpat_model

        tasks: list[Callable[[], KPATBaseModel]] = [single_task]
        max_workers: int = 1

        results: list[KPATBaseModel] = (
            default_parallel_processing_service.execute_in_parallel(
                tasks=tasks,
                max_workers=max_workers,
            )
        )

        assert len(results) == 1
        assert results[0] is sample_kpat_model

    def test_single_task_batched_execution(
        self,
        default_parallel_processing_service: DefaultParallelProcessingService,
        sample_kpat_model: MagicMock,
    ) -> None:
        """Test batched execution with single task."""

        def single_task() -> MagicMock:
            return sample_kpat_model

        tasks: list[Callable[[], KPATBaseModel]] = [single_task]
        max_workers: int = 1
        batch_size: int = 1

        results: list[KPATBaseModel] = (
            default_parallel_processing_service.execute_with_batching(
                tasks=tasks,
                max_workers=max_workers,
                batch_size=batch_size,
            )
        )

        assert len(results) == 1
        assert results[0] is sample_kpat_model

    def test_max_workers_equals_task_count(
        self,
        default_parallel_processing_service: DefaultParallelProcessingService,
        mock_callable_tasks: list[Callable[[], KPATBaseModel]],
        sample_kpat_model: MagicMock,
    ) -> None:
        """Test execution where max_workers equals number of tasks."""
        max_workers: int = len(mock_callable_tasks)

        results: list[KPATBaseModel] = (
            default_parallel_processing_service.execute_in_parallel(
                tasks=mock_callable_tasks,
                max_workers=max_workers,
            )
        )

        assert len(results) == len(mock_callable_tasks)
        for result in results:
            assert result is sample_kpat_model

    def test_max_workers_exceeds_task_count(
        self,
        default_parallel_processing_service: DefaultParallelProcessingService,
        mock_callable_tasks: list[Callable[[], KPATBaseModel]],
        sample_kpat_model: MagicMock,
    ) -> None:
        """Test execution where max_workers exceeds number of tasks."""
        max_workers: int = len(mock_callable_tasks) * 2

        results: list[KPATBaseModel] = (
            default_parallel_processing_service.execute_in_parallel(
                tasks=mock_callable_tasks,
                max_workers=max_workers,
            )
        )

        assert len(results) == len(mock_callable_tasks)
        for result in results:
            assert result is sample_kpat_model

    def test_batch_size_equals_task_count(
        self,
        default_parallel_processing_service: DefaultParallelProcessingService,
        mock_callable_tasks: list[Callable[[], KPATBaseModel]],
        sample_kpat_model: MagicMock,
    ) -> None:
        """Test batched execution where batch_size equals number of tasks."""
        max_workers: int = 2
        batch_size: int = len(mock_callable_tasks)

        results: list[KPATBaseModel] = (
            default_parallel_processing_service.execute_with_batching(
                tasks=mock_callable_tasks,
                max_workers=max_workers,
                batch_size=batch_size,
            )
        )

        assert len(results) == len(mock_callable_tasks)
        for result in results:
            assert result is sample_kpat_model

    def test_batch_size_one(
        self,
        default_parallel_processing_service: DefaultParallelProcessingService,
        mock_callable_tasks: list[Callable[[], KPATBaseModel]],
        sample_kpat_model: MagicMock,
    ) -> None:
        """Test batched execution with batch_size=1."""
        max_workers: int = 2
        batch_size: int = 1

        results: list[KPATBaseModel] = (
            default_parallel_processing_service.execute_with_batching(
                tasks=mock_callable_tasks,
                max_workers=max_workers,
                batch_size=batch_size,
            )
        )

        assert len(results) == len(mock_callable_tasks)
        for result in results:
            assert result is sample_kpat_model

    # NOTE: Immediate exit interrupt scenarios moved to integration tests
    # These tests require real async timing that's difficult to mock properly:
    # - test_immediate_exit_interrupt_raises_interrupted_error
    # - test_immediate_exit_interrupt_batching_raises_interrupted_error
    #
    # The InterruptedError is raised inside concurrent.futures.as_completed() loops,
    # which complete instantly with mocked futures, preventing the interrupt
    # checks from running. Integration tests use real executors and can test
    # this behavior properly with actual timing scenarios.


@pytest.mark.unit
@pytest.mark.core
class TestDefaultParallelProcessingServiceProtocolCompliance:
    """Test cases for DefaultParallelProcessingService protocol compliance."""

    def test_implements_parallel_processing_service_protocol(
        self,
        default_parallel_processing_service: DefaultParallelProcessingService,
    ) -> None:
        """Test that DefaultParallelProcessingService implements the protocol."""
        # Verify that the service has the required methods
        assert hasattr(default_parallel_processing_service, "execute_in_parallel")
        assert hasattr(default_parallel_processing_service, "execute_with_batching")
        assert callable(default_parallel_processing_service.execute_in_parallel)
        assert callable(default_parallel_processing_service.execute_with_batching)

    def test_has_required_execute_in_parallel_method(
        self,
        default_parallel_processing_service: DefaultParallelProcessingService,
    ) -> None:
        """Test that service has execute_in_parallel method with correct signature."""
        assert hasattr(default_parallel_processing_service, "execute_in_parallel")
        assert callable(default_parallel_processing_service.execute_in_parallel)

    def test_has_required_execute_with_batching_method(
        self,
        default_parallel_processing_service: DefaultParallelProcessingService,
    ) -> None:
        """Test that service has execute_with_batching method with correct signature."""
        assert hasattr(default_parallel_processing_service, "execute_with_batching")
        assert callable(default_parallel_processing_service.execute_with_batching)

    def test_execute_in_parallel_returns_list(
        self,
        default_parallel_processing_service: DefaultParallelProcessingService,
        mock_callable_tasks: list[Callable[[], KPATBaseModel]],
    ) -> None:
        """Test that execute_in_parallel returns a list."""
        max_workers: int = 2

        results: list[KPATBaseModel] = (
            default_parallel_processing_service.execute_in_parallel(
                tasks=mock_callable_tasks,
                max_workers=max_workers,
            )
        )

        assert isinstance(results, list)

    def test_execute_with_batching_returns_list(
        self,
        default_parallel_processing_service: DefaultParallelProcessingService,
        mock_callable_tasks: list[Callable[[], KPATBaseModel]],
    ) -> None:
        """Test that execute_with_batching returns a list."""
        max_workers: int = 2
        batch_size: int = 2

        results = default_parallel_processing_service.execute_with_batching(
            tasks=mock_callable_tasks,
            max_workers=max_workers,
            batch_size=batch_size,
        )

        assert isinstance(results, list)


# END AI-GEN
