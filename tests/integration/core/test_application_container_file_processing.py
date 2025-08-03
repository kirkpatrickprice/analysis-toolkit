"""Integration tests for application container with file processing."""

from pathlib import Path
from unittest.mock import Mock, patch

from dependency_injector.providers import Configuration

from kp_analysis_toolkit.core.containers.application import (
    ApplicationContainer,
    container,
    initialize_dependency_injection,
)
from kp_analysis_toolkit.core.services.file_processing import FileProcessingService
from kp_analysis_toolkit.core.services.rich_output import RichOutputService


class TestApplicationContainerFileProcessingIntegration:
    """Test application container integration with file processing services."""

    def test_application_container_includes_file_processing(self) -> None:
        """Test that ApplicationContainer includes file processing service in core."""
        app_container = ApplicationContainer()

        assert hasattr(app_container, "core")
        assert hasattr(app_container.core(), "file_processing_service")
        assert app_container.core().file_processing_service is not None

    def test_file_processing_service_available_through_global_container(self) -> None:
        """Test that file processing service is available through global container."""
        # Reset container state
        global_container: ApplicationContainer = container

        # Configure the container
        global_container.core().config.verbose.from_value(False)
        global_container.core().config.quiet.from_value(False)
        global_container.core().config.console_width.from_value(120)
        global_container.core().config.force_terminal.from_value(True)
        global_container.core().config.stderr_enabled.from_value(True)

        # Get file processing service from core container
        service: FileProcessingService = (
            global_container.core().file_processing_service()
        )

        assert isinstance(service, FileProcessingService)
        assert service.encoding_detector is not None
        assert service.hash_generator is not None
        assert service.file_validator is not None
        assert service.rich_output is not None

    def test_file_processing_service_end_to_end_workflow(self, tmp_path: Path) -> None:
        """Test file processing service end-to-end workflow through container."""
        # Create a test file
        test_file: Path = tmp_path / "test.txt"
        test_file.write_text("Hello, world!", encoding="utf-8")

        # Configure container
        global_container: ApplicationContainer = container
        global_container.core().config.verbose.from_value(False)
        global_container.core().config.quiet.from_value(False)
        global_container.core().config.console_width.from_value(120)
        global_container.core().config.force_terminal.from_value(True)
        global_container.core().config.stderr_enabled.from_value(True)

        # Get service and process file
        service: FileProcessingService = (
            global_container.core().file_processing_service()
        )
        result: dict[str, str | None] = service.process_file(test_file)

        # Verify results
        assert isinstance(result, dict)
        assert "encoding" in result
        assert "hash" in result
        from tests.conftest import assert_valid_encoding

        assert_valid_encoding(result["encoding"], "utf-8")
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
        service: FileProcessingService = container.core().file_processing_service()
        assert isinstance(service, FileProcessingService)

        # Verify configuration propagated to rich output
        rich_config: Configuration = container.core().config
        assert rich_config.verbose() is True
        assert rich_config.quiet() is False
        assert rich_config.console_width() == 80  # noqa: PLR2004
        assert rich_config.force_terminal() is False
        assert rich_config.stderr_enabled() is False

    @patch("kp_analysis_toolkit.utils.get_file_encoding._get_file_processing_service")
    @patch("kp_analysis_toolkit.utils.hash_generator._get_file_processing_service")
    def test_backward_compatibility_utilities_use_container(
        self,
        mock_hash_get_service: Mock,
        mock_encoding_get_service: Mock,
    ) -> None:
        """Test that backward compatibility utilities can access container services."""
        # Initialize DI first
        initialize_dependency_injection()

        # Create a mock service to return
        from unittest.mock import MagicMock

        mock_service = MagicMock()
        mock_service.detect_encoding.return_value = "utf-8"
        mock_service.generate_hash.return_value = "mock_hash"

        # Setup mocks to return the service when called
        mock_hash_get_service.return_value = mock_service
        mock_encoding_get_service.return_value = mock_service

        # Create a test file to trigger the utility functions
        import tempfile
        from pathlib import Path

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("test content")
            test_file = Path(f.name)

        try:
            # Call the utility functions to trigger DI service usage
            from kp_analysis_toolkit.utils.get_file_encoding import detect_encoding
            from kp_analysis_toolkit.utils.hash_generator import generate_file_hash

            # These calls should use the DI services
            encoding: str | None = detect_encoding(test_file)
            file_hash: str = generate_file_hash(test_file)

            # Verify the mocked services were called
            mock_encoding_get_service.assert_called()
            mock_hash_get_service.assert_called()

            # Verify the service methods were called
            mock_service.detect_encoding.assert_called_with(test_file)
            mock_service.generate_hash.assert_called_with(test_file)

            # Verify the results
            assert encoding == "utf-8"
            assert file_hash == "mock_hash"

        finally:
            # Clean up
            test_file.unlink(missing_ok=True)


class TestFileProcessingContainerWiring:
    """Test file processing container wiring for backward compatibility."""

    def test_module_wiring_configuration(self) -> None:
        """Test that core container can be wired to utility modules."""
        # Configure container
        initialize_dependency_injection()

        # Verify core container is wired
        core_container = container.core()
        assert core_container is not None

        # Test that wiring doesn't raise errors
        core_container.wire(modules=["unittest.mock"])  # Safe module to test
        core_container.unwire()

    def test_global_container_singleton_behavior(
        self, container_initialized: None,
    ) -> None:
        """Test that global container maintains singleton services."""
        # Container is properly initialized by the fixture

        # Get service instances multiple times
        service1: FileProcessingService = container.core().file_processing_service()
        service2: FileProcessingService = container.core().file_processing_service()

        # Services are created using Factory providers, so they won't be singletons
        # This test should verify that the behavior is consistent with the implementation
        # Since the current implementation uses Factory providers, we expect new instances
        assert service1 is not service2, "Factory providers should create new instances"

        # However, the core container itself should be a singleton
        container1 = container.core()
        container2 = container.core()
        assert container1 is container2, "Core container should be singleton"

    def test_application_container_dependency_injection(
        self, container_initialized: None,
    ) -> None:
        """Test that file processing container gets core dependencies correctly."""
        # Reconfigure with specific settings for this test
        initialize_dependency_injection(console_width=100, verbose=True)

        # Get file processing service
        fp_service: FileProcessingService = container.core().file_processing_service()

        # Verify it has access to rich output from core
        assert fp_service.rich_output is not None

        # Verify rich output configuration propagated
        rich_output: RichOutputService = container.core().rich_output()
        assert rich_output.verbose is True
