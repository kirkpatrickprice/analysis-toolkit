"""Tests for core containers and dependency injection."""

from unittest.mock import MagicMock, patch

import pytest

from kp_analysis_toolkit.core.containers.application import (
    ApplicationContainer,
    configure_application_container,
    container,
    initialize_dependency_injection,
    wire_application_container,
)
from kp_analysis_toolkit.core.containers.core import CoreContainer
from kp_analysis_toolkit.core.services.rich_output import RichOutputService
from kp_analysis_toolkit.models.rich_config import RichOutputConfig


class TestCoreContainer:
    """Test the CoreContainer for dependency injection."""

    def test_core_container_creation(self) -> None:
        """Test that CoreContainer can be created without errors."""
        container = CoreContainer()
        assert container is not None

    def test_core_container_has_rich_output_provider(self) -> None:
        """Test that CoreContainer has rich_output provider configured."""
        container = CoreContainer()
        assert hasattr(container, "rich_output")
        assert container.rich_output is not None

    def test_core_container_config_provider(self) -> None:
        """Test that CoreContainer has config provider."""
        container = CoreContainer()
        assert hasattr(container, "config")
        assert container.config is not None

    def test_rich_output_service_creation(self) -> None:
        """Test that RichOutputService can be created from container."""
        test_container = CoreContainer()

        # Configure the container
        test_container.config.verbose.from_value(False)
        test_container.config.quiet.from_value(False)
        test_container.config.console_width.from_value(120)
        test_container.config.force_terminal.from_value(True)
        test_container.config.stderr_enabled.from_value(True)

        # Get the service
        rich_output = test_container.rich_output()

        assert isinstance(rich_output, RichOutputService)
        assert rich_output.verbose is False
        assert rich_output.quiet is False

    def test_rich_output_service_with_verbose_config(self) -> None:
        """Test RichOutputService with verbose configuration."""
        test_container = CoreContainer()

        # Configure for verbose mode
        test_container.config.verbose.from_value(True)
        test_container.config.quiet.from_value(False)
        test_container.config.console_width.from_value(100)
        test_container.config.force_terminal.from_value(False)
        test_container.config.stderr_enabled.from_value(True)

        rich_output = test_container.rich_output()

        assert rich_output.verbose is True
        assert rich_output.quiet is False

    def test_rich_output_service_with_quiet_config(self) -> None:
        """Test RichOutputService with quiet configuration."""
        test_container = CoreContainer()

        # Configure for quiet mode
        test_container.config.verbose.from_value(False)
        test_container.config.quiet.from_value(True)
        test_container.config.console_width.from_value(80)
        test_container.config.force_terminal.from_value(True)
        test_container.config.stderr_enabled.from_value(False)

        rich_output = test_container.rich_output()

        assert rich_output.verbose is False
        assert rich_output.quiet is True


class TestApplicationContainer:
    """Test the ApplicationContainer and integration functions."""

    def test_application_container_creation(self) -> None:
        """Test that ApplicationContainer can be created."""
        app_container = ApplicationContainer()
        assert app_container is not None
        assert hasattr(app_container, "core")

    def test_application_container_has_core_container(self) -> None:
        """Test that ApplicationContainer contains CoreContainer."""
        app_container = ApplicationContainer()
        core_container = app_container.core()

        # The core provider returns a configured container, not the class
        # Check that it has the expected RichOutput provider
        assert hasattr(core_container, "rich_output")
        assert core_container.rich_output is not None

    def test_configure_application_container(self) -> None:
        """Test configure_application_container function."""
        # Test with default values
        configure_application_container()

        # Verify that the function runs without error by checking core container exists
        assert container.core() is not None

    def test_configure_application_container_with_custom_values(self) -> None:
        """Test configure_application_container with custom values."""
        configure_application_container(
            verbose=True,
            quiet=False,
            console_width=100,
            force_terminal=False,
            stderr_enabled=True,
        )

        # Function should complete without error
        assert container.core() is not None

    def test_wire_application_container(self) -> None:
        """Test wire_application_container function."""
        # This should not raise an error
        wire_application_container()

    def test_initialize_dependency_injection_default(self) -> None:
        """Test initialize_dependency_injection with default parameters."""
        initialize_dependency_injection()

        # Should be able to get a RichOutput instance
        rich_output = container.core().rich_output()
        assert isinstance(rich_output, RichOutputService)

    def test_initialize_dependency_injection_verbose(self) -> None:
        """Test initialize_dependency_injection with verbose=True."""
        # Reset container before test
        container.reset_singletons()

        initialize_dependency_injection(verbose=True, quiet=False)

        rich_output = container.core().rich_output()
        assert isinstance(rich_output, RichOutputService)
        assert rich_output.verbose is True

    def test_initialize_dependency_injection_quiet(self) -> None:
        """Test initialize_dependency_injection with quiet=True."""
        # Reset container before test
        container.reset_singletons()

        initialize_dependency_injection(verbose=False, quiet=True)

        rich_output = container.core().rich_output()
        assert isinstance(rich_output, RichOutputService)
        assert rich_output.quiet is True

    @pytest.mark.usefixtures("isolated_console_env")
    def test_initialize_dependency_injection_custom_console_width(self) -> None:
        """Test initialize_dependency_injection with custom console width."""
        # Reset container before test
        container.reset_singletons()

        initialize_dependency_injection(console_width=80)

        rich_output = container.core().rich_output()
        assert isinstance(rich_output, RichOutputService)
        # Console width should be applied to the console objects
        expected_width = 80
        assert rich_output.console.width == expected_width
        assert rich_output.error_console.width == expected_width


class TestDependencyInjectionIntegration:
    """Test the overall dependency injection system integration."""

    def test_end_to_end_di_workflow(self) -> None:
        """Test complete DI workflow from initialization to service usage."""
        # Reset container before test
        container.reset_singletons()

        # Initialize DI
        initialize_dependency_injection(verbose=True, quiet=False)

        # Get service from container
        rich_output = container.core().rich_output()

        # Verify service is functional
        assert isinstance(rich_output, RichOutputService)
        assert rich_output.verbose is True
        assert rich_output.quiet is False

        # Test that methods are available
        assert hasattr(rich_output, "info")
        assert hasattr(rich_output, "success")
        assert hasattr(rich_output, "error")
        assert hasattr(rich_output, "warning")
        assert hasattr(rich_output, "debug")

    def test_singleton_behavior(self) -> None:
        """Test that RichOutputService behaves as singleton."""
        # Reset container before test
        container.reset_singletons()

        initialize_dependency_injection()

        # Get two instances
        rich_output1 = container.core().rich_output()
        rich_output2 = container.core().rich_output()

        # Should be the same instance (singleton)
        assert rich_output1 is rich_output2

    @patch("kp_analysis_toolkit.core.services.rich_output.Console")
    def test_rich_output_service_initialization(
        self,
        mock_console_class: MagicMock,
    ) -> None:
        """Test that RichOutputService initializes Console objects correctly."""
        mock_console = MagicMock()
        mock_console_class.return_value = mock_console

        config = RichOutputConfig(
            verbose=True,
            quiet=False,
            console_width=100,
            force_terminal=True,
            stderr_enabled=True,
        )

        service = RichOutputService(config)

        # Console should be created with correct parameters
        expected_console_count = 2  # console and error_console
        assert mock_console_class.call_count == expected_console_count

        # Verify service attributes
        assert service.verbose is True
        assert service.quiet is False
