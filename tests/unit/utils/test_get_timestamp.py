"""Unit tests for the get_timestamp utility function."""

import re
from unittest.mock import Mock, patch

import pytest

from kp_analysis_toolkit.utils.get_timestamp import get_timestamp

# Constants for test validation
EXPECTED_CALL_COUNT_THREE = 3
EXPECTED_TIMESTAMP_LENGTH = 15  # 8 digits + 1 hyphen + 6 digits
# Regex pattern for YYYYMMDD-HHMMSS format (8 digits, hyphen, 6 digits)
TIMESTAMP_PATTERN = re.compile(r"^\d{8}-\d{6}$")


@pytest.mark.core
@pytest.mark.unit
class TestGetTimestamp:
    """Test the get_timestamp utility function."""

    def test_get_timestamp_returns_string(self) -> None:
        """Test that get_timestamp returns a string."""
        # AI-GEN: GitHub Copilot|2025-01-24|KPAT-Utils-Tests|reviewed:yes
        result = get_timestamp()

        assert isinstance(result, str)
        assert len(result) > 0
        # END AI-GEN

    def test_get_timestamp_format_validation(self) -> None:
        """Test that get_timestamp returns timestamp in expected format."""
        # AI-GEN: GitHub Copilot|2025-01-24|KPAT-Utils-Tests|reviewed:yes
        result = get_timestamp()

        # Should match YYYYMMDD-HHMMSS pattern (8 digits, hyphen, 6 digits)
        assert TIMESTAMP_PATTERN.match(result) is not None, (
            f"Timestamp '{result}' does not match expected pattern YYYYMMDD-HHMMSS"
        )

        # Additional validation that the pattern is exactly what we expect
        assert len(result) == EXPECTED_TIMESTAMP_LENGTH  # 8 + 1 + 6 characters
        assert result[8] == "-"  # Hyphen separator at correct position
        # END AI-GEN

    def test_get_timestamp_uses_container_service(self) -> None:
        """Test that get_timestamp properly delegates to container timestamp service."""
        # AI-GEN: GitHub Copilot|2025-01-24|KPAT-Utils-Tests|reviewed:yes
        mock_timestamp_service = Mock()
        mock_timestamp_service.get_timestamp.return_value = "20250124-143000"

        mock_container = Mock()
        mock_container.core.timestamp_service.return_value = mock_timestamp_service

        with patch(
            "kp_analysis_toolkit.core.containers.application.container", mock_container,
        ):
            result = get_timestamp()

            # Verify the service was called
            mock_container.core.timestamp_service.assert_called_once()
            mock_timestamp_service.get_timestamp.assert_called_once()

            # Verify the result
            assert result == "20250124-143000"
        # END AI-GEN

    def test_get_timestamp_container_import_lazy(self) -> None:
        """Test that container import happens inside function (lazy loading)."""
        # AI-GEN: GitHub Copilot|2025-01-24|KPAT-Utils-Tests|reviewed:yes
        # This test verifies that the import happens inside the function
        # which is important for avoiding circular imports
        mock_timestamp_service = Mock()
        mock_timestamp_service.get_timestamp.return_value = "20250124-150000"

        mock_container = Mock()
        mock_container.core.timestamp_service.return_value = mock_timestamp_service

        with patch(
            "kp_analysis_toolkit.core.containers.application.container", mock_container,
        ):
            # Call the function
            result = get_timestamp()

            # Verify container was accessed
            assert mock_container.core.timestamp_service.called
            assert result == "20250124-150000"
        # END AI-GEN

    def test_get_timestamp_multiple_calls_unique_values(self) -> None:
        """Test that multiple calls can return different timestamps."""
        # AI-GEN: GitHub Copilot|2025-01-24|KPAT-Utils-Tests|reviewed:yes
        mock_timestamp_service1 = Mock()
        mock_timestamp_service1.get_timestamp.return_value = "20250124-143000"
        mock_timestamp_service2 = Mock()
        mock_timestamp_service2.get_timestamp.return_value = "20250124-143001"
        mock_timestamp_service3 = Mock()
        mock_timestamp_service3.get_timestamp.return_value = "20250124-143002"

        mock_container = Mock()
        mock_container.core.timestamp_service.side_effect = [
            mock_timestamp_service1,
            mock_timestamp_service2,
            mock_timestamp_service3,
        ]

        with patch(
            "kp_analysis_toolkit.core.containers.application.container", mock_container,
        ):
            # Call multiple times
            result1 = get_timestamp()
            result2 = get_timestamp()
            result3 = get_timestamp()

            # Each call should return different values
            assert result1 == "20250124-143000"
            assert result2 == "20250124-143001"
            assert result3 == "20250124-143002"

            # Service should have been called 3 times
            assert (
                mock_container.core.timestamp_service.call_count
                == EXPECTED_CALL_COUNT_THREE
            )
        # END AI-GEN

    def test_get_timestamp_pydantic_model_integration(self) -> None:
        """Test get_timestamp integration with Pydantic model usage patterns."""
        # AI-GEN: GitHub Copilot|2025-01-24|KPAT-Utils-Tests|reviewed:yes
        # Test the pattern used in nipper_expander models: f"{stem}_expanded-{get_timestamp()}.xlsx"
        mock_timestamp_service = Mock()
        mock_timestamp_service.get_timestamp.return_value = "20250124-143000"

        mock_container = Mock()
        mock_container.core.timestamp_service.return_value = mock_timestamp_service

        with patch(
            "kp_analysis_toolkit.core.containers.application.container", mock_container,
        ):
            # Simulate nipper_expander usage pattern
            stem = "test_file"
            expanded_filename = f"{stem}_expanded-{get_timestamp()}.xlsx"

            # Verify expected format
            assert expanded_filename == "test_file_expanded-20250124-143000.xlsx"

            # Test rtf_to_text usage pattern (direct assignment)
            timestamp = get_timestamp()
            assert timestamp == "20250124-143000"
        # END AI-GEN

    def test_get_timestamp_filename_safe_characters(self) -> None:
        """Test that get_timestamp returns filename-safe characters."""
        # AI-GEN: GitHub Copilot|2025-01-24|KPAT-Utils-Tests|reviewed:yes
        result = get_timestamp()

        # Should only contain digits and dash (filename-safe)
        allowed_chars = set("0123456789-")
        result_chars = set(result)

        assert result_chars.issubset(allowed_chars)

        # Should not contain characters that are problematic in filenames
        forbidden_chars = set('\\/:*?"<>|')
        assert not any(char in result for char in forbidden_chars)
        # END AI-GEN

    def test_get_timestamp_consistency_with_service(self) -> None:
        """Test that get_timestamp maintains consistency with core timestamp service."""
        # AI-GEN: GitHub Copilot|2025-01-24|KPAT-Utils-Tests|reviewed:yes
        # This test ensures the utility function returns exactly what the service returns
        expected_timestamp = "20250124-143000"
        mock_timestamp_service = Mock()
        mock_timestamp_service.get_timestamp.return_value = expected_timestamp

        mock_container = Mock()
        mock_container.core.timestamp_service.return_value = mock_timestamp_service

        with patch(
            "kp_analysis_toolkit.core.containers.application.container", mock_container,
        ):
            result = get_timestamp()

            # Should return exactly what the service returns (no modification)
            assert result == expected_timestamp
            assert result == mock_timestamp_service.get_timestamp.return_value
        # END AI-GEN

    def test_get_timestamp_error_propagation(self) -> None:
        """Test that errors from timestamp service are properly propagated."""
        # AI-GEN: GitHub Copilot|2025-01-24|KPAT-Utils-Tests|reviewed:yes
        mock_timestamp_service = Mock()
        mock_timestamp_service.get_timestamp.side_effect = RuntimeError("Service error")

        mock_container = Mock()
        mock_container.core.timestamp_service.return_value = mock_timestamp_service

        with (
            patch(
                "kp_analysis_toolkit.core.containers.application.container",
                mock_container,
            ),
            pytest.raises(RuntimeError, match="Service error"),
        ):
            # Error should propagate through the utility function
            get_timestamp()
        # END AI-GEN

    def test_get_timestamp_backwards_compatibility(self) -> None:
        """Test backwards compatibility for existing Pydantic model usage."""
        # AI-GEN: GitHub Copilot|2025-01-24|KPAT-Utils-Tests|reviewed:yes
        # Test that the function works in the context it's currently used
        mock_timestamp_service = Mock()
        mock_timestamp_service.get_timestamp.return_value = "20250124-143000"

        mock_container = Mock()
        mock_container.core.timestamp_service.return_value = mock_timestamp_service

        with patch(
            "kp_analysis_toolkit.core.containers.application.container", mock_container,
        ):
            # Test can be imported and called without issues
            from kp_analysis_toolkit.utils.get_timestamp import (
                get_timestamp as imported_func,
            )

            result = imported_func()
            assert result == "20250124-143000"

            # Test works in string formatting contexts
            formatted = f"output_{result}.txt"
            assert formatted == "output_20250124-143000.txt"
        # END AI-GEN
