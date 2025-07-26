# AI-GEN: GitHub Copilot|2025-01-27|task-result-unit-tests|reviewed:no
"""Unit tests for DefaultTaskResult implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from unittest.mock import MagicMock

    from kp_analysis_toolkit.models.base import KPATBaseModel

from kp_analysis_toolkit.core.services.parallel_processing.task_result import (
    DefaultTaskResult,
)


@pytest.mark.unit
@pytest.mark.core
class TestDefaultTaskResult:
    """Test cases for DefaultTaskResult implementation."""

    def test_init_success_with_result(self, sample_kpat_model: MagicMock) -> None:
        """Test successful initialization with result."""
        task_result: DefaultTaskResult = DefaultTaskResult(
            success=True,
            result=sample_kpat_model,
        )

        assert task_result.success is True
        assert task_result.result is sample_kpat_model
        assert task_result.error is None

    def test_init_failure_with_error(self, sample_error: ValueError) -> None:
        """Test failure initialization with error."""
        task_result: DefaultTaskResult = DefaultTaskResult(
            success=False,
            error=sample_error,
        )

        assert task_result.success is False
        assert task_result.error is sample_error

    def test_init_success_without_result_raises_value_error(self) -> None:
        """Test that successful initialization without result raises ValueError."""
        with pytest.raises(ValueError, match="result is required when success=True"):
            DefaultTaskResult(success=True, result=None)

    def test_init_failure_without_error_raises_value_error(self) -> None:
        """Test that failure initialization without error raises ValueError."""
        with pytest.raises(ValueError, match="error is required when success=False"):
            DefaultTaskResult(success=False, error=None)

    def test_init_with_both_result_and_error_success_true(
        self,
        sample_kpat_model: MagicMock,
        sample_error: ValueError,
    ) -> None:
        """Test initialization with both result and error when success=True."""
        task_result: DefaultTaskResult = DefaultTaskResult(
            success=True,
            result=sample_kpat_model,
            error=sample_error,
        )

        assert task_result.success is True
        assert task_result.result is sample_kpat_model
        assert task_result.error is sample_error

    def test_init_with_both_result_and_error_success_false(
        self,
        sample_kpat_model: MagicMock,
        sample_error: ValueError,
    ) -> None:
        """Test initialization with both result and error when success=False."""
        task_result: DefaultTaskResult = DefaultTaskResult(
            success=False,
            result=sample_kpat_model,
            error=sample_error,
        )

        assert task_result.success is False
        assert task_result.error is sample_error

    def test_result_property_access_success(
        self,
        real_task_result_success: DefaultTaskResult,
        sample_kpat_model: MagicMock,
    ) -> None:
        """Test accessing result property on successful task result."""
        result: KPATBaseModel = real_task_result_success.result
        assert result is sample_kpat_model

    def test_result_property_access_failure_raises_value_error(
        self,
        real_task_result_failure: DefaultTaskResult,
    ) -> None:
        """Test accessing result property on failed task result raises ValueError."""
        with pytest.raises(
            ValueError,
            match="Cannot access result when task failed. Check success property first.",
        ):
            _ = real_task_result_failure.result

    def test_error_property_success(
        self,
        real_task_result_success: DefaultTaskResult,
    ) -> None:
        """Test error property on successful task result returns None."""
        assert real_task_result_success.error is None

    def test_error_property_failure(
        self,
        real_task_result_failure: DefaultTaskResult,
        sample_error: ValueError,
    ) -> None:
        """Test error property on failed task result returns the error."""
        assert real_task_result_failure.error is sample_error

    def test_success_property_true(
        self,
        real_task_result_success: DefaultTaskResult,
    ) -> None:
        """Test success property returns True for successful result."""
        assert real_task_result_success.success is True

    def test_success_property_false(
        self,
        real_task_result_failure: DefaultTaskResult,
    ) -> None:
        """Test success property returns False for failed result."""
        assert real_task_result_failure.success is False


@pytest.mark.unit
@pytest.mark.core
class TestDefaultTaskResultClassMethods:
    """Test cases for DefaultTaskResult class methods."""

    def test_create_success(self, sample_kpat_model: MagicMock) -> None:
        """Test create_success class method."""
        task_result: DefaultTaskResult = DefaultTaskResult.create_success(
            sample_kpat_model,
        )

        assert task_result.success is True
        assert task_result.result is sample_kpat_model
        assert task_result.error is None

    def test_create_failure(self, sample_error: ValueError) -> None:
        """Test create_failure class method."""
        task_result: DefaultTaskResult = DefaultTaskResult.create_failure(sample_error)

        assert task_result.success is False
        assert task_result.error is sample_error

    def test_create_failure_result_property_access_raises_error(
        self,
        sample_error: ValueError,
    ) -> None:
        """Test that accessing result on failure created via class method raises error."""
        task_result: DefaultTaskResult = DefaultTaskResult.create_failure(sample_error)

        with pytest.raises(
            ValueError,
            match="Cannot access result when task failed. Check success property first.",
        ):
            _ = task_result.result


@pytest.mark.unit
@pytest.mark.core
class TestDefaultTaskResultStringRepresentation:
    """Test cases for DefaultTaskResult string representation."""

    def test_repr_success_with_result(self, sample_kpat_model: MagicMock) -> None:
        """Test __repr__ for successful task result with result."""
        task_result: DefaultTaskResult = DefaultTaskResult.create_success(
            sample_kpat_model,
        )

        repr_str: str = repr(task_result)
        assert "DefaultTaskResult(success=True, result_type=MagicMock)" in repr_str

    def test_repr_failure_with_error(self, sample_error: ValueError) -> None:
        """Test __repr__ for failed task result with error."""
        task_result: DefaultTaskResult = DefaultTaskResult.create_failure(sample_error)

        repr_str: str = repr(task_result)
        assert "DefaultTaskResult(success=False, error_type=ValueError)" in repr_str

    def test_repr_failure_with_runtime_error(
        self,
        sample_runtime_error: RuntimeError,
    ) -> None:
        """Test __repr__ for failed task result with RuntimeError."""
        task_result: DefaultTaskResult = DefaultTaskResult.create_failure(
            sample_runtime_error,
        )

        repr_str: str = repr(task_result)
        assert "DefaultTaskResult(success=False, error_type=RuntimeError)" in repr_str


@pytest.mark.unit
@pytest.mark.core
class TestDefaultTaskResultEdgeCases:
    """Test cases for DefaultTaskResult edge cases and boundary conditions."""

    def test_multiple_error_types(self) -> None:
        """Test DefaultTaskResult with different error types."""
        errors: list[Exception] = [
            ValueError("Value error"),
            RuntimeError("Runtime error"),
            OSError("OS error"),
            KeyError("Key error"),
            AttributeError("Attribute error"),
        ]

        for error in errors:
            task_result: DefaultTaskResult = DefaultTaskResult.create_failure(error)
            assert task_result.success is False
            assert task_result.error is error
            assert type(task_result.error).__name__ in repr(task_result)

    def test_task_result_immutability(
        self,
        sample_kpat_model: MagicMock,
        sample_error: ValueError,
    ) -> None:
        """Test that TaskResult properties maintain their values after creation."""
        success_result: DefaultTaskResult = DefaultTaskResult.create_success(
            sample_kpat_model,
        )
        failure_result: DefaultTaskResult = DefaultTaskResult.create_failure(
            sample_error,
        )

        # Verify success result properties don't change
        assert success_result.success is True
        assert success_result.result is sample_kpat_model
        assert success_result.error is None

        # Verify failure result properties don't change
        assert failure_result.success is False
        assert failure_result.error is sample_error

        # Try accessing result multiple times on success
        result_1: KPATBaseModel = success_result.result
        result_2: KPATBaseModel = success_result.result
        assert result_1 is result_2 is sample_kpat_model

    def test_result_property_with_different_model_types(self) -> None:
        """Test result property works with different KPATBaseModel types."""
        from unittest.mock import MagicMock

        from kp_analysis_toolkit.models.base import KPATBaseModel

        # Create different mock model types
        models: list[MagicMock] = []
        for i in range(3):
            mock_model: MagicMock = MagicMock(spec=KPATBaseModel)
            mock_model.model_dump.return_value = {"id": i, "data": f"test_{i}"}
            models.append(mock_model)

        # Test each model type
        for model in models:
            task_result: DefaultTaskResult = DefaultTaskResult.create_success(model)
            assert task_result.result is model
            assert task_result.success is True

    def test_error_message_preservation(self) -> None:
        """Test that error messages are preserved in TaskResult."""
        error_messages: list[str] = [
            "Simple error message",
            "Error with special characters: !@#$%^&*()",
            "Multi-line\nerror\nmessage",
            "",  # Empty message
            "Very long error message " * 100,  # Long message
        ]

        for message in error_messages:
            error: ValueError = ValueError(message)
            task_result: DefaultTaskResult = DefaultTaskResult.create_failure(error)

            assert task_result.error is error
            assert str(task_result.error) == message


# END AI-GEN
