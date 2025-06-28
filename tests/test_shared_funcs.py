"""Tests for shared_funcs module."""

import contextlib
from unittest.mock import MagicMock, patch

import click
import pytest

from kp_analysis_toolkit.shared_funcs import print_help


class TestPrintHelp:
    """Test shared help functionality."""

    @patch("click.get_current_context")
    @patch("click.echo")
    def test_print_help_functionality(
        self,
        mock_echo: MagicMock,
        mock_get_context: MagicMock,
    ) -> None:
        """Test that print_help displays help and exits."""
        # Mock the context
        mock_context = MagicMock()
        mock_context.get_help.return_value = "Mock help text"
        mock_get_context.return_value = mock_context

        # Mock exit to prevent actual exit
        mock_context.exit = MagicMock()

        # Call print_help
        try:  # noqa: SIM105
            print_help()
        except SystemExit:
            # Expected if ctx.exit() calls sys.exit()
            pass

        # Verify help was retrieved and displayed
        mock_context.get_help.assert_called_once()
        mock_echo.assert_called_once_with("Mock help text")

    @patch("click.get_current_context")
    def test_print_help_calls_exit(self, mock_get_context: MagicMock) -> None:
        """Test that print_help calls context exit."""
        # Mock the context
        mock_context = MagicMock()
        mock_context.get_help.return_value = "Help text"
        mock_get_context.return_value = mock_context

        # Call print_help - it should call exit
        try:  # noqa: SIM105
            print_help()
        except SystemExit:
            # Expected behavior
            pass

        # Verify exit was called
        mock_context.exit.assert_called_once()

    @patch("click.get_current_context")
    @patch("click.echo")
    def test_print_help_integration(
        self,
        mock_echo: MagicMock,
        mock_get_context: MagicMock,
    ) -> None:
        """Test print_help integration with click context."""
        # Create a realistic mock context
        mock_context = MagicMock(spec=click.Context)
        mock_context.get_help.return_value = (
            "Usage: kpat_cli [OPTIONS] COMMAND [ARGS]..."
        )
        mock_get_context.return_value = mock_context

        # Mock exit to prevent actual program termination
        mock_context.exit = MagicMock()

        # Call print_help
        with contextlib.suppress(SystemExit):
            print_help()

        # Verify the complete workflow
        mock_get_context.assert_called_once()
        mock_context.get_help.assert_called_once()
        mock_echo.assert_called_once()
        mock_context.exit.assert_called_once()

    def test_print_help_return_type_annotation(self) -> None:
        """Test that print_help has correct return type annotation."""
        # This test verifies the function signature
        import inspect

        from kp_analysis_toolkit.shared_funcs import print_help

        signature = inspect.signature(print_help)

        # Should have NoReturn annotation
        assert signature.return_annotation.__name__ == "NoReturn"

    @patch("click.get_current_context")
    def test_print_help_exception_handling(self, mock_get_context: MagicMock) -> None:
        """Test print_help handles click context exceptions."""
        # Mock context to raise an exception
        mock_get_context.side_effect = RuntimeError("Click context error")

        # Should handle the exception gracefully or re-raise appropriately
        try:  # noqa: SIM105
            print_help()
        except (RuntimeError, SystemExit):
            # Either behavior is acceptable depending on implementation
            pass


class TestSharedFunctionsIntegration:
    """Test integration aspects of shared functions."""

    def test_module_imports(self) -> None:
        """Test that all required modules are properly imported."""
        # Test that the module can be imported without errors
        from kp_analysis_toolkit import shared_funcs

        # Verify expected functions exist
        assert hasattr(shared_funcs, "print_help")
        assert callable(shared_funcs.print_help)

    def test_function_availability(self) -> None:
        """Test that shared functions are available for import."""
        # This test ensures the functions can be imported by other modules
        try:
            from kp_analysis_toolkit.shared_funcs import print_help

            # Should be callable
            assert callable(print_help)

            # Should have correct type annotations
            import inspect

            signature = inspect.signature(print_help)
            assert len(signature.parameters) == 0

        except ImportError as e:
            pytest.fail(f"Failed to import shared functions: {e}")

    def test_click_integration(self) -> None:
        """Test integration with click framework."""
        # Verify that click is properly imported and used
        import click

        from kp_analysis_toolkit.shared_funcs import print_help

        # The function should use click utilities
        assert hasattr(click, "get_current_context")
        assert hasattr(click, "echo")

        # Function should be designed to work within click context
        with patch("click.get_current_context") as mock_context:
            mock_ctx = MagicMock()
            mock_ctx.get_help.return_value = "test help"
            mock_ctx.exit = MagicMock()
            mock_context.return_value = mock_ctx

            with contextlib.suppress(SystemExit):
                print_help()

            # Should have interacted with click context
            mock_context.assert_called_once()
