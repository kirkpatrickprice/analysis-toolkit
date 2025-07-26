# AI-GEN: GitHub Copilot|2025-01-25|parallel-processing-interrupt-handler-tests|reviewed:no
"""Unit tests for DefaultInterruptHandler implementation."""

from __future__ import annotations

import signal
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, Mock

import pytest

if TYPE_CHECKING:
    from kp_analysis_toolkit.core.services.parallel_processing.interrupt_handler import (
        DefaultInterruptHandler,
    )


# Test constants
EXPECTED_SIGNAL_HANDLER_COUNT: int = 2
STAGE_TERMINATE_ACTIVE: int = 2
STAGE_IMMEDIATE_EXIT: int = 3
MIN_WARNING_CALLS_AFTER_TWO_INTERRUPTS: int = 2


class TestDefaultInterruptHandler:
    """Test the DefaultInterruptHandler implementation."""

    def test_init_stores_rich_output_service(
        self,
        mock_rich_output_service: MagicMock,
    ) -> None:
        """Test that initialization stores the RichOutputService dependency."""
        from kp_analysis_toolkit.core.services.parallel_processing.interrupt_handler import (
            DefaultInterruptHandler,
        )

        handler: DefaultInterruptHandler = DefaultInterruptHandler(
            mock_rich_output_service,
        )

        # Test initial state without accessing private members
        assert not handler.is_interrupted()
        assert handler.get_interrupt_stage() == 0

    def test_setup_configures_signal_handlers(
        self,
        default_interrupt_handler: DefaultInterruptHandler,
        mock_signal_module: MagicMock,
    ) -> None:
        """Test that setup configures SIGINT and SIGTERM handlers."""
        # Call setup
        default_interrupt_handler.setup()

        # Verify signal handlers were configured
        assert mock_signal_module.signal.call_count == EXPECTED_SIGNAL_HANDLER_COUNT
        calls = mock_signal_module.signal.call_args_list

        # Check SIGINT handler
        sigint_call = calls[0]
        assert sigint_call[0][0] == mock_signal_module.SIGINT
        assert callable(sigint_call[0][1])

        # Check SIGTERM handler
        sigterm_call = calls[1]
        assert sigterm_call[0][0] == mock_signal_module.SIGTERM
        assert callable(sigterm_call[0][1])

        # Verify initial state
        assert not default_interrupt_handler.is_interrupted()
        assert default_interrupt_handler.get_interrupt_stage() == 0

    def test_setup_is_idempotent(
        self,
        default_interrupt_handler: DefaultInterruptHandler,
        mock_signal_module: MagicMock,
    ) -> None:
        """Test that setup can be called multiple times without issues."""
        # Call setup twice
        default_interrupt_handler.setup()
        default_interrupt_handler.setup()

        # Should only configure signals once
        assert mock_signal_module.signal.call_count == EXPECTED_SIGNAL_HANDLER_COUNT

    def test_setup_raises_os_error_on_signal_failure(
        self,
        default_interrupt_handler: DefaultInterruptHandler,
        mock_signal_module: MagicMock,
    ) -> None:
        """Test that setup raises OSError when signal configuration fails."""
        # Mock signal.signal to raise OSError
        mock_signal_module.signal.side_effect = OSError("Signal configuration failed")

        # Should raise OSError with descriptive message
        with pytest.raises(OSError, match="Failed to configure signal handlers"):
            default_interrupt_handler.setup()

    def test_cleanup_restores_signal_handlers(
        self,
        default_interrupt_handler: DefaultInterruptHandler,
        mock_signal_module: MagicMock,
    ) -> None:
        """Test that cleanup restores original signal handlers."""
        # Mock original handlers
        original_sigint: MagicMock = Mock()
        original_sigterm: MagicMock = Mock()

        # Setup phase - signal.signal returns original handlers
        mock_signal_module.signal.side_effect = [original_sigint, original_sigterm]

        # Setup and then cleanup
        default_interrupt_handler.setup()

        # Reset mock and prepare for cleanup calls
        mock_signal_module.signal.reset_mock()
        mock_signal_module.signal.side_effect = None  # Clear side effect
        mock_signal_module.signal.return_value = None  # Set default return

        default_interrupt_handler.cleanup()

        # Verify signal handlers were restored
        assert mock_signal_module.signal.call_count == EXPECTED_SIGNAL_HANDLER_COUNT
        cleanup_calls = mock_signal_module.signal.call_args_list

        # Check SIGINT restoration
        sigint_restore = cleanup_calls[0]
        assert sigint_restore[0][0] == mock_signal_module.SIGINT
        assert sigint_restore[0][1] is original_sigint

        # Check SIGTERM restoration
        sigterm_restore = cleanup_calls[1]
        assert sigterm_restore[0][0] == mock_signal_module.SIGTERM
        assert sigterm_restore[0][1] is original_sigterm

    def test_cleanup_is_idempotent(
        self,
        default_interrupt_handler: DefaultInterruptHandler,
        mock_signal_module: MagicMock,
    ) -> None:
        """Test that cleanup can be called multiple times without issues."""
        # Setup first
        default_interrupt_handler.setup()

        # Configure mock for first cleanup call
        mock_signal_module.signal.side_effect = [None, None]

        # Call cleanup first time
        default_interrupt_handler.cleanup()

        # Reset mock to verify second call behavior
        mock_signal_module.signal.reset_mock()

        # Call cleanup second time - should be no-op since _is_setup is False
        default_interrupt_handler.cleanup()

        # Second cleanup should be a no-op (no signal calls)
        assert mock_signal_module.signal.call_count == 0

    def test_cleanup_handles_os_error_gracefully(
        self,
        default_interrupt_handler: DefaultInterruptHandler,
        mock_signal_module: MagicMock,
    ) -> None:
        """Test that cleanup handles OSError during signal restoration gracefully."""
        # Setup first
        default_interrupt_handler.setup()

        # Mock signal restoration to raise OSError
        mock_signal_module.signal.side_effect = OSError("Signal restoration failed")

        # Should not raise exception
        default_interrupt_handler.cleanup()

        # State should still be reset
        assert not default_interrupt_handler.is_interrupted()
        assert default_interrupt_handler.get_interrupt_stage() == 0

    def test_cleanup_without_setup_does_nothing(
        self,
        default_interrupt_handler: DefaultInterruptHandler,
        mock_signal_module: MagicMock,
    ) -> None:
        """Test that cleanup without prior setup does nothing."""
        # Call cleanup without setup
        default_interrupt_handler.cleanup()

        # Should not attempt signal restoration
        mock_signal_module.signal.assert_not_called()

    def test_initial_interrupt_state_is_not_interrupted(
        self,
        default_interrupt_handler: DefaultInterruptHandler,
    ) -> None:
        """Test that initial interrupt state is not interrupted."""
        assert not default_interrupt_handler.is_interrupted()
        assert default_interrupt_handler.get_interrupt_stage() == 0
        assert not default_interrupt_handler.should_cancel_queued_tasks()
        assert not default_interrupt_handler.should_terminate_active_tasks()
        assert not default_interrupt_handler.should_immediate_exit()

    def test_interrupt_stage_progression(
        self,
        default_interrupt_handler: DefaultInterruptHandler,
        mock_signal_module: MagicMock,
        mock_rich_output_service: MagicMock,
    ) -> None:
        """Test interrupt stage progression through multiple interrupts."""
        # Setup handler
        default_interrupt_handler.setup()

        # Get the interrupt handler function
        interrupt_func = mock_signal_module.signal.call_args_list[0][0][1]

        # Stage 1: First interrupt - cancel queued tasks
        interrupt_func(signal.SIGINT, None)

        assert default_interrupt_handler.is_interrupted()
        assert default_interrupt_handler.get_interrupt_stage() == 1
        assert default_interrupt_handler.should_cancel_queued_tasks()
        assert not default_interrupt_handler.should_terminate_active_tasks()
        assert not default_interrupt_handler.should_immediate_exit()

        # Verify stage 1 message
        mock_rich_output_service.warning.assert_called_with(
            "Interrupt received. Cancelling queued tasks and finishing active jobs...",
            force=True,
        )
        mock_rich_output_service.info.assert_called_with(
            "Press CTRL-C again to terminate active jobs immediately.",
            force=True,
        )

        # Stage 2: Second interrupt - terminate active tasks
        interrupt_func(signal.SIGINT, None)

        assert default_interrupt_handler.get_interrupt_stage() == STAGE_TERMINATE_ACTIVE
        assert default_interrupt_handler.should_cancel_queued_tasks()
        assert default_interrupt_handler.should_terminate_active_tasks()
        assert not default_interrupt_handler.should_immediate_exit()

        # Verify stage 2 message
        assert (
            mock_rich_output_service.warning.call_count
            >= MIN_WARNING_CALLS_AFTER_TWO_INTERRUPTS
        )

    def test_stage_three_immediate_exit(
        self,
        default_interrupt_handler: DefaultInterruptHandler,
        mock_signal_module: MagicMock,
        mock_sys_exit: MagicMock,
    ) -> None:
        """Test that stage 3 interrupt causes immediate exit."""
        # Setup handler
        default_interrupt_handler.setup()

        # Get the interrupt handler function
        interrupt_func = mock_signal_module.signal.call_args_list[0][0][1]

        # Progress through stages 1 and 2
        interrupt_func(signal.SIGINT, None)
        interrupt_func(signal.SIGINT, None)

        # Stage 3: Third interrupt - immediate exit
        interrupt_func(signal.SIGINT, None)

        # Should call sys.exit(1)
        mock_sys_exit.assert_called_once_with(1)

    def test_handle_interrupt_stage_displays_appropriate_messages(
        self,
        default_interrupt_handler: DefaultInterruptHandler,
        mock_rich_output_service: MagicMock,
        interrupt_stage_cancel_queued: int,
        interrupt_stage_terminate_active: int,
        interrupt_stage_immediate_exit: int,
    ) -> None:
        """Test that handle_interrupt_stage displays appropriate messages for each stage."""
        # Test stage 1 message
        default_interrupt_handler.handle_interrupt_stage(interrupt_stage_cancel_queued)

        mock_rich_output_service.warning.assert_called_with(
            "Interrupt received. Cancelling queued tasks and finishing active jobs...",
            force=True,
        )
        mock_rich_output_service.info.assert_called_with(
            "Press CTRL-C again to terminate active jobs immediately.",
            force=True,
        )

        # Reset mocks
        mock_rich_output_service.reset_mock()

        # Test stage 2 message
        default_interrupt_handler.handle_interrupt_stage(
            interrupt_stage_terminate_active,
        )

        mock_rich_output_service.warning.assert_called_with(
            "Second interrupt received. Terminating active tasks...",
            force=True,
        )
        mock_rich_output_service.info.assert_called_with(
            "Press CTRL-C again to exit immediately without cleanup.",
            force=True,
        )

        # Reset mocks
        mock_rich_output_service.reset_mock()

        # Test stage 3 message
        default_interrupt_handler.handle_interrupt_stage(interrupt_stage_immediate_exit)

        mock_rich_output_service.error.assert_called_with(
            "Third interrupt received. Exiting immediately without cleanup.",
            force=True,
        )

    def test_context_manager_enter_returns_self(
        self,
        default_interrupt_handler: DefaultInterruptHandler,
    ) -> None:
        """Test that context manager __enter__ returns self."""
        result: DefaultInterruptHandler = default_interrupt_handler.__enter__()

        assert result is default_interrupt_handler

    def test_context_manager_enter_calls_setup(
        self,
        default_interrupt_handler: DefaultInterruptHandler,
        mock_signal_module: MagicMock,
    ) -> None:
        """Test that context manager __enter__ calls setup."""
        default_interrupt_handler.__enter__()

        # Verify setup was called (signal handlers configured)
        assert mock_signal_module.signal.call_count == EXPECTED_SIGNAL_HANDLER_COUNT

    def test_context_manager_exit_calls_cleanup(
        self,
        default_interrupt_handler: DefaultInterruptHandler,
        mock_signal_module: MagicMock,
    ) -> None:
        """Test that context manager __exit__ calls cleanup."""
        # Mock original handlers for setup
        original_sigint: MagicMock = Mock()
        original_sigterm: MagicMock = Mock()
        mock_signal_module.signal.side_effect = [original_sigint, original_sigterm]

        # Setup first
        default_interrupt_handler.__enter__()

        # Configure mock for cleanup call
        mock_signal_module.signal.reset_mock()
        mock_signal_module.signal.side_effect = None
        mock_signal_module.signal.return_value = None

        # Call __exit__
        result: None = default_interrupt_handler.__exit__(None, None, None)

        # Verify cleanup was called (signal handlers restored)
        assert mock_signal_module.signal.call_count == EXPECTED_SIGNAL_HANDLER_COUNT
        assert result is None

    def test_context_manager_exit_does_not_suppress_exceptions(
        self,
        default_interrupt_handler: DefaultInterruptHandler,
    ) -> None:
        """Test that context manager __exit__ does not suppress exceptions."""
        # Setup
        default_interrupt_handler.__enter__()

        # Call __exit__ with exception info
        result: None = default_interrupt_handler.__exit__(
            ValueError,
            ValueError("test error"),
            None,
        )

        # Should not suppress exceptions (returns None/False)
        assert result is None

    def test_context_manager_usage(
        self,
        default_interrupt_handler: DefaultInterruptHandler,
        mock_signal_module: MagicMock,
    ) -> None:
        """Test full context manager usage pattern."""
        # Test context manager usage
        with default_interrupt_handler as handler:
            assert handler is default_interrupt_handler
            # Verify setup was called
            assert mock_signal_module.signal.call_count == EXPECTED_SIGNAL_HANDLER_COUNT

        # Reset and verify cleanup was called
        mock_signal_module.signal.reset_mock()
        # We can't directly verify cleanup was called without accessing privates,
        # but we can verify the behavior works end-to-end


class TestDefaultInterruptHandlerProtocolCompliance:
    """Test that DefaultInterruptHandler implements the InterruptHandler protocol correctly."""

    @pytest.mark.parametrize(
        "method_name",
        [
            "setup",
            "cleanup",
            "__enter__",
            "__exit__",
            "is_interrupted",
            "get_interrupt_stage",
            "should_cancel_queued_tasks",
            "should_terminate_active_tasks",
            "should_immediate_exit",
            "handle_interrupt_stage",
        ],
    )
    def test_has_required_protocol_methods(
        self,
        default_interrupt_handler: DefaultInterruptHandler,
        method_name: str,
    ) -> None:
        """Test that DefaultInterruptHandler has all required protocol methods."""
        assert hasattr(default_interrupt_handler, method_name)
        assert callable(getattr(default_interrupt_handler, method_name))

    def test_is_interrupted_returns_boolean(
        self,
        default_interrupt_handler: DefaultInterruptHandler,
    ) -> None:
        """Test that is_interrupted returns boolean as required by protocol."""
        result: bool = default_interrupt_handler.is_interrupted()

        assert isinstance(result, bool)

    def test_get_interrupt_stage_returns_integer(
        self,
        default_interrupt_handler: DefaultInterruptHandler,
    ) -> None:
        """Test that get_interrupt_stage returns integer as required by protocol."""
        result: int = default_interrupt_handler.get_interrupt_stage()

        assert isinstance(result, int)
        assert result >= 0

    def test_should_methods_return_boolean(
        self,
        default_interrupt_handler: DefaultInterruptHandler,
    ) -> None:
        """Test that should_* methods return boolean as required by protocol."""
        cancel_result: bool = default_interrupt_handler.should_cancel_queued_tasks()
        terminate_result: bool = (
            default_interrupt_handler.should_terminate_active_tasks()
        )
        exit_result: bool = default_interrupt_handler.should_immediate_exit()

        assert isinstance(cancel_result, bool)
        assert isinstance(terminate_result, bool)
        assert isinstance(exit_result, bool)

    def test_supports_context_manager_protocol(
        self,
        default_interrupt_handler: DefaultInterruptHandler,
    ) -> None:
        """Test that DefaultInterruptHandler supports context manager protocol."""
        # Test context manager usage
        with default_interrupt_handler as handler:
            assert handler is default_interrupt_handler

        # Should complete without error


class TestInterruptStageConstants:
    """Test interrupt stage constant values and relationships."""

    def test_stage_constants_have_expected_values(
        self,
        interrupt_stage_no_interrupt: int,
        interrupt_stage_cancel_queued: int,
        interrupt_stage_terminate_active: int,
        interrupt_stage_immediate_exit: int,
    ) -> None:
        """Test that interrupt stage constants have expected values."""
        assert interrupt_stage_no_interrupt == 0
        assert interrupt_stage_cancel_queued == 1
        assert interrupt_stage_terminate_active == STAGE_TERMINATE_ACTIVE
        assert interrupt_stage_immediate_exit == STAGE_IMMEDIATE_EXIT

    def test_stage_progression_order(
        self,
        interrupt_stage_no_interrupt: int,
        interrupt_stage_cancel_queued: int,
        interrupt_stage_terminate_active: int,
        interrupt_stage_immediate_exit: int,
    ) -> None:
        """Test that interrupt stages progress in correct order."""
        assert interrupt_stage_no_interrupt < interrupt_stage_cancel_queued
        assert interrupt_stage_cancel_queued < interrupt_stage_terminate_active
        assert interrupt_stage_terminate_active < interrupt_stage_immediate_exit

    def test_should_methods_respect_stage_hierarchy(
        self,
        default_interrupt_handler: DefaultInterruptHandler,
        mock_signal_module: MagicMock,
    ) -> None:
        """Test that should_* methods respect interrupt stage hierarchy."""
        # Setup handler
        default_interrupt_handler.setup()

        # Get the interrupt handler function
        interrupt_func = mock_signal_module.signal.call_args_list[0][0][1]

        # Test stage 1: cancel queued only
        interrupt_func(signal.SIGINT, None)

        assert default_interrupt_handler.should_cancel_queued_tasks()
        assert not default_interrupt_handler.should_terminate_active_tasks()
        assert not default_interrupt_handler.should_immediate_exit()

        # Test stage 2: cancel queued + terminate active
        interrupt_func(signal.SIGINT, None)

        assert default_interrupt_handler.should_cancel_queued_tasks()
        assert default_interrupt_handler.should_terminate_active_tasks()
        assert not default_interrupt_handler.should_immediate_exit()


# END AI-GEN
