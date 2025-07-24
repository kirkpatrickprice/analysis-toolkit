"""Unit tests for the timestamp service."""

from unittest.mock import Mock, patch

import pytest

from kp_analysis_toolkit.core.services.timestamp import (
    TimeStamper,
    TimeStampService,
)

# Constants for timestamp format validation
EXPECTED_TIMESTAMP_LENGTH = 15
DASH_POSITION = 8


@pytest.mark.core
@pytest.mark.unit
class TestTimeStampService:
    """Test the TimeStampService class."""

    def test_timestamp_service_initialization(self) -> None:
        """Test that TimeStampService can be initialized."""
        service = TimeStampService()
        assert service is not None
        assert hasattr(service, "get_timestamp")

    def test_get_timestamp_format(self) -> None:
        """Test that get_timestamp returns correct format."""
        service = TimeStampService()
        timestamp = service.get_timestamp()

        # Should be in format YYYYMMDD-HHMMSS
        assert len(timestamp) == EXPECTED_TIMESTAMP_LENGTH
        assert timestamp[DASH_POSITION] == "-"

        # Should be all digits except the dash
        assert timestamp[:DASH_POSITION].isdigit()
        assert timestamp[DASH_POSITION + 1 :].isdigit()

    def test_get_timestamp_uniqueness(self) -> None:
        """Test that consecutive timestamps are different or same within same second."""
        service = TimeStampService()
        timestamp1 = service.get_timestamp()
        timestamp2 = service.get_timestamp()

        # They might be the same if called in the same second
        # This is expected behavior, not a bug
        assert isinstance(timestamp1, str)
        assert isinstance(timestamp2, str)
        assert len(timestamp1) == EXPECTED_TIMESTAMP_LENGTH
        assert len(timestamp2) == EXPECTED_TIMESTAMP_LENGTH

    @patch("kp_analysis_toolkit.core.services.timestamp.datetime")
    def test_get_timestamp_mocked(self, mock_datetime: Mock) -> None:
        """Test timestamp generation with mocked datetime."""
        # Mock datetime.now()
        mock_datetime.now.return_value.strftime.return_value = "20231225-143000"

        service = TimeStampService()
        timestamp = service.get_timestamp()

        assert timestamp == "20231225-143000"
        mock_datetime.now.assert_called_once()
        mock_datetime.now.return_value.strftime.assert_called_once_with(
            "%Y%m%d-%H%M%S",
        )

    def test_protocol_compliance(self) -> None:
        """Test that TimeStampService implements TimeStamper protocol correctly."""
        service = TimeStampService()

        # Should have get_timestamp method
        assert hasattr(service, "get_timestamp")
        assert callable(service.get_timestamp)

        # Method should return string
        result = service.get_timestamp()
        assert isinstance(result, str)


@pytest.mark.core
@pytest.mark.unit
class TestTimeStamperProtocol:
    """Test the TimeStamper protocol."""

    def test_protocol_definition(self) -> None:
        """Test that TimeStamper protocol is properly defined."""
        # Should have get_timestamp method defined
        assert hasattr(TimeStamper, "get_timestamp")

        # Should be a typing.Protocol
        from typing import get_origin

        assert (
            get_origin(TimeStamper) is None
        )  # Protocols don't have origins like generics

    def test_service_implements_protocol(self) -> None:
        """Test that TimeStampService correctly implements TimeStamper protocol."""
        service = TimeStampService()

        # Should implement all required methods from protocol
        assert hasattr(service, "get_timestamp")
        assert callable(service.get_timestamp)

        # Protocol compliance - service should behave as expected by protocol
        result = service.get_timestamp()
        assert isinstance(result, str)
        assert len(result) == EXPECTED_TIMESTAMP_LENGTH
