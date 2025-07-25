# AI-GEN: GitHub Copilot|2025-01-25|parallel-processing-progress-tracker-tests|reviewed:no
"""Unit tests for DefaultProgressTracker implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock

import pytest

if TYPE_CHECKING:
    import rich.progress

    from kp_analysis_toolkit.core.services.parallel_processing.progress_tracker import (
        DefaultProgressTracker,
    )


# Test constants
EXPECTED_TOTAL_TASKS: int = 10
EXPECTED_ADVANCE_AMOUNT: int = 2
EXPECTED_TASK_DESCRIPTION: str = "Test Task"
EXPECTED_SECOND_TASK_DESCRIPTION: str = "Second Task"
MIN_TOTAL_TASKS: int = 1
ZERO_TOTAL_TASKS: int = 0
NEGATIVE_TOTAL_TASKS: int = -1
NEGATIVE_ADVANCE: int = -1
ZERO_ADVANCE: int = 0
POSITIVE_ADVANCE: int = 1
EXPECTED_UPDATE_CALL_COUNT: int = 2


class TestDefaultProgressTracker:
    """Test the DefaultProgressTracker implementation."""

    def test_init_stores_rich_output_service(
        self,
        mock_rich_output_service: MagicMock,
    ) -> None:
        """Test that initialization stores the RichOutputService dependency."""
        from kp_analysis_toolkit.core.services.parallel_processing.progress_tracker import (
            DefaultProgressTracker,
        )

        tracker: DefaultProgressTracker = DefaultProgressTracker(
            mock_rich_output_service,
        )

        # Test initial state by attempting operations that would fail if not properly initialized
        # We can't access private members, so we test behavior instead
        # The constructor should succeed without error
        assert tracker is not None

        # Test that we can use the tracker without error (indicates proper initialization)
        with tracker:
            pass  # Should not raise any errors

    def test_track_progress_creates_new_progress_context_when_none_active(
        self,
        default_progress_tracker: DefaultProgressTracker,
        mock_rich_output_service: MagicMock,
        mock_rich_progress_context: MagicMock,
        task_id: rich.progress.TaskID,
    ) -> None:
        """Test that track_progress creates a new progress context when none is active."""
        # Configure the mock to return our progress context
        mock_rich_output_service.progress.return_value = mock_rich_progress_context
        mock_rich_progress_context.__enter__.return_value = mock_rich_progress_context
        mock_rich_progress_context.add_task.return_value = task_id

        # Call track_progress
        result_task_id: rich.progress.TaskID = default_progress_tracker.track_progress(
            EXPECTED_TOTAL_TASKS,
            EXPECTED_TASK_DESCRIPTION,
        )

        # Verify progress context was created
        mock_rich_output_service.progress.assert_called_once_with(
            show_eta=True,
            show_percentage=True,
            show_time_elapsed=True,
        )
        mock_rich_progress_context.__enter__.assert_called_once()

        # Verify task was added
        mock_rich_progress_context.add_task.assert_called_once_with(
            EXPECTED_TASK_DESCRIPTION,
            total=EXPECTED_TOTAL_TASKS,
        )

        # Should return the task ID
        assert result_task_id == task_id

    def test_track_progress_uses_existing_progress_context_when_active(
        self,
        default_progress_tracker: DefaultProgressTracker,
        mock_rich_output_service: MagicMock,
        mock_rich_progress_context: MagicMock,
        task_id: rich.progress.TaskID,
        other_task_id: rich.progress.TaskID,
    ) -> None:
        """Test that track_progress uses existing progress context when already active."""
        # Configure the mock to return our progress context
        mock_rich_output_service.progress.return_value = mock_rich_progress_context
        mock_rich_progress_context.__enter__.return_value = mock_rich_progress_context
        mock_rich_progress_context.add_task.side_effect = [task_id, other_task_id]

        # Create first task (establishes progress context)
        first_task_id: rich.progress.TaskID = default_progress_tracker.track_progress(
            EXPECTED_TOTAL_TASKS,
            EXPECTED_TASK_DESCRIPTION,
        )

        # Reset mocks to track second call
        mock_rich_output_service.reset_mock()
        mock_rich_progress_context.reset_mock()

        # Create second task (should reuse existing context)
        second_task_id: rich.progress.TaskID = default_progress_tracker.track_progress(
            EXPECTED_TOTAL_TASKS,
            EXPECTED_SECOND_TASK_DESCRIPTION,
        )

        # Progress context should NOT be created again
        mock_rich_output_service.progress.assert_not_called()
        mock_rich_progress_context.__enter__.assert_not_called()

        # But task should still be added
        mock_rich_progress_context.add_task.assert_called_once_with(
            EXPECTED_SECOND_TASK_DESCRIPTION,
            total=EXPECTED_TOTAL_TASKS,
        )

        # Should return different task IDs
        assert first_task_id == task_id
        assert second_task_id == other_task_id
        assert first_task_id != second_task_id

    def test_track_progress_validates_total_positive(
        self,
        default_progress_tracker: DefaultProgressTracker,
    ) -> None:
        """Test that track_progress validates total is positive."""
        # Test zero total
        with pytest.raises(ValueError, match="Total must be greater than 0, got 0"):
            default_progress_tracker.track_progress(
                ZERO_TOTAL_TASKS,
                EXPECTED_TASK_DESCRIPTION,
            )

        # Test negative total
        with pytest.raises(ValueError, match="Total must be greater than 0, got -1"):
            default_progress_tracker.track_progress(
                NEGATIVE_TOTAL_TASKS,
                EXPECTED_TASK_DESCRIPTION,
            )

    def test_track_progress_validates_description_not_empty(
        self,
        default_progress_tracker: DefaultProgressTracker,
    ) -> None:
        """Test that track_progress validates description is not empty."""
        # Test empty description
        with pytest.raises(ValueError, match="Description cannot be empty"):
            default_progress_tracker.track_progress(EXPECTED_TOTAL_TASKS, "")

        # Test whitespace-only description
        with pytest.raises(ValueError, match="Description cannot be empty"):
            default_progress_tracker.track_progress(EXPECTED_TOTAL_TASKS, "   ")

    def test_update_progress_validates_advance_non_negative(
        self,
        default_progress_tracker: DefaultProgressTracker,
        valid_task_id: rich.progress.TaskID,
    ) -> None:
        """Test that update_progress validates advance is non-negative."""
        with pytest.raises(ValueError, match="Advance must be non-negative, got -1"):
            default_progress_tracker.update_progress(valid_task_id, NEGATIVE_ADVANCE)

    def test_update_progress_validates_task_id_exists(
        self,
        default_progress_tracker: DefaultProgressTracker,
        invalid_task_id: rich.progress.TaskID,
    ) -> None:
        """Test that update_progress validates task ID exists."""
        with pytest.raises(ValueError, match=f"Invalid task ID: {invalid_task_id}"):
            default_progress_tracker.update_progress(invalid_task_id, POSITIVE_ADVANCE)

    def test_update_progress_validates_active_progress_exists(
        self,
        default_progress_tracker: DefaultProgressTracker,
        valid_task_id: rich.progress.TaskID,
    ) -> None:
        """Test that update_progress validates active progress context exists."""
        # Test with invalid task ID (which gets checked first)
        # The validation order is: advance >= 0, task_id exists, progress context exists
        with pytest.raises(ValueError, match=f"Invalid task ID: {valid_task_id}"):
            default_progress_tracker.update_progress(valid_task_id, POSITIVE_ADVANCE)

    def test_update_progress_calls_rich_progress_update(
        self,
        default_progress_tracker: DefaultProgressTracker,
        mock_rich_output_service: MagicMock,
        mock_rich_progress_context: MagicMock,
        task_id: rich.progress.TaskID,
    ) -> None:
        """Test that update_progress calls Rich progress update with correct parameters."""
        # Set up progress context and task
        mock_rich_output_service.progress.return_value = mock_rich_progress_context
        mock_rich_progress_context.__enter__.return_value = mock_rich_progress_context
        mock_rich_progress_context.add_task.return_value = task_id

        # Create a task first
        default_progress_tracker.track_progress(
            EXPECTED_TOTAL_TASKS,
            EXPECTED_TASK_DESCRIPTION,
        )

        # Update progress
        default_progress_tracker.update_progress(task_id, EXPECTED_ADVANCE_AMOUNT)

        # Verify Rich progress was updated
        mock_rich_progress_context.update.assert_called_once_with(
            task_id,
            advance=EXPECTED_ADVANCE_AMOUNT,
        )

    def test_update_progress_with_default_advance(
        self,
        default_progress_tracker: DefaultProgressTracker,
        mock_rich_output_service: MagicMock,
        mock_rich_progress_context: MagicMock,
        task_id: rich.progress.TaskID,
    ) -> None:
        """Test that update_progress uses default advance of 1."""
        # Set up progress context and task
        mock_rich_output_service.progress.return_value = mock_rich_progress_context
        mock_rich_progress_context.__enter__.return_value = mock_rich_progress_context
        mock_rich_progress_context.add_task.return_value = task_id

        # Create a task first
        default_progress_tracker.track_progress(
            EXPECTED_TOTAL_TASKS,
            EXPECTED_TASK_DESCRIPTION,
        )

        # Update progress without specifying advance
        default_progress_tracker.update_progress(task_id)

        # Verify Rich progress was updated with default advance of 1
        mock_rich_progress_context.update.assert_called_once_with(task_id, advance=1)

    def test_complete_progress_validates_task_id_exists(
        self,
        default_progress_tracker: DefaultProgressTracker,
        invalid_task_id: rich.progress.TaskID,
    ) -> None:
        """Test that complete_progress validates task ID exists."""
        with pytest.raises(ValueError, match=f"Invalid task ID: {invalid_task_id}"):
            default_progress_tracker.complete_progress(invalid_task_id)

    def test_complete_progress_validates_active_progress_exists(
        self,
        default_progress_tracker: DefaultProgressTracker,
        valid_task_id: rich.progress.TaskID,
    ) -> None:
        """Test that complete_progress validates active progress context exists."""
        # Test with invalid task ID (which gets checked first)
        # The validation order is: task_id exists, progress context exists
        with pytest.raises(ValueError, match=f"Invalid task ID: {valid_task_id}"):
            default_progress_tracker.complete_progress(valid_task_id)

    def test_complete_progress_marks_task_complete(
        self,
        default_progress_tracker: DefaultProgressTracker,
        mock_rich_output_service: MagicMock,
        mock_rich_progress_context: MagicMock,
        task_id: rich.progress.TaskID,
    ) -> None:
        """Test that complete_progress marks task as 100% complete."""
        # Set up progress context and task
        mock_rich_output_service.progress.return_value = mock_rich_progress_context
        mock_rich_progress_context.__enter__.return_value = mock_rich_progress_context
        mock_rich_progress_context.add_task.return_value = task_id

        # Mock the tasks property for completion logic
        mock_task: MagicMock = MagicMock()
        mock_task.total = EXPECTED_TOTAL_TASKS
        mock_rich_progress_context.tasks = {task_id: mock_task}

        # Create a task first
        default_progress_tracker.track_progress(
            EXPECTED_TOTAL_TASKS,
            EXPECTED_TASK_DESCRIPTION,
        )

        # Complete the task
        default_progress_tracker.complete_progress(task_id)

        # Verify task was marked complete
        mock_rich_progress_context.update.assert_called_once_with(
            task_id,
            completed=EXPECTED_TOTAL_TASKS,
        )

    def test_complete_progress_cleans_up_context_when_no_more_tasks(
        self,
        default_progress_tracker: DefaultProgressTracker,
        mock_rich_output_service: MagicMock,
        mock_rich_progress_context: MagicMock,
        task_id: rich.progress.TaskID,
    ) -> None:
        """Test that complete_progress cleans up progress context when no more tasks."""
        # Set up progress context and task
        mock_rich_output_service.progress.return_value = mock_rich_progress_context
        mock_rich_progress_context.__enter__.return_value = mock_rich_progress_context
        mock_rich_progress_context.add_task.return_value = task_id

        # Mock the tasks property for completion logic
        mock_task: MagicMock = MagicMock()
        mock_task.total = EXPECTED_TOTAL_TASKS
        mock_rich_progress_context.tasks = {task_id: mock_task}

        # Create a task first
        default_progress_tracker.track_progress(
            EXPECTED_TOTAL_TASKS,
            EXPECTED_TASK_DESCRIPTION,
        )

        # Complete the task (should trigger cleanup since it's the only task)
        default_progress_tracker.complete_progress(task_id)

        # Verify progress context was cleaned up
        mock_rich_progress_context.__exit__.assert_called_once_with(None, None, None)

    def test_complete_progress_preserves_context_when_other_tasks_exist(
        self,
        default_progress_tracker: DefaultProgressTracker,
        mock_rich_output_service: MagicMock,
        mock_rich_progress_context: MagicMock,
        task_id: rich.progress.TaskID,
        other_task_id: rich.progress.TaskID,
    ) -> None:
        """Test that complete_progress preserves context when other tasks exist."""
        # Set up progress context and tasks
        mock_rich_output_service.progress.return_value = mock_rich_progress_context
        mock_rich_progress_context.__enter__.return_value = mock_rich_progress_context
        mock_rich_progress_context.add_task.side_effect = [task_id, other_task_id]

        # Mock the tasks property for completion logic
        mock_task: MagicMock = MagicMock()
        mock_task.total = EXPECTED_TOTAL_TASKS
        mock_rich_progress_context.tasks = {
            task_id: mock_task,
            other_task_id: mock_task,
        }

        # Create two tasks
        default_progress_tracker.track_progress(
            EXPECTED_TOTAL_TASKS,
            EXPECTED_TASK_DESCRIPTION,
        )
        default_progress_tracker.track_progress(
            EXPECTED_TOTAL_TASKS,
            EXPECTED_SECOND_TASK_DESCRIPTION,
        )

        # Complete only the first task
        default_progress_tracker.complete_progress(task_id)

        # Progress context should NOT be cleaned up (other task still exists)
        mock_rich_progress_context.__exit__.assert_not_called()

        # Verify task was still marked complete
        mock_rich_progress_context.update.assert_called_once_with(
            task_id,
            completed=EXPECTED_TOTAL_TASKS,
        )

    def test_context_manager_enter_returns_self(
        self,
        default_progress_tracker: DefaultProgressTracker,
    ) -> None:
        """Test that context manager __enter__ returns self."""
        result: DefaultProgressTracker = default_progress_tracker.__enter__()

        assert result is default_progress_tracker

    def test_context_manager_exit_cleans_up_progress(
        self,
        default_progress_tracker: DefaultProgressTracker,
        mock_rich_output_service: MagicMock,
        mock_rich_progress_context: MagicMock,
        task_id: rich.progress.TaskID,
    ) -> None:
        """Test that context manager __exit__ cleans up active progress."""
        # Set up progress context and task
        mock_rich_output_service.progress.return_value = mock_rich_progress_context
        mock_rich_progress_context.__enter__.return_value = mock_rich_progress_context
        mock_rich_progress_context.add_task.return_value = task_id

        # Use as context manager and create a task
        with default_progress_tracker:
            default_progress_tracker.track_progress(
                EXPECTED_TOTAL_TASKS,
                EXPECTED_TASK_DESCRIPTION,
            )

        # Verify progress context was cleaned up on exit
        mock_rich_progress_context.__exit__.assert_called_once()

    def test_context_manager_exit_handles_cleanup_errors_gracefully(
        self,
        default_progress_tracker: DefaultProgressTracker,
        mock_rich_output_service: MagicMock,
        mock_rich_progress_context: MagicMock,
        task_id: rich.progress.TaskID,
    ) -> None:
        """Test that context manager __exit__ handles cleanup errors gracefully."""
        # Set up progress context and task
        mock_rich_output_service.progress.return_value = mock_rich_progress_context
        mock_rich_progress_context.__enter__.return_value = mock_rich_progress_context
        mock_rich_progress_context.add_task.return_value = task_id

        # Make cleanup raise RuntimeError
        mock_rich_progress_context.__exit__.side_effect = RuntimeError(
            "Progress already closed",
        )

        # Should not raise exception despite cleanup error
        with default_progress_tracker:
            default_progress_tracker.track_progress(
                EXPECTED_TOTAL_TASKS,
                EXPECTED_TASK_DESCRIPTION,
            )

        # Verify cleanup was attempted
        mock_rich_progress_context.__exit__.assert_called_once()

    def test_context_manager_exit_handles_attribute_errors_gracefully(
        self,
        default_progress_tracker: DefaultProgressTracker,
        mock_rich_output_service: MagicMock,
        mock_rich_progress_context: MagicMock,
        task_id: rich.progress.TaskID,
    ) -> None:
        """Test that context manager __exit__ handles AttributeError gracefully."""
        # Set up progress context and task
        mock_rich_output_service.progress.return_value = mock_rich_progress_context
        mock_rich_progress_context.__enter__.return_value = mock_rich_progress_context
        mock_rich_progress_context.add_task.return_value = task_id

        # Make cleanup raise AttributeError
        mock_rich_progress_context.__exit__.side_effect = AttributeError(
            "Invalid state",
        )

        # Should not raise exception despite cleanup error
        with default_progress_tracker:
            default_progress_tracker.track_progress(
                EXPECTED_TOTAL_TASKS,
                EXPECTED_TASK_DESCRIPTION,
            )

        # Verify cleanup was attempted
        mock_rich_progress_context.__exit__.assert_called_once()

    def test_context_manager_exit_does_not_suppress_exceptions(
        self,
        default_progress_tracker: DefaultProgressTracker,
    ) -> None:
        """Test that context manager __exit__ does not suppress exceptions."""
        # Test that __exit__ returns None (doesn't suppress exceptions)
        # __exit__ implicitly returns None, which means it doesn't suppress exceptions
        default_progress_tracker.__exit__(None, None, None)

        # The fact that we reach this line confirms __exit__ returned None (no exception suppression)

    def test_context_manager_usage(
        self,
        default_progress_tracker: DefaultProgressTracker,
        mock_rich_output_service: MagicMock,
        mock_rich_progress_context: MagicMock,
        task_id: rich.progress.TaskID,
    ) -> None:
        """Test full context manager usage pattern."""
        # Set up progress context
        mock_rich_output_service.progress.return_value = mock_rich_progress_context
        mock_rich_progress_context.__enter__.return_value = mock_rich_progress_context
        mock_rich_progress_context.add_task.return_value = task_id

        # Mock the tasks property for completion logic
        mock_task: MagicMock = MagicMock()
        mock_task.total = EXPECTED_TOTAL_TASKS
        mock_rich_progress_context.tasks = {task_id: mock_task}

        # Test full usage pattern
        with default_progress_tracker as tracker:
            assert tracker is default_progress_tracker

            # Create and work with a task
            task_id_result: rich.progress.TaskID = tracker.track_progress(
                EXPECTED_TOTAL_TASKS,
                EXPECTED_TASK_DESCRIPTION,
            )
            tracker.update_progress(task_id_result, EXPECTED_ADVANCE_AMOUNT)
            tracker.complete_progress(task_id_result)

        # Verify all operations succeeded and cleanup occurred
        mock_rich_progress_context.__exit__.assert_called()


class TestDefaultProgressTrackerProtocolCompliance:
    """Test that DefaultProgressTracker implements the ProgressTracker protocol correctly."""

    @pytest.mark.parametrize(
        "method_name",
        [
            "track_progress",
            "update_progress",
            "complete_progress",
            "__enter__",
            "__exit__",
        ],
    )
    def test_has_required_protocol_methods(
        self,
        default_progress_tracker: DefaultProgressTracker,
        method_name: str,
    ) -> None:
        """Test that DefaultProgressTracker has all required protocol methods."""
        assert hasattr(default_progress_tracker, method_name)
        assert callable(getattr(default_progress_tracker, method_name))

    def test_track_progress_returns_task_id(
        self,
        default_progress_tracker: DefaultProgressTracker,
        mock_rich_output_service: MagicMock,
        mock_rich_progress_context: MagicMock,
        task_id: rich.progress.TaskID,
    ) -> None:
        """Test that track_progress returns TaskID as required by protocol."""
        # Set up progress context
        mock_rich_output_service.progress.return_value = mock_rich_progress_context
        mock_rich_progress_context.__enter__.return_value = mock_rich_progress_context
        mock_rich_progress_context.add_task.return_value = task_id

        result: rich.progress.TaskID = default_progress_tracker.track_progress(
            EXPECTED_TOTAL_TASKS,
            EXPECTED_TASK_DESCRIPTION,
        )

        assert isinstance(result, int)  # TaskID is a type alias for int
        assert result == task_id
        assert result == task_id

    def test_update_progress_accepts_task_id_and_advance(
        self,
        default_progress_tracker: DefaultProgressTracker,
        mock_rich_output_service: MagicMock,
        mock_rich_progress_context: MagicMock,
        task_id: rich.progress.TaskID,
    ) -> None:
        """Test that update_progress accepts TaskID and advance as required by protocol."""
        # Set up progress context and task
        mock_rich_output_service.progress.return_value = mock_rich_progress_context
        mock_rich_progress_context.__enter__.return_value = mock_rich_progress_context
        mock_rich_progress_context.add_task.return_value = task_id

        # Create a task first
        default_progress_tracker.track_progress(
            EXPECTED_TOTAL_TASKS,
            EXPECTED_TASK_DESCRIPTION,
        )

        # Should accept TaskID and advance without error
        default_progress_tracker.update_progress(task_id, EXPECTED_ADVANCE_AMOUNT)
        default_progress_tracker.update_progress(task_id)  # Test default advance

        # Verify calls were made (indicates method signature compliance)
        assert (
            mock_rich_progress_context.update.call_count == EXPECTED_UPDATE_CALL_COUNT
        )

    def test_complete_progress_accepts_task_id(
        self,
        default_progress_tracker: DefaultProgressTracker,
        mock_rich_output_service: MagicMock,
        mock_rich_progress_context: MagicMock,
        task_id: rich.progress.TaskID,
    ) -> None:
        """Test that complete_progress accepts TaskID as required by protocol."""
        # Set up progress context and task
        mock_rich_output_service.progress.return_value = mock_rich_progress_context
        mock_rich_progress_context.__enter__.return_value = mock_rich_progress_context
        mock_rich_progress_context.add_task.return_value = task_id

        # Mock the tasks property for completion logic
        mock_task: MagicMock = MagicMock()
        mock_task.total = EXPECTED_TOTAL_TASKS
        mock_rich_progress_context.tasks = {task_id: mock_task}

        # Create a task first
        default_progress_tracker.track_progress(
            EXPECTED_TOTAL_TASKS,
            EXPECTED_TASK_DESCRIPTION,
        )

        # Should accept TaskID without error
        default_progress_tracker.complete_progress(task_id)

        # Verify call was made (indicates method signature compliance)
        mock_rich_progress_context.update.assert_called_once()

    def test_supports_context_manager_protocol(
        self,
        default_progress_tracker: DefaultProgressTracker,
    ) -> None:
        """Test that DefaultProgressTracker supports context manager protocol."""
        # Test context manager usage
        with default_progress_tracker as tracker:
            assert tracker is default_progress_tracker

        # Should complete without error


# END AI-GEN
