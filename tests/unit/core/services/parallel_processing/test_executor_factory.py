# AI-GEN: GitHub Copilot|2025-01-25|parallel-processing-executor-factory-tests|reviewed:no
"""Unit tests for parallel processing executor factory implementations."""

from __future__ import annotations

import concurrent.futures
from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest

from kp_analysis_toolkit.core.services.parallel_processing.executor_factory import (
    ProcessPoolExecutorFactory,
    ThreadPoolExecutorFactory,
)

if TYPE_CHECKING:
    from typing import Any
    from unittest.mock import MagicMock

    # Type alias for factory classes used in parametrized tests
    FactoryClass = type[ProcessPoolExecutorFactory | ThreadPoolExecutorFactory]

# =============================================================================
# PROCESSPOOL EXECUTOR FACTORY TESTS
# =============================================================================


class TestProcessPoolExecutorFactory:
    """Unit tests for ProcessPoolExecutorFactory."""

    def test_create_executor_returns_process_pool_executor(self) -> None:
        """Test that create_executor returns a ProcessPoolExecutor instance."""
        factory: ProcessPoolExecutorFactory = ProcessPoolExecutorFactory()
        max_workers: int = 2

        executor: concurrent.futures.ProcessPoolExecutor = factory.create_executor(
            max_workers,
        )

        assert isinstance(executor, concurrent.futures.ProcessPoolExecutor)

    def test_create_executor_with_valid_max_workers(self) -> None:
        """Test create_executor with various valid max_workers values."""
        factory: ProcessPoolExecutorFactory = ProcessPoolExecutorFactory()
        valid_values: list[int] = [1, 2, 4, 8]

        for max_workers in valid_values:
            executor: concurrent.futures.ProcessPoolExecutor = factory.create_executor(
                max_workers,
            )
            assert isinstance(executor, concurrent.futures.ProcessPoolExecutor)
            # Clean up the executor
            executor.shutdown(wait=False)

    def test_create_executor_raises_value_error_when_max_workers_is_zero(self) -> None:
        """Test that create_executor raises ValueError when max_workers is 0."""
        factory: ProcessPoolExecutorFactory = ProcessPoolExecutorFactory()

        with pytest.raises(ValueError, match="max_workers must be greater than 0"):
            factory.create_executor(0)

    def test_create_executor_raises_value_error_when_max_workers_is_negative(
        self,
    ) -> None:
        """Test that create_executor raises ValueError when max_workers is negative."""
        factory: ProcessPoolExecutorFactory = ProcessPoolExecutorFactory()

        with pytest.raises(ValueError, match="max_workers must be greater than 0"):
            factory.create_executor(-1)

    def test_create_executor_includes_max_workers_in_error_message(self) -> None:
        """Test that error message includes the invalid max_workers value."""
        factory: ProcessPoolExecutorFactory = ProcessPoolExecutorFactory()
        invalid_value: int = -5

        with pytest.raises(
            ValueError,
            match=f"max_workers must be greater than 0, got {invalid_value}",
        ):
            factory.create_executor(invalid_value)

    @patch("concurrent.futures.ProcessPoolExecutor")
    def test_create_executor_passes_max_workers_to_constructor(
        self,
        mock_executor_class: MagicMock,
    ) -> None:
        """Test that create_executor passes max_workers to ProcessPoolExecutor."""
        factory: ProcessPoolExecutorFactory = ProcessPoolExecutorFactory()
        max_workers: int = 4

        factory.create_executor(max_workers)

        mock_executor_class.assert_called_once_with(
            max_workers=max_workers,
            mp_context=None,
        )

    @patch("concurrent.futures.ProcessPoolExecutor")
    def test_create_executor_handles_os_error_from_constructor(
        self,
        mock_executor_class: MagicMock,
    ) -> None:
        """Test that create_executor handles OSError from ProcessPoolExecutor constructor."""
        factory: ProcessPoolExecutorFactory = ProcessPoolExecutorFactory()
        original_error: OSError = OSError("System resource error")
        mock_executor_class.side_effect = original_error

        with pytest.raises(OSError, match="Failed to create ProcessPoolExecutor"):
            factory.create_executor(2)

    @patch("concurrent.futures.ProcessPoolExecutor")
    def test_create_executor_chains_os_error_from_constructor(
        self,
        mock_executor_class: MagicMock,
    ) -> None:
        """Test that create_executor properly chains OSError from constructor."""
        factory: ProcessPoolExecutorFactory = ProcessPoolExecutorFactory()
        original_error: OSError = OSError("Resource exhausted")
        mock_executor_class.side_effect = original_error

        with pytest.raises(
            OSError,
            match="Failed to create ProcessPoolExecutor",
        ) as exc_info:
            factory.create_executor(4)

        assert exc_info.value.__cause__ is original_error

    def test_create_executor_configures_default_mp_context(self) -> None:
        """Test that create_executor uses default multiprocessing context."""
        factory: ProcessPoolExecutorFactory = ProcessPoolExecutorFactory()

        with patch("concurrent.futures.ProcessPoolExecutor") as mock_constructor:
            factory.create_executor(2)

            # Verify that mp_context=None is passed (uses default context)
            call_kwargs: dict[str, Any] = mock_constructor.call_args.kwargs
            assert call_kwargs["mp_context"] is None


# =============================================================================
# THREADPOOL EXECUTOR FACTORY TESTS
# =============================================================================


class TestThreadPoolExecutorFactory:
    """Unit tests for ThreadPoolExecutorFactory."""

    def test_create_executor_returns_thread_pool_executor(self) -> None:
        """Test that create_executor returns a ThreadPoolExecutor instance."""
        factory: ThreadPoolExecutorFactory = ThreadPoolExecutorFactory()
        max_workers: int = 2

        executor: concurrent.futures.ThreadPoolExecutor = factory.create_executor(
            max_workers,
        )

        assert isinstance(executor, concurrent.futures.ThreadPoolExecutor)

    def test_create_executor_with_valid_max_workers(self) -> None:
        """Test create_executor with various valid max_workers values."""
        factory: ThreadPoolExecutorFactory = ThreadPoolExecutorFactory()
        valid_values: list[int] = [1, 2, 4, 8]

        for max_workers in valid_values:
            executor: concurrent.futures.ThreadPoolExecutor = factory.create_executor(
                max_workers,
            )
            assert isinstance(executor, concurrent.futures.ThreadPoolExecutor)
            # Clean up the executor
            executor.shutdown(wait=False)

    def test_create_executor_raises_value_error_when_max_workers_is_zero(self) -> None:
        """Test that create_executor raises ValueError when max_workers is 0."""
        factory: ThreadPoolExecutorFactory = ThreadPoolExecutorFactory()

        with pytest.raises(ValueError, match="max_workers must be greater than 0"):
            factory.create_executor(0)

    def test_create_executor_raises_value_error_when_max_workers_is_negative(
        self,
    ) -> None:
        """Test that create_executor raises ValueError when max_workers is negative."""
        factory: ThreadPoolExecutorFactory = ThreadPoolExecutorFactory()

        with pytest.raises(ValueError, match="max_workers must be greater than 0"):
            factory.create_executor(-1)

    def test_create_executor_includes_max_workers_in_error_message(self) -> None:
        """Test that error message includes the invalid max_workers value."""
        factory: ThreadPoolExecutorFactory = ThreadPoolExecutorFactory()
        invalid_value: int = -3

        with pytest.raises(
            ValueError,
            match=f"max_workers must be greater than 0, got {invalid_value}",
        ):
            factory.create_executor(invalid_value)

    @patch("concurrent.futures.ThreadPoolExecutor")
    def test_create_executor_passes_max_workers_to_constructor(
        self,
        mock_executor_class: MagicMock,
    ) -> None:
        """Test that create_executor passes max_workers to ThreadPoolExecutor."""
        factory: ThreadPoolExecutorFactory = ThreadPoolExecutorFactory()
        max_workers: int = 6

        factory.create_executor(max_workers)

        mock_executor_class.assert_called_once_with(
            max_workers=max_workers,
            thread_name_prefix="kpat-worker",
        )

    @patch("concurrent.futures.ThreadPoolExecutor")
    def test_create_executor_handles_os_error_from_constructor(
        self,
        mock_executor_class: MagicMock,
    ) -> None:
        """Test that create_executor handles OSError from ThreadPoolExecutor constructor."""
        factory: ThreadPoolExecutorFactory = ThreadPoolExecutorFactory()
        original_error: OSError = OSError("Thread creation failed")
        mock_executor_class.side_effect = original_error

        with pytest.raises(OSError, match="Failed to create ThreadPoolExecutor"):
            factory.create_executor(2)

    @patch("concurrent.futures.ThreadPoolExecutor")
    def test_create_executor_chains_os_error_from_constructor(
        self,
        mock_executor_class: MagicMock,
    ) -> None:
        """Test that create_executor properly chains OSError from constructor."""
        factory: ThreadPoolExecutorFactory = ThreadPoolExecutorFactory()
        original_error: OSError = OSError("Thread limit reached")
        mock_executor_class.side_effect = original_error

        with pytest.raises(
            OSError,
            match="Failed to create ThreadPoolExecutor",
        ) as exc_info:
            factory.create_executor(3)

        assert exc_info.value.__cause__ is original_error

    def test_create_executor_configures_thread_name_prefix(self) -> None:
        """Test that create_executor uses correct thread name prefix."""
        factory: ThreadPoolExecutorFactory = ThreadPoolExecutorFactory()

        with patch("concurrent.futures.ThreadPoolExecutor") as mock_constructor:
            factory.create_executor(2)

            # Verify that thread_name_prefix is set correctly
            call_kwargs: dict[str, Any] = mock_constructor.call_args.kwargs
            assert call_kwargs["thread_name_prefix"] == "kpat-worker"


# =============================================================================
# PROTOCOL COMPLIANCE TESTS
# =============================================================================


class TestExecutorFactoryProtocolCompliance:
    """Test that both factory implementations comply with ExecutorFactory protocol."""

    @pytest.mark.parametrize(
        "factory_class",
        [ProcessPoolExecutorFactory, ThreadPoolExecutorFactory],
    )
    def test_factory_has_create_executor_method(
        self,
        factory_class: FactoryClass,
    ) -> None:
        """Test that factory implementations have create_executor method."""
        factory = factory_class()

        assert hasattr(factory, "create_executor")
        assert callable(factory.create_executor)

    @pytest.mark.parametrize(
        "factory_class",
        [ProcessPoolExecutorFactory, ThreadPoolExecutorFactory],
    )
    def test_create_executor_returns_executor_interface(
        self,
        factory_class: FactoryClass,
    ) -> None:
        """Test that create_executor returns an object implementing Executor interface."""
        factory = factory_class()

        executor: concurrent.futures.Executor = factory.create_executor(2)

        # Check that it has the basic Executor interface methods
        assert hasattr(executor, "submit")
        assert hasattr(executor, "shutdown")
        assert callable(executor.submit)
        assert callable(executor.shutdown)

        # Clean up
        executor.shutdown(wait=False)

    @pytest.mark.parametrize(
        "factory_class",
        [ProcessPoolExecutorFactory, ThreadPoolExecutorFactory],
    )
    def test_create_executor_supports_context_manager(
        self,
        factory_class: FactoryClass,
    ) -> None:
        """Test that created executors can be used as context managers."""
        factory = factory_class()

        executor: concurrent.futures.Executor = factory.create_executor(2)

        # Should support context manager protocol
        assert hasattr(executor, "__enter__")
        assert hasattr(executor, "__exit__")

        # Should work in with statement
        with executor:
            pass  # Context manager should handle cleanup


# END AI-GEN
