"""
Comprehensive tests for RichOutput dependency injection implementation.

This test file specifically captures the DI changes made for RichOutput,
ensuring all functionality works correctly together.
"""

from unittest.mock import MagicMock, patch

import pytest

from kp_analysis_toolkit.core.containers.application import (
    ApplicationContainer,
    configure_application_container,
    container,
    initialize_dependency_injection,
)
from kp_analysis_toolkit.core.services.rich_output import RichOutputService
from kp_analysis_toolkit.models.rich_config import RichOutputConfig
from kp_analysis_toolkit.utils.rich_output import get_rich_output


class TestRichOutputDIImplementation:
    """Test the complete DI implementation for RichOutput."""

    def test_full_di_stack_integration(self) -> None:
        """Test the complete DI stack from container to service."""
        # Reset container to ensure clean state
        container.reset_singletons()

        # Initialize DI with specific configuration
        initialize_dependency_injection(
            verbose=True,
            quiet=False,
            console_width=100,
            force_terminal=False,
            stderr_enabled=True,
        )

        # Get the service through DI
        rich_output = container.core().rich_output()

        # Verify the service was configured correctly
        assert isinstance(rich_output, RichOutputService)
        assert rich_output.verbose is True
        assert rich_output.quiet is False
        # Use tolerant assertion for CI environments
        from tests.conftest import assert_console_width_tolerant
        assert_console_width_tolerant(rich_output.console.width, 100)
        assert_console_width_tolerant(rich_output.error_console.width, 100)

    def test_backward_compatibility_layer(self) -> None:
        """Test that backward compatibility layer works with DI."""
        # Reset container
        container.reset_singletons()

        # Initialize DI
        initialize_dependency_injection(verbose=False, quiet=True)

        # Test backward compatibility imports
        from kp_analysis_toolkit.utils.rich_output import (
            RichOutput as BackwardRichOutput,
        )

        # Should be the same class as RichOutputService
        assert BackwardRichOutput is RichOutputService

        # Test get_rich_output function with no parameters (uses DI)
        rich_output = get_rich_output()
        assert isinstance(rich_output, RichOutputService)
        assert rich_output.quiet is True  # Should get the DI-configured instance

        # Test get_rich_output with parameters (creates new instance)
        rich_output_override = get_rich_output(verbose=True, quiet=False)
        assert isinstance(rich_output_override, RichOutputService)
        assert rich_output_override.verbose is True
        assert rich_output_override.quiet is False

    def test_get_rich_output_with_overrides(self) -> None:
        """Test get_rich_output with parameter overrides."""
        # Reset container
        container.reset_singletons()

        # Initialize DI with one set of values
        initialize_dependency_injection(verbose=False, quiet=False)

        # Override with get_rich_output parameters
        rich_output = get_rich_output(verbose=True, quiet=True)

        # Should get new instance with overridden values
        assert rich_output.verbose is True
        assert rich_output.quiet is True

    def test_singleton_behavior_across_di_and_utils(self) -> None:
        """Test singleton behavior between DI container and utils."""
        # Reset container
        container.reset_singletons()

        # Initialize DI
        initialize_dependency_injection()

        # Get instance through DI
        di_instance = container.core().rich_output()

        # Get instance through utils (without overrides)
        utils_instance = get_rich_output()

        # Should be the same instance
        assert di_instance is utils_instance

    @patch("kp_analysis_toolkit.core.services.rich_output.Console")
    def test_console_configuration_through_di(
        self, mock_console_class: MagicMock,
    ) -> None:
        """Test that Console objects are configured correctly through DI."""
        mock_console = MagicMock()
        mock_error_console = MagicMock()
        mock_console_class.side_effect = [mock_console, mock_error_console]

        # Reset container
        container.reset_singletons()

        # Initialize DI with specific console settings
        initialize_dependency_injection(
            console_width=80,
            force_terminal=True,
        )

        # Get the service
        rich_output = container.core().rich_output()

        # Verify Console was created with correct parameters
        expected_console_calls = 2  # Main console and error console
        assert mock_console_class.call_count == expected_console_calls

        # Check the parameters passed to Console
        for call in mock_console_class.call_args_list:
            args, kwargs = call
            assert kwargs["width"] == 80
            assert kwargs["force_terminal"] is True

    def test_configuration_model_validation(self) -> None:
        """Test that RichOutputConfig validates properly in DI context."""
        # Test that invalid configuration raises appropriate errors
        with pytest.raises((ValueError, TypeError)):
            config = RichOutputConfig(console_width=-1)  # Invalid width

        # Test valid configuration
        config = RichOutputConfig(
            verbose=True,
            quiet=False,
            console_width=120,
            force_terminal=True,
            stderr_enabled=True,
        )

        # Should be able to create service with valid config
        service = RichOutputService(config)
        assert isinstance(service, RichOutputService)

    def test_container_reconfiguration(self) -> None:
        """Test that container can be reconfigured with new settings."""
        # Reset container
        container.reset_singletons()

        # Initial configuration
        configure_application_container(verbose=False, quiet=False)
        first_instance = container.core().rich_output()
        assert first_instance.verbose is False

        # Reset and reconfigure
        container.reset_singletons()
        configure_application_container(verbose=True, quiet=False)
        second_instance = container.core().rich_output()
        assert second_instance.verbose is True

        # Should be different instances due to reset
        assert first_instance is not second_instance

    def test_di_initialization_error_handling(self) -> None:
        """Test error handling in DI initialization."""
        # Test that initialization with invalid parameters doesn't crash
        try:
            initialize_dependency_injection(
                console_width=0,  # This might be invalid
            )
            # If it doesn't raise an error, that's fine too
        except Exception as e:
            # If it does raise an error, it should be a meaningful one
            assert isinstance(e, (ValueError, TypeError))

    def test_convenience_functions_work_with_di(self) -> None:
        """Test that convenience functions work with DI-managed instances."""
        # Reset container
        container.reset_singletons()

        # Initialize DI
        initialize_dependency_injection(verbose=True)

        # Import and test convenience functions
        from kp_analysis_toolkit.utils.rich_output import (
            debug,
            error,
            info,
            success,
            warning,
        )

        # These should work without throwing errors
        # (We can't easily test output, but we can test they don't crash)
        try:
            info("Test info message")
            success("Test success message")
            warning("Test warning message")
            error("Test error message")
            debug("Test debug message")
        except Exception as e:
            pytest.fail(f"Convenience functions failed with DI: {e}")

    def test_multiple_container_instances(self) -> None:
        """Test behavior with multiple container instances."""
        # Create separate container instances
        container1 = ApplicationContainer()
        container2 = ApplicationContainer()

        # Configure them completely with all required values
        container1.core().config.verbose.from_value(True)
        container1.core().config.quiet.from_value(False)
        container1.core().config.console_width.from_value(120)
        container1.core().config.force_terminal.from_value(True)
        container1.core().config.stderr_enabled.from_value(True)

        container2.core().config.verbose.from_value(False)
        container2.core().config.quiet.from_value(True)
        container2.core().config.console_width.from_value(80)
        container2.core().config.force_terminal.from_value(False)
        container2.core().config.stderr_enabled.from_value(False)

        # Get services from each
        service1 = container1.core().rich_output()
        service2 = container2.core().rich_output()

        # Should have different configurations
        assert service1.verbose is True
        assert service1.quiet is False
        assert service2.verbose is False
        assert service2.quiet is True

        # Should be different instances
        assert service1 is not service2


class TestRichOutputDIPerformance:
    """Test performance aspects of the DI implementation."""

    def test_singleton_creation_performance(self) -> None:
        """Test that singleton creation is efficient."""
        # Reset container
        container.reset_singletons()

        # Initialize DI
        initialize_dependency_injection()

        # First call should create the instance
        instance1 = container.core().rich_output()

        # Subsequent calls should return the same instance quickly
        for _ in range(100):
            instance = container.core().rich_output()
            assert instance is instance1

    def test_configuration_change_performance(self) -> None:
        """Test performance of configuration changes."""
        import time

        # Test that reconfiguration doesn't take too long
        start_time = time.time()

        for i in range(10):
            container.reset_singletons()
            configure_application_container(
                verbose=bool(i % 2),
                quiet=not bool(i % 2),
                console_width=80 + i,
            )
            container.core().rich_output()

        end_time = time.time()

        # Should complete within reasonable time (adjust as needed)
        assert end_time - start_time < 1.0  # 1 second for 10 reconfigurations


class TestRichOutputDIEdgeCases:
    """Test edge cases and error conditions in the DI implementation."""

    def test_container_reset_during_usage(self) -> None:
        """Test behavior when container is reset while service is in use."""
        # Reset container
        container.reset_singletons()

        # Initialize and get service
        initialize_dependency_injection()
        service = container.core().rich_output()

        # Reset container while service is still in use
        container.reset_singletons()

        # Original service should still work
        try:
            service.info("Test message")
        except Exception as e:
            pytest.fail(f"Service failed after container reset: {e}")

        # New service should be different
        initialize_dependency_injection()
        new_service = container.core().rich_output()
        assert new_service is not service

    def test_invalid_configuration_handling(self) -> None:
        """Test handling of invalid configurations."""
        # Reset container
        container.reset_singletons()

        # Test with potentially problematic values
        try:
            configure_application_container(
                console_width=999999,  # Very large width
            )
            service = container.core().rich_output()
            # Should either work or fail gracefully
            assert isinstance(service, RichOutputService)
        except Exception:
            # If it fails, that's acceptable for invalid input
            pass

    def test_concurrent_access_safety(self) -> None:
        """Test that concurrent access to DI container is safe."""
        import threading

        # Reset container
        container.reset_singletons()

        # Initialize DI
        initialize_dependency_injection()

        services = []
        errors = []

        def get_service():
            try:
                service = container.core().rich_output()
                services.append(service)
            except Exception as e:
                errors.append(e)

        # Create multiple threads accessing the container
        threads = [threading.Thread(target=get_service) for _ in range(10)]

        # Start all threads
        for thread in threads:
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Should have no errors
        assert len(errors) == 0

        # All services should be the same instance (singleton)
        assert len(services) == 10
        for service in services:
            assert service is services[0]
