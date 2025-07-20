"""Integration tests for the CLI with version checking."""

from unittest.mock import Mock, patch

import pytest
from click.testing import CliRunner

from kp_analysis_toolkit.cli import cli


@pytest.mark.cli
@pytest.mark.integration
class TestCLIVersionChecking:
    """Integration tests for CLI version checking functionality."""

    def test_cli_with_skip_update_check(self, cli_runner: CliRunner) -> None:
        """Test CLI with --skip-update-check flag shows help correctly."""
        result = cli_runner.invoke(cli, ["--skip-update-check", "--help"])

        assert result.exit_code == 0
        assert "Command line interface for the KP Analysis Toolkit" in result.output
        assert "--skip-update-check" in result.output

    @patch("kp_analysis_toolkit.cli.main.check_and_prompt_update")
    def test_cli_calls_version_check_by_default(
        self,
        mock_check_update: Mock,
        cli_runner: CliRunner,
    ) -> None:
        """Test that CLI calls version check by default when invoked without subcommand."""
        result = cli_runner.invoke(cli, [])

        assert result.exit_code == 0
        mock_check_update.assert_called_once()

    @patch("kp_analysis_toolkit.cli.main.check_and_prompt_update")
    def test_cli_skips_version_check_when_flag_set(
        self,
        mock_check_update: Mock,
        cli_runner: CliRunner,
    ) -> None:
        """Test that CLI skips version check when flag is set."""
        result = cli_runner.invoke(cli, ["--skip-update-check"])

        assert result.exit_code == 0
        mock_check_update.assert_not_called()

    @patch("kp_analysis_toolkit.cli.main.check_and_prompt_update")
    def test_cli_help_does_not_trigger_version_check(
        self,
        mock_check_update: Mock,
        cli_runner: CliRunner,
    ) -> None:
        """Test that --help does not trigger version check (Click special handling)."""
        result = cli_runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "Command line interface for the KP Analysis Toolkit" in result.output
        assert "--skip-update-check" in result.output
        # Help is handled specially by Click and doesn't invoke the group callback
        mock_check_update.assert_not_called()

    def test_cli_version_option_still_works(self, cli_runner: CliRunner) -> None:
        """Test that the --version option still works correctly."""
        result = cli_runner.invoke(cli, ["--version"])

        assert result.exit_code == 0
        from tests.conftest import assert_rich_version_output

        assert_rich_version_output(result.output)

    @patch("kp_analysis_toolkit.cli.main.check_and_prompt_update")
    def test_subcommands_trigger_version_check(
        self,
        mock_check_update: Mock,
        cli_runner: CliRunner,
    ) -> None:
        """Test that accessing subcommands also triggers version check."""
        result = cli_runner.invoke(cli, ["scripts", "--help"])

        assert result.exit_code == 0
        mock_check_update.assert_called_once()
        from tests.conftest import assert_rich_help_output

        assert_rich_help_output(result.output, "Process collector script results files")

    @patch("kp_analysis_toolkit.cli.main.check_and_prompt_update")
    def test_nipper_subcommand_triggers_version_check(
        self,
        mock_check_update: Mock,
        cli_runner: CliRunner,
    ) -> None:
        """Test that the nipper subcommand also triggers version check."""
        result = cli_runner.invoke(cli, ["nipper", "--help"])

        assert result.exit_code == 0
        mock_check_update.assert_called_once()
        from tests.conftest import assert_rich_help_output

        assert_rich_help_output(result.output, "Process a Nipper CSV file")
