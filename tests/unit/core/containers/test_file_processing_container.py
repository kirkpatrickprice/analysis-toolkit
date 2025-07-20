"""Tests for file processing container."""

from typing import TYPE_CHECKING

import pytest

from kp_analysis_toolkit.core.containers.file_processing import FileProcessingContainer
from kp_analysis_toolkit.core.services.file_processing import FileProcessingService
from kp_analysis_toolkit.core.services.file_processing.encoding import (
    RobustEncodingDetector,
)
from kp_analysis_toolkit.core.services.file_processing.hashing import (
    SHA384FileHashGenerator,
)

if TYPE_CHECKING:
    from kp_analysis_toolkit.core.containers.core import CoreContainer


@pytest.mark.file_processing
@pytest.mark.core
@pytest.mark.unit
class TestFileProcessingContainer:
    """Test the FileProcessingContainer for dependency injection."""

    def test_file_processing_container_creation(self) -> None:
        """Test that FileProcessingContainer can be created without errors."""
        container = FileProcessingContainer()
        assert container is not None

    def test_file_processing_container_has_required_providers(self) -> None:
        """Test that FileProcessingContainer has all required providers."""
        container = FileProcessingContainer()

        # Check all providers exist
        assert hasattr(container, "encoding_detector")
        assert hasattr(container, "hash_generator")
        assert hasattr(container, "file_validator")
        assert hasattr(container, "file_processing_service")

        # Check providers are configured
        assert container.encoding_detector is not None
        assert container.hash_generator is not None
        assert container.file_validator is not None
        assert container.file_processing_service is not None

    def test_encoding_detection_service_creation(
        self,
        real_core_container: "CoreContainer",
    ) -> None:
        """Test that RobustEncodingDetector can be created from container."""
        container = FileProcessingContainer()
        container.core.override(real_core_container)

        # Get the service
        service = container.encoding_detector()

        assert isinstance(service, RobustEncodingDetector)

    def test_hashing_service_creation(
        self,
        real_core_container: "CoreContainer",
    ) -> None:
        """Test that SHA384FileHashGenerator can be created from container."""
        container = FileProcessingContainer()
        container.core.override(real_core_container)

        # Get the service
        service = container.hash_generator()

        assert isinstance(service, SHA384FileHashGenerator)

    def test_file_processing_service_creation(
        self,
        real_core_container: "CoreContainer",
    ) -> None:
        """Test that FileProcessingService can be created from container."""
        container = FileProcessingContainer()
        container.core.override(real_core_container)

        # Get the service
        service = container.file_processing_service()

        assert isinstance(service, FileProcessingService)

    def test_file_processing_service_dependencies_injected(
        self,
        real_core_container: "CoreContainer",
    ) -> None:
        """Test that FileProcessingService receives proper dependencies."""
        container = FileProcessingContainer()
        container.core.override(real_core_container)

        # Get the service
        service = container.file_processing_service()

        # Test that dependencies are injected
        assert service.encoding_detector is not None
        assert service.hash_generator is not None
        assert service.file_validator is not None

    def test_container_wiring_capabilities(
        self,
        real_core_container: "CoreContainer",
    ) -> None:
        """Test that the container can be properly wired for dependency injection."""
        container = FileProcessingContainer()
        container.core.override(real_core_container)

        # Wire the container
        container.wire(modules=["__main__"])

        # Test that wiring works
        assert container.file_processing_service is not None

    def test_singleton_behavior(self, real_core_container: "CoreContainer") -> None:
        """Test that services maintain factory behavior within container."""
        container = FileProcessingContainer()
        container.core.override(real_core_container)

        # Get the same service multiple times
        service1 = container.file_processing_service()
        service2 = container.file_processing_service()

        # FileProcessingService is a Factory, so instances are different
        assert service1 is not service2
        assert isinstance(service1, FileProcessingService)
        assert isinstance(service2, FileProcessingService)

        # But component services should be the same (singleton/factory pattern)
        encoding1 = container.encoding_detector()
        encoding2 = container.encoding_detector()
        # Encoding detectors are factories, so different instances
        assert encoding1 is not encoding2

        # Hash generators are also factories, so different instances
        hash1 = container.hash_generator()
        hash2 = container.hash_generator()
        assert hash1 is not hash2
