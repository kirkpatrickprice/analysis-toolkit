# AI-GEN: GitHub Copilot|2025-01-24|task-result-impl|reviewed:no
"""Concrete implementation of TaskResult for wrapping parallel task execution results."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from kp_analysis_toolkit.models.base import KPATBaseModel

from kp_analysis_toolkit.core.services.parallel_processing.protocols import TaskResult


class DefaultTaskResult(TaskResult):
    """Default implementation of TaskResult for wrapping task execution outcomes."""

    def __init__(
        self,
        *,
        success: bool,
        result: KPATBaseModel | None = None,
        error: Exception | None = None,
    ) -> None:
        """
        Initialize task result.

        Args:
            success: Whether the task completed successfully
            result: Result data from successful task execution (required if success=True)
            error: Error that occurred during task execution (required if success=False)

        Raises:
            ValueError: If success=True but result is None, or success=False but error is None

        """
        if success and result is None:
            msg: str = "result is required when success=True"
            raise ValueError(msg)

        if not success and error is None:
            msg = "error is required when success=False"
            raise ValueError(msg)

        self._success: bool = success
        self._result: KPATBaseModel | None = result
        self._error: Exception | None = error

    @property
    def success(self) -> bool:
        """Whether the task completed successfully."""
        return self._success

    @property
    def error(self) -> Exception | None:
        """Error that occurred during task execution, if any."""
        return self._error

    @property
    def result(self) -> KPATBaseModel:
        """
        Result data from successful task execution as a validated Pydantic model.

        Returns:
            The task result data

        Raises:
            ValueError: If accessed when success=False

        """
        if not self._success:
            msg: str = (
                "Cannot access result when task failed. Check success property first."
            )
            raise ValueError(msg)

        # We know result is not None because we validated it in __init__
        return self._result  # type: ignore[return-value]

    @classmethod
    def create_success(cls, result: KPATBaseModel) -> DefaultTaskResult:
        """
        Create a successful task result.

        Args:
            result: The successful task result data

        Returns:
            TaskResult instance representing successful execution

        """
        return cls(success=True, result=result)

    @classmethod
    def create_failure(cls, error: Exception) -> DefaultTaskResult:
        """
        Create a failed task result.

        Args:
            error: The error that occurred during task execution

        Returns:
            TaskResult instance representing failed execution

        """
        return cls(success=False, error=error)

    def __repr__(self) -> str:
        """Return string representation of the task result."""
        if self._success:
            result_type: str = type(self._result).__name__ if self._result else "None"
            return f"DefaultTaskResult(success=True, result_type={result_type})"

        error_type: str = type(self._error).__name__ if self._error else "None"
        return f"DefaultTaskResult(success=False, error_type={error_type})"


# END AI-GEN
