"""Service-level dependency injection fixtures for testing."""

from unittest.mock import MagicMock, Mock

import pytest


@pytest.fixture
def mock_file_processing_service() -> MagicMock:
    """Create a mock FileProcessingService for testing."""
    from kp_analysis_toolkit.core.services.file_processing import FileProcessingService

    service = Mock(spec=FileProcessingService)

    # Setup default behaviors
    service.process_file.return_value = {
        "encoding": "utf-8",
        "hash": "mock_hash_value",
    }
    service.detect_encoding.return_value = "utf-8"
    service.generate_hash.return_value = "mock_hash_value"

    return service
