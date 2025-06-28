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

    @patch("builtins.input", return_value="y")
    def test_prompt_for_upgrade_yes(self, mock_input: Mock) -> None:
        """Test prompt_for_upgrade when user says yes."""
        checker = VersionChecker()

        with patch("click.confirm", return_value=True):
            result = checker.prompt_for_upgrade(__version__)

        assert result is True

    @patch("builtins.input", return_value="n")
    def test_prompt_for_upgrade_no(self, mock_input: Mock) -> None:
        """Test prompt_for_upgrade when user says no."""
        checker = VersionChecker()

        with patch("click.confirm", return_value=False):
            result = checker.prompt_for_upgrade(__version__)

        assert result is False

    @patch("kp_analysis_toolkit.utils.version_checker.shutil.which")
    def test_find_pipx_executable_found(self, mock_which: Mock) -> None:
        """Test _find_pipx_executable when pipx is found."""
        mock_which.return_value = "/usr/bin/pipx"

        checker = VersionChecker()
        result = checker._find_pipx_executable()

        assert result == "/usr/bin/pipx"
        mock_which.assert_called_once_with("pipx")

    @patch("kp_analysis_toolkit.utils.version_checker.shutil.which")
    def test_find_pipx_executable_not_found(self, mock_which: Mock) -> None:
        """Test _find_pipx_executable when pipx is not found."""
        mock_which.return_value = None

        checker = VersionChecker()
        result = checker._find_pipx_executable()

        assert result is None

    @patch("kp_analysis_toolkit.utils.version_checker.subprocess.run")
    @patch("kp_analysis_toolkit.utils.version_checker.shutil.which")
    def test_upgrade_package_success(self, mock_which: Mock, mock_run: Mock) -> None:
        """Test upgrade_package when upgrade succeeds."""
        mock_which.return_value = "/usr/bin/pipx"
        mock_run.return_value = Mock(returncode=0)

        checker = VersionChecker()
        result = checker.upgrade_package()

        assert result is True
        mock_run.assert_called_once()

    @patch("kp_analysis_toolkit.utils.version_checker.shutil.which")
    def test_upgrade_package_pipx_not_found(self, mock_which: Mock) -> None:
        """Test upgrade_package when pipx is not found."""
        mock_which.return_value = None

        checker = VersionChecker()
        result = checker.upgrade_package()

        assert result is False


class TestCheckAndPromptUpdate:
    """Tests for the check_and_prompt_update function."""

    @patch("kp_analysis_toolkit.utils.version_checker.VersionChecker")
    def test_no_update_available(self, mock_checker_class: Mock) -> None:
        """Test when no update is available."""
        mock_checker = Mock()
        mock_checker.check_for_updates.return_value = (False, __version__)
        mock_checker_class.return_value = mock_checker

        # Should not raise any exception
        check_and_prompt_update()

        mock_checker.check_for_updates.assert_called_once()

    @patch("kp_analysis_toolkit.utils.version_checker.VersionChecker")
    def test_network_error(self, mock_checker_class: Mock) -> None:
        """Test when network error occurs."""
        mock_checker = Mock()
        mock_checker.check_for_updates.return_value = (False, None)
        mock_checker_class.return_value = mock_checker

        # Should not raise any exception
        check_and_prompt_update()

        mock_checker.check_for_updates.assert_called_once()

    @patch("kp_analysis_toolkit.utils.version_checker.VersionChecker")
    def test_update_available_user_declines(self, mock_checker_class: Mock) -> None:
        """Test when update is available but user declines."""
        newer_version = _get_next_minor_version(__version__)
        mock_checker = Mock()
        mock_checker.check_for_updates.return_value = (True, newer_version)
        mock_checker.prompt_for_upgrade.return_value = False
        mock_checker_class.return_value = mock_checker

        check_and_prompt_update()

        mock_checker.check_for_updates.assert_called_once()
        mock_checker.prompt_for_upgrade.assert_called_once_with(newer_version)
        mock_checker.upgrade_package.assert_not_called()

    @patch("kp_analysis_toolkit.utils.version_checker.VersionChecker")
    def test_update_available_user_accepts_success(
        self,
        mock_checker_class: Mock,
    ) -> None:
        """Test when update is available, user accepts, and upgrade succeeds."""
        newer_version = _get_next_minor_version(__version__)
        mock_checker = Mock()
        mock_checker.check_for_updates.return_value = (True, newer_version)
        mock_checker.prompt_for_upgrade.return_value = True
        mock_checker.upgrade_package.return_value = True
        mock_checker_class.return_value = mock_checker

        check_and_prompt_update()

        mock_checker.check_for_updates.assert_called_once()
        mock_checker.prompt_for_upgrade.assert_called_once_with(newer_version)
        mock_checker.upgrade_package.assert_called_once()
        mock_checker.restart_application.assert_called_once()

    @patch("kp_analysis_toolkit.utils.version_checker.VersionChecker")
    def test_update_available_user_accepts_fails(
        self,
        mock_checker_class: Mock,
    ) -> None:
        """Test when update is available, user accepts, but upgrade fails."""
        newer_version = _get_next_minor_version(__version__)
        mock_checker = Mock()
        mock_checker.check_for_updates.return_value = (True, newer_version)
        mock_checker.prompt_for_upgrade.return_value = True
        mock_checker.upgrade_package.return_value = False
        mock_checker_class.return_value = mock_checker

        check_and_prompt_update()

        mock_checker.check_for_updates.assert_called_once()
        mock_checker.prompt_for_upgrade.assert_called_once_with(newer_version)
        mock_checker.upgrade_package.assert_called_once()
        mock_checker.restart_application.assert_not_called()
