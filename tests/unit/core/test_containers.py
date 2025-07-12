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
from kp_analysis_toolkit.core.services.file_processing import FileProcessingService
from kp_analysis_toolkit.core.services.rich_output import RichOutputService
from kp_analysis_toolkit.models.rich_config import RichOutputConfig

# Core services that should be available in the CoreContainer
# This list should be updated when new core services are added
EXPECTED_CORE_SERVICES = [
    "rich_output",
    "excel_export_service",
    "file_processing_service",
]


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

    def test_application_container_has_core_and_services(self) -> None:
        """Test that ApplicationContainer has core container with all services."""
        app_container = ApplicationContainer()

        # Check core container
        assert hasattr(app_container, "core")
        assert app_container.core is not None

        # Check that core container has all the expected services
        for service_name in EXPECTED_CORE_SERVICES:
            assert hasattr(app_container.core(), service_name), (
                f"Missing service: {service_name}"
            )

    def test_global_container_instance(self) -> None:
        """Test that global container instance is available and configured."""
        assert container is not None

        # In dependency-injector, containers become DynamicContainer instances
        # We should check for the expected attributes instead of exact type
        assert hasattr(container, "core")

        # Test that the core container is accessible and has all services
        assert container.core is not None
        for service_name in EXPECTED_CORE_SERVICES:
            assert hasattr(container.core(), service_name), (
                f"Missing service: {service_name}"
            )

    def test_file_processing_service_gets_core_dependencies(self) -> None:
        """Test that file processing service receives core dependencies."""
        app_container = ApplicationContainer()

        # Configure core container
        app_container.core().config.verbose.from_value(True)
        app_container.core().config.quiet.from_value(False)
        app_container.core().config.console_width.from_value(100)
        app_container.core().config.force_terminal.from_value(True)
        app_container.core().config.stderr_enabled.from_value(True)

        # Get file processing service from core container
        fp_service = app_container.core().file_processing_service()

        assert isinstance(fp_service, FileProcessingService)
        assert fp_service.rich_output is not None

        # Verify rich output has correct configuration
        rich_output = fp_service.rich_output
        assert rich_output.verbose is True
        assert rich_output.quiet is False

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

    def test_application_container_wiring_functions(self) -> None:
        """Test application container wiring helper functions."""
        # Test configure function
        configure_application_container(
            verbose=True,
            quiet=False,
            console_width=80,
            force_terminal=False,
            stderr_enabled=False,
        )

        # Verify configuration was applied
        core_config = container.core().config
        assert core_config.verbose() is True
        assert core_config.quiet() is False
        assert core_config.console_width() == 80  # noqa: PLR2004
        assert core_config.force_terminal() is False
        assert core_config.stderr_enabled() is False

    def test_wire_application_container_function(self) -> None:
        """Test wire_application_container function."""
        # Should not raise an exception
        wire_application_container()

        # Test that the container is wired (indirect verification)
        assert container is not None

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
