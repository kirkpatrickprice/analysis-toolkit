# AI-GEN: GitHub Copilot|2025-01-24|parallel-processing-interrupt-handler|reviewed:no
"""Concrete implementation of InterruptHandler protocol for multi-stage interrupt handling."""

from __future__ import annotations

import signal
import sys
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from types import TracebackType

    from kp_analysis_toolkit.core.services.rich_output import RichOutputService

from kp_analysis_toolkit.core.services.parallel_processing.protocols import (
    InterruptHandler,
)

# Interrupt stage constants
_STAGE_NO_INTERRUPT: int = 0
_STAGE_CANCEL_QUEUED: int = 1
_STAGE_TERMINATE_ACTIVE: int = 2
_STAGE_IMMEDIATE_EXIT: int = 3


class DefaultInterruptHandler(InterruptHandler):
    """
    Default implementation of InterruptHandler for multi-stage graceful interruption.

    Implements a three-stage interrupt handling strategy:
    1. First CTRL-C: Cancel queued tasks, finish active tasks
    2. Second CTRL-C: Terminate active tasks, return partial results
    3. Third CTRL-C: Immediate termination with no cleanup

    Provides both standalone usage and context manager interface for automatic cleanup.
    """

    def __init__(self, rich_output: RichOutputService) -> None:
        """
        Initialize with Rich Output Service dependency.

        Args:
            rich_output: Rich output service for user communication

        """
        self._rich_output: RichOutputService = rich_output
        self._interrupt_stage: int = _STAGE_NO_INTERRUPT
        self._original_sigint_handler: signal._HANDLER = None
        self._original_sigterm_handler: signal._HANDLER = None
        self._is_setup: bool = False

    def setup(self) -> None:
        """
        Set up multi-stage interrupt handling for parallel operations.

        Configures signal handlers (SIGINT/SIGTERM) and shared state for
        coordinating interruption across process boundaries. Suppresses
        Python's default KeyboardInterrupt traceback handling.

        Raises:
            OSError: If signal handlers cannot be configured

        """
        if self._is_setup:
            return  # Already set up

        try:
            # Store original signal handlers
            self._original_sigint_handler = signal.signal(
                signal.SIGINT, self._handle_interrupt
            )
            self._original_sigterm_handler = signal.signal(
                signal.SIGTERM, self._handle_interrupt
            )

            # Reset interrupt stage
            self._interrupt_stage = _STAGE_NO_INTERRUPT
            self._is_setup = True

        except (OSError, ValueError) as e:
            error_msg: str = f"Failed to configure signal handlers: {e}"
            raise OSError(error_msg) from e

    def cleanup(self) -> None:
        """
        Clean up interrupt handling resources.

        Restores original signal handlers and cleans up shared state.
        Should be called after parallel operations complete, regardless
        of completion status.

        """
        if not self._is_setup:
            return  # Nothing to clean up

        try:
            # Restore original signal handlers
            if self._original_sigint_handler is not None:
                signal.signal(signal.SIGINT, self._original_sigint_handler)
                self._original_sigint_handler = None

            if self._original_sigterm_handler is not None:
                signal.signal(signal.SIGTERM, self._original_sigterm_handler)
                self._original_sigterm_handler = None

            # Reset state
            self._interrupt_stage = _STAGE_NO_INTERRUPT
            self._is_setup = False

        except (OSError, ValueError):
            # Ignore errors during cleanup to avoid masking original exceptions
            pass

    def __enter__(self) -> Self:
        """
        Context manager entry - sets up interrupt handling.

        Returns:
            Self for use in context manager

        Raises:
            OSError: If signal handlers cannot be configured

        """
        self.setup()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool | None:
        """
        Context manager exit - ensures cleanup happens.

        Calls cleanup() regardless of whether an exception occurred.
        Does not suppress exceptions (returns None/False).

        Args:
            exc_type: Exception type if an exception occurred
            exc_val: Exception value if an exception occurred
            exc_tb: Exception traceback if an exception occurred

        Returns:
            None (does not suppress exceptions)

        """
        self.cleanup()
        return None  # Don't suppress exceptions

    def is_interrupted(self) -> bool:
        """
        Check if any stage of interruption has been requested.

        Returns:
            True if interruption has been requested at any stage, False otherwise

        """
        return self._interrupt_stage > _STAGE_NO_INTERRUPT

    def get_interrupt_stage(self) -> int:
        """
        Get the current interrupt stage.

        Returns:
            0: No interrupt requested
            1: First CTRL-C - Cancel queued tasks, finish active, return available results
            2: Second CTRL-C - Terminate active tasks, return partial results
            3: Third CTRL-C - Immediate termination, no cleanup

        """
        return self._interrupt_stage

    def should_cancel_queued_tasks(self) -> bool:
        """
        Check if queued tasks should be cancelled.

        Returns:
            True if interrupt stage >= 1 (cancel queued tasks)

        """
        return self._interrupt_stage >= _STAGE_CANCEL_QUEUED

    def should_terminate_active_tasks(self) -> bool:
        """
        Check if active tasks should be terminated.

        Returns:
            True if interrupt stage >= 2 (terminate active tasks)

        """
        return self._interrupt_stage >= _STAGE_TERMINATE_ACTIVE

    def should_immediate_exit(self) -> bool:
        """
        Check if immediate exit without cleanup is requested.

        Returns:
            True if interrupt stage >= 3 (immediate termination)

        """
        return self._interrupt_stage >= _STAGE_IMMEDIATE_EXIT

    def handle_interrupt_stage(self, stage: int) -> None:
        """
        Handle user communication for interrupt stage transitions.

        Displays appropriate messages to user about interrupt behavior:
        - Stage 1: "Cancelling queued tasks. Press CTRL-C again to terminate active jobs."
        - Stage 2: "Cancelling active tasks. Press CTRL-C again to terminate immediately."
        - Stage 3: Immediate exit without message

        Args:
            stage: The interrupt stage being entered (1, 2, or 3)

        """
        if stage == _STAGE_CANCEL_QUEUED:
            self._rich_output.warning(
                "Interrupt received. Cancelling queued tasks and finishing active jobs...",
                force=True,
            )
            self._rich_output.info(
                "Press CTRL-C again to terminate active jobs immediately.",
                force=True,
            )
        elif stage == _STAGE_TERMINATE_ACTIVE:
            self._rich_output.warning(
                "Second interrupt received. Terminating active tasks...",
                force=True,
            )
            self._rich_output.info(
                "Press CTRL-C again to exit immediately without cleanup.",
                force=True,
            )
        elif stage >= _STAGE_IMMEDIATE_EXIT:
            # Stage 3 exits immediately without message
            self._rich_output.error(
                "Third interrupt received. Exiting immediately without cleanup.",
                force=True,
            )

    def _handle_interrupt(self, _signum: int, _frame: object) -> None:
        """
        Internal signal handler for SIGINT/SIGTERM.

        Advances interrupt stage and communicates with user about behavior.

        Args:
            _signum: Signal number that was received (unused)
            _frame: Current stack frame (unused)

        """
        # Increment interrupt stage
        self._interrupt_stage += 1

        # Handle user communication for this stage
        self.handle_interrupt_stage(self._interrupt_stage)

        # For stage 3, exit immediately
        if self._interrupt_stage >= _STAGE_IMMEDIATE_EXIT:
            self.cleanup()  # Try to clean up, but don't wait
            sys.exit(1)  # Immediate termination


# END AI-GEN
