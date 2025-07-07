"""Tests for the RichOutput service implementation."""

from unittest.mock import MagicMock, patch

from kp_analysis_toolkit.core.services.rich_output import (
    RichOutputService,
)
from kp_analysis_toolkit.models.enums import MessageType
from kp_analysis_toolkit.models.rich_config import RichOutputConfig


class TestRichOutputService:
    """Test the RichOutputService implementation."""

    def test_rich_output_service_creation(self) -> None:
        """Test RichOutputService can be created with configuration."""
        config = RichOutputConfig(
            verbose=False,
            quiet=False,
            console_width=120,
            force_terminal=True,
            stderr_enabled=True,
        )

        service = RichOutputService(config)
        assert isinstance(service, RichOutputService)
        assert service.verbose is False
        assert service.quiet is False

    def test_rich_output_service_implements_protocol(self) -> None:
        """Test that RichOutputService implements RichOutputProtocol."""
        config = RichOutputConfig()
        service = RichOutputService(config)

        # Check that all protocol methods are available
        assert hasattr(service, "info")
        assert hasattr(service, "success")
        assert hasattr(service, "error")
        assert hasattr(service, "warning")
        assert hasattr(service, "debug")
        assert hasattr(service, "header")
        assert hasattr(service, "subheader")
        assert hasattr(service, "message")

    @patch("kp_analysis_toolkit.core.services.rich_output.Console")
    def test_console_initialization(self, mock_console_class: MagicMock) -> None:
        """Test that Console objects are initialized correctly."""
        mock_console = MagicMock()
        mock_error_console = MagicMock()
        mock_console_class.side_effect = [mock_console, mock_error_console]

        config = RichOutputConfig(
            console_width=100,
            force_terminal=True,
            stderr_enabled=True,
        )

        service = RichOutputService(config)

        # Verify Console was called twice with correct parameters
        expected_calls = [
            # Main console
            {
                "stderr": False,
                "force_terminal": True,
                "width": 100,
            },
            # Error console
            {
                "stderr": True,
                "force_terminal": True,
                "width": 100,
            },
        ]

        assert mock_console_class.call_count == 2
        for i, call in enumerate(mock_console_class.call_args_list):
            args, kwargs = call
            for key, expected_value in expected_calls[i].items():
                assert kwargs[key] == expected_value

    def test_message_styling_configuration(self) -> None:
        """Test that message styling is configured correctly."""
        config = RichOutputConfig()
        service = RichOutputService(config)

        # Check that styling dictionary is set up
        assert hasattr(service, "_styles")
        assert MessageType.INFO in service._styles
        assert MessageType.SUCCESS in service._styles
        assert MessageType.WARNING in service._styles
        assert MessageType.ERROR in service._styles
        assert MessageType.DEBUG in service._styles
        assert MessageType.HEADER in service._styles
        assert MessageType.SUBHEADER in service._styles

    @patch("kp_analysis_toolkit.core.services.rich_output.Console")
    def test_quiet_mode_suppresses_output(self, mock_console_class: MagicMock) -> None:
        """Test that quiet mode suppresses non-essential output."""
        mock_console = MagicMock()
        mock_error_console = MagicMock()
        mock_console_class.side_effect = [mock_console, mock_error_console]

        config = RichOutputConfig(quiet=True)
        service = RichOutputService(config)

        # Test that info message is suppressed in quiet mode
        service.info("Test message")
        mock_console.print.assert_not_called()

        # Test that error message is not suppressed (force=True by default)
        service.error("Error message")
        mock_error_console.print.assert_called()

    @patch("kp_analysis_toolkit.core.services.rich_output.Console")
    def test_force_parameter_overrides_quiet(
        self, mock_console_class: MagicMock
    ) -> None:
        """Test that force parameter overrides quiet mode."""
        mock_console = MagicMock()
        mock_error_console = MagicMock()
        mock_console_class.side_effect = [mock_console, mock_error_console]

        config = RichOutputConfig(quiet=True)
        service = RichOutputService(config)

        # Test that force=True shows message even in quiet mode
        service.info("Forced message", force=True)
        mock_console.print.assert_called()

    @patch("kp_analysis_toolkit.core.services.rich_output.Console")
    def test_verbose_mode_shows_debug(self, mock_console_class: MagicMock) -> None:
        """Test that verbose mode shows debug messages."""
        mock_console = MagicMock()
        mock_error_console = MagicMock()
        mock_console_class.side_effect = [mock_console, mock_error_console]

        # Test non-verbose mode
        config = RichOutputConfig(verbose=False)
        service = RichOutputService(config)
        service.debug("Debug message")
        mock_console.print.assert_not_called()

        # Reset mocks
        mock_console.reset_mock()
        mock_error_console.reset_mock()
        mock_console_class.side_effect = [mock_console, mock_error_console]

        # Test verbose mode
        config = RichOutputConfig(verbose=True)
        service = RichOutputService(config)
        service.debug("Debug message")
        mock_console.print.assert_called()

    def test_message_types_have_correct_styling(self) -> None:
        """Test that different message types have appropriate styling."""
        config = RichOutputConfig()
        service = RichOutputService(config)

        # Verify each message type has style and prefix
        expected_styles = {
            MessageType.INFO: {"style": "blue", "prefix": "🔵 "},
            MessageType.SUCCESS: {"style": "bold green", "prefix": "✅ "},
            MessageType.WARNING: {"style": "bold yellow", "prefix": "⚠️ "},
            MessageType.ERROR: {"style": "bold red", "prefix": "❌ "},
            MessageType.DEBUG: {"style": "dim white", "prefix": "🔍 "},
            MessageType.HEADER: {"style": "bold blue", "prefix": "📋 "},
            MessageType.SUBHEADER: {"style": "bold white", "prefix": "▸ "},
        }

        for message_type, expected in expected_styles.items():
            actual = service._styles[message_type]
            assert actual["style"] == expected["style"]
            assert actual["prefix"] == expected["prefix"]


class TestRichOutputBackwardCompatibility:
    """Test backward compatibility with existing RichOutput usage."""

    def test_can_import_rich_output_from_utils(self) -> None:
        """Test that RichOutput can still be imported from utils."""
        from kp_analysis_toolkit.utils.rich_output import RichOutput

        # Should be able to import without error
        assert RichOutput is not None

    def test_can_import_get_rich_output_function(self) -> None:
        """Test that get_rich_output function is available."""
        from kp_analysis_toolkit.utils.rich_output import get_rich_output

        # Should be able to import and call
        rich_output = get_rich_output()
        assert rich_output is not None

    def test_get_rich_output_returns_rich_output_service(self) -> None:
        """Test that get_rich_output returns RichOutputService instance."""
        from kp_analysis_toolkit.utils.rich_output import get_rich_output

        rich_output = get_rich_output()
        assert isinstance(rich_output, RichOutputService)

    def test_get_rich_output_with_parameters(self) -> None:
        """Test get_rich_output with verbose and quiet parameters."""
        from kp_analysis_toolkit.utils.rich_output import get_rich_output

        # Test verbose mode
        rich_output_verbose = get_rich_output(verbose=True, quiet=False)
        assert rich_output_verbose.verbose is True
        assert rich_output_verbose.quiet is False

        # Test quiet mode
        rich_output_quiet = get_rich_output(verbose=False, quiet=True)
        assert rich_output_quiet.verbose is False
        assert rich_output_quiet.quiet is True

    def test_convenience_functions_available(self) -> None:
        """Test that convenience functions are available for backward compatibility."""
        from kp_analysis_toolkit.utils.rich_output import (
            debug,
            error,
            header,
            info,
            subheader,
            success,
            warning,
        )

        # All functions should be callable
        assert callable(info)
        assert callable(success)
        assert callable(warning)
        assert callable(error)
        assert callable(debug)
        assert callable(header)
        assert callable(subheader)

    @patch("kp_analysis_toolkit.utils.rich_output.get_rich_output")
    def test_convenience_functions_use_get_rich_output(
        self, mock_get_rich_output: MagicMock
    ) -> None:
        """Test that convenience functions delegate to get_rich_output."""
        from kp_analysis_toolkit.utils.rich_output import info

        mock_rich_output = MagicMock()
        mock_get_rich_output.return_value = mock_rich_output

        info("Test message")

        mock_get_rich_output.assert_called_once()
        mock_rich_output.info.assert_called_once_with("Test message", force=False)


class TestRichOutputConfiguration:
    """Test RichOutputConfig model validation."""

    def test_rich_output_config_defaults(self) -> None:
        """Test RichOutputConfig default values."""
        config = RichOutputConfig()

        assert config.verbose is False
        assert config.quiet is False
        assert config.console_width == 120
        assert config.force_terminal is True
        assert config.stderr_enabled is True

    def test_rich_output_config_custom_values(self) -> None:
        """Test RichOutputConfig with custom values."""
        config = RichOutputConfig(
            verbose=True,
            quiet=False,
            console_width=80,
            force_terminal=False,
            stderr_enabled=False,
        )

        assert config.verbose is True
        assert config.quiet is False
        assert config.console_width == 80
        assert config.force_terminal is False
        assert config.stderr_enabled is False

    def test_rich_output_config_validation(self) -> None:
        """Test RichOutputConfig validation constraints."""
        # Test minimum console width
        config = RichOutputConfig(console_width=40)
        assert config.console_width == 40

        # Test maximum console width
        config = RichOutputConfig(console_width=300)
        assert config.console_width == 300

    def test_rich_output_config_inherits_from_kpat_base_model(self) -> None:
        """Test that RichOutputConfig inherits from KPATBaseModel."""
        from kp_analysis_toolkit.models.base import KPATBaseModel

        config = RichOutputConfig()
        assert isinstance(config, KPATBaseModel)
