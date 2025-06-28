from enum import Enum

import pytest

from kp_analysis_toolkit.process_scripts.models.base import EnumStrMixin


class DummyOS(EnumStrMixin, Enum):
    """Test enum class for testing EnumStrMixin."""

    WINDOWS = "Windows"
    LINUX = "Linux"
    MACOS = "macOS"


class TestEnumStrMixin:
    def test_exact_match(self) -> None:
        """Test that exact case matching works."""
        assert DummyOS("Windows") == DummyOS.WINDOWS
        assert DummyOS("Linux") == DummyOS.LINUX
        assert DummyOS("macOS") == DummyOS.MACOS

    def test_case_insensitive_match(self) -> None:
        """Test that case-insensitive matching works."""
        assert DummyOS("windows") == DummyOS.WINDOWS
        assert DummyOS("linux") == DummyOS.LINUX
        assert DummyOS("macos") == DummyOS.MACOS

    def test_mixed_case_match(self) -> None:
        """Test that mixed-case matching works."""
        assert DummyOS("WiNdOwS") == DummyOS.WINDOWS
        assert DummyOS("LiNuX") == DummyOS.LINUX
        assert DummyOS("MacOS") == DummyOS.MACOS

    def test_no_match_raises_value_error(self) -> None:
        """Test that ValueError is raised when no match is found."""
        with pytest.raises(ValueError) as excinfo:
            DummyOS("Android")

        # Check that error message contains all valid values
        error_message = str(excinfo.value)
        assert "Invalid value 'Android'" in error_message
        assert "Windows" in error_message
        assert "Linux" in error_message
        assert "macOS" in error_message

    def test_non_string_value(self) -> None:
        """Test that non-string values are handled correctly."""
        with pytest.raises(ValueError) as excinfo:
            DummyOS(123)

        error_message = str(excinfo.value)
        assert "Invalid value '123'" in error_message
