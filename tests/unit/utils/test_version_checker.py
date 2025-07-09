"""Tests for the version checker utility."""

import json
from unittest.mock import Mock, patch
from urllib.error import URLError

from kp_analysis_toolkit import __version__
from kp_analysis_toolkit.utils.version_checker import (
    VersionChecker,
    check_and_prompt_update,
)


def _get_next_minor_version(current_version: str) -> str:
    """Helper function to get the next minor version for testing."""
    parts = current_version.split(".")
    if len(parts) >= 2:
        major, minor = parts[0], int(parts[1])
        patch_version = parts[2] if len(parts) > 2 else "0"
        return f"{major}.{minor + 1}.{patch_version}"
    return current_version


class TestVersionChecker:
    """Tests for the VersionChecker class."""

    def test_init(self) -> None:
        """Test VersionChecker initialization."""
        checker = VersionChecker()
        assert checker.package_name == "kp-analysis-toolkit"
        assert checker.current_version == __version__

    def test_init_custom_package(self) -> None:
        """Test VersionChecker initialization with custom package name."""
        checker = VersionChecker("custom-package")
        assert checker.package_name == "custom-package"

    @patch("kp_analysis_toolkit.utils.version_checker.urlopen")
    def test_check_for_updates_newer_available(self, mock_urlopen: Mock) -> None:
        """Test check_for_updates when newer version is available."""
        # Calculate a newer version dynamically
        newer_version = _get_next_minor_version(__version__)

        # Mock PyPI response
        mock_response = Mock()
        mock_response.read.return_value = json.dumps(
            {
                "info": {"version": newer_version},
            },
        ).encode()
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=None)
        mock_urlopen.return_value = mock_response

        checker = VersionChecker()
        has_update, latest_version = checker.check_for_updates()

        assert has_update is True
        assert latest_version == newer_version
        mock_urlopen.assert_called_once()

    @patch("kp_analysis_toolkit.utils.version_checker.urlopen")
    def test_check_for_updates_no_update(self, mock_urlopen: Mock) -> None:
        """Test check_for_updates when no update is available."""
        # Mock PyPI response with same version as current
        mock_response = Mock()
        mock_response.read.return_value = json.dumps(
            {
                "info": {"version": __version__},
            },
        ).encode()
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=None)
        mock_urlopen.return_value = mock_response

        checker = VersionChecker()
        has_update, latest_version = checker.check_for_updates()

        assert has_update is False
        assert latest_version == __version__

    @patch("kp_analysis_toolkit.utils.version_checker.urlopen")
    def test_check_for_updates_network_error(self, mock_urlopen: Mock) -> None:
        """Test check_for_updates when network error occurs."""
        mock_urlopen.side_effect = URLError("Network error")

        checker = VersionChecker()
        has_update, latest_version = checker.check_for_updates()

        assert has_update is False
        assert latest_version is None

    def test_prompt_for_upgrade_displays_info(self) -> None:
        """Test prompt_for_upgrade displays upgrade information."""
        checker = VersionChecker()

        with patch(
            "kp_analysis_toolkit.utils.version_checker.get_rich_output",
        ) as mock_rich:
            mock_rich_instance = Mock()
            mock_rich.return_value = mock_rich_instance

            result = checker.prompt_for_upgrade("2.1.0")

        # New implementation returns None and displays info
        assert result is None
        mock_rich_instance.header.assert_called_once()
        mock_rich_instance.panel.assert_called_once()
        mock_rich_instance.info.assert_called_once()
        mock_rich_instance.warning.assert_called_once()


class TestCheckAndPromptUpdate:
    """Tests for the check_and_prompt_update function."""

    @patch("kp_analysis_toolkit.utils.version_checker.VersionChecker")
    def test_no_update_available(self, mock_checker_class: Mock) -> None:
        """Test when no update is available."""
        mock_checker = Mock()
        mock_checker.check_for_updates.return_value = (False, __version__)
        mock_checker_class.return_value = mock_checker

        # Should not raise any exception and should not exit
        check_and_prompt_update()

        mock_checker.check_for_updates.assert_called_once()
        mock_checker.prompt_for_upgrade.assert_not_called()

    @patch("kp_analysis_toolkit.utils.version_checker.VersionChecker")
    def test_network_error(self, mock_checker_class: Mock) -> None:
        """Test when network error occurs during update check."""
        mock_checker = Mock()
        mock_checker.check_for_updates.return_value = (False, None)
        mock_checker_class.return_value = mock_checker

        # Should not raise any exception
        check_and_prompt_update()

        mock_checker.check_for_updates.assert_called_once()
        mock_checker.prompt_for_upgrade.assert_not_called()

    @patch("kp_analysis_toolkit.utils.version_checker.VersionChecker")
    def test_update_available_shows_info_and_exits(
        self, mock_checker_class: Mock,
    ) -> None:
        """Test when update is available, shows info and exits."""
        newer_version = _get_next_minor_version(__version__)
        mock_checker = Mock()
        mock_checker.check_for_updates.return_value = (True, newer_version)
        mock_checker_class.return_value = mock_checker

        with patch("sys.exit") as mock_exit:
            check_and_prompt_update()

        mock_checker.check_for_updates.assert_called_once()
        mock_checker.prompt_for_upgrade.assert_called_once_with(newer_version)
        mock_exit.assert_called_once_with(0)
