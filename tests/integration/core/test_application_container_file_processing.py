"""Integration tests for application container with file processing."""

from pathlib import Path
from unittest.mock import Mock, patch

from kp_analysis_toolkit.core.containers.application import (
    ApplicationContainer,
    container,
    initialize_dependency_injection,
)
from kp_analysis_toolkit.core.services.file_processing import FileProcessingService


class TestApplicationContainerFileProcessingIntegration:
    """Test application container integration with file processing services."""

    def test_application_container_includes_file_processing(self) -> None:
        """Test that ApplicationContainer includes file processing container."""
        app_container = ApplicationContainer()

        assert hasattr(app_container, "file_processing")
        assert app_container.file_processing is not None

    def test_file_processing_service_available_through_global_container(self) -> None:
        """Test that file processing service is available through global container."""
        # Reset container state
        global_container = container

        # Configure the container
        global_container.core().config.verbose.from_value(False)
        global_container.core().config.quiet.from_value(False)
        global_container.core().config.console_width.from_value(120)
        global_container.core().config.force_terminal.from_value(True)
        global_container.core().config.stderr_enabled.from_value(True)

        # Get file processing service
        service = global_container.file_processing().file_processing_service()

        assert isinstance(service, FileProcessingService)
        assert service.encoding_detector is not None
        assert service.hash_generator is not None
        assert service.file_validator is not None
        assert service.rich_output is not None

    def test_file_processing_service_end_to_end_workflow(self, tmp_path: Path) -> None:
        """Test file processing service end-to-end workflow through container."""
        # Create a test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello, world!", encoding="utf-8")

        # Configure container
        global_container = container
        global_container.core().config.verbose.from_value(False)
        global_container.core().config.quiet.from_value(False)
        global_container.core().config.console_width.from_value(120)
        global_container.core().config.force_terminal.from_value(True)
        global_container.core().config.stderr_enabled.from_value(True)

        # Get service and process file
        service = global_container.file_processing().file_processing_service()
        result = service.process_file(test_file)

        # Verify results
        assert isinstance(result, dict)
        assert "encoding" in result
        assert "hash" in result
        assert result["encoding"] == "utf-8"
        assert result["hash"]  # Should have a hash value

    def test_initialization_configures_file_processing_correctly(self) -> None:
        """Test that initialize_dependency_injection configures file processing."""
        # Initialize DI with specific settings
        initialize_dependency_injection(
            verbose=True,
            quiet=False,
            console_width=80,
            force_terminal=False,
            stderr_enabled=False,
        )

        # Verify file processing service is configured
        service = container.file_processing().file_processing_service()
        assert isinstance(service, FileProcessingService)

        # Verify configuration propagated to rich output
        rich_config = container.core().config
        assert rich_config.verbose() is True
        assert rich_config.quiet() is False
        assert rich_config.console_width() == 80  # noqa: PLR2004
        assert rich_config.force_terminal() is False
        assert rich_config.stderr_enabled() is False

    @patch("kp_analysis_toolkit.utils.get_file_encoding.get_di_state")
    @patch("kp_analysis_toolkit.utils.hash_generator.get_di_state")
    def test_backward_compatibility_utilities_use_container(
        self,
        mock_hash_di_state: Mock,
        mock_encoding_di_state: Mock,
    ) -> None:
        """Test that backward compatibility utilities can access container services."""
        # Setup mocks to return the global container and service
        mock_hash_di_state.return_value = (container.file_processing, True)
        mock_encoding_di_state.return_value = (container.file_processing, True)

        # Initialize DI
        initialize_dependency_injection()

        # These calls should trigger DI state checks
        mock_hash_di_state.assert_called()
        mock_encoding_di_state.assert_called()


class TestFileProcessingContainerWiring:
    """Test file processing container wiring for backward compatibility."""

    def test_module_wiring_configuration(self) -> None:
        """Test that file processing container can be wired to utility modules."""
        # Configure container
        initialize_dependency_injection()

        # Verify container is wired
        file_processing_container = container.file_processing()
        assert file_processing_container is not None

        # Test that wiring doesn't raise errors
        file_processing_container.wire(modules=["unittest.mock"])  # Safe module to test
        file_processing_container.unwire()

    def test_global_container_singleton_behavior(self) -> None:
        """Test that global container maintains singleton services."""
        # Get service instances multiple times
        service1 = container.file_processing().file_processing_service()
        service2 = container.file_processing().file_processing_service()

        # Should be the same instance
        assert service1 is service2

        # Same for encoding detector
        encoder1 = container.file_processing().encoding_detector()
        encoder2 = container.file_processing().encoding_detector()
        assert encoder1 is encoder2

    def test_application_container_dependency_injection(self) -> None:
        """Test that file processing container gets core dependencies correctly."""
        # Configure application container
        initialize_dependency_injection(console_width=100, verbose=True)

        # Get file processing service
        fp_service = container.file_processing().file_processing_service()

        # Verify it has access to rich output from core
        assert fp_service.rich_output is not None

        # Verify rich output configuration propagated
        rich_output = container.core().rich_output()
        assert rich_output.verbose is True
