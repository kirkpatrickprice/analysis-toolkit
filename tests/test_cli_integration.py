"""Integration tests for the CLI with version checking."""

from unittest.mock import Mock, patch

from click.testing import CliRunner

from kp_analysis_toolkit.cli import cli


class TestCLIVersionChecking:
    """Integration tests for CLI version checking functionality."""

    def test_cli_with_skip_update_check(self) -> None:
        """Test CLI with --skip-update-check flag shows help correctly."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--skip-update-check", "--help"])

        assert result.exit_code == 0
        assert "Command line interface for the KP Analysis Toolkit" in result.output
        assert "--skip-update-check" in result.output

    @patch("kp_analysis_toolkit.cli.check_and_prompt_update")
    def test_cli_calls_version_check_by_default(self, mock_check_update: Mock) -> None:
        """Test that CLI calls version check by default when invoked without subcommand."""
        runner = CliRunner()
        result = runner.invoke(cli, [])

        assert result.exit_code == 0
        mock_check_update.assert_called_once()

    @patch("kp_analysis_toolkit.cli.check_and_prompt_update")
    def test_cli_skips_version_check_when_flag_set(
        self,
        mock_check_update: Mock,
    ) -> None:
        """Test that CLI skips version check when flag is set."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--skip-update-check"])

        assert result.exit_code == 0
        mock_check_update.assert_not_called()

    @patch("kp_analysis_toolkit.cli.check_and_prompt_update")
    def test_cli_help_does_not_trigger_version_check(self, mock_check_update: Mock) -> None:
        """Test that --help does not trigger version check (Click special handling)."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "Command line interface for the KP Analysis Toolkit" in result.output
        assert "--skip-update-check" in result.output
        # Help is handled specially by Click and doesn't invoke the group callback
        mock_check_update.assert_not_called()

    def test_cli_version_option_still_works(self) -> None:
        """Test that the --version option still works correctly."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])

        assert result.exit_code == 0
        assert "kpat_cli version" in result.output

    @patch("kp_analysis_toolkit.cli.check_and_prompt_update")
    def test_subcommands_trigger_version_check(self, mock_check_update: Mock) -> None:
        """Test that accessing subcommands also triggers version check."""
        runner = CliRunner()
        result = runner.invoke(cli, ["scripts", "--help"])

        assert result.exit_code == 0
        mock_check_update.assert_called_once()
        assert "Process collector script results files" in result.output

    @patch("kp_analysis_toolkit.cli.check_and_prompt_update")
    def test_nipper_subcommand_triggers_version_check(
        self,
        mock_check_update: Mock,
    ) -> None:
        """Test that the nipper subcommand also triggers version check."""
        runner = CliRunner()
        result = runner.invoke(cli, ["nipper", "--help"])

        assert result.exit_code == 0
        mock_check_update.assert_called_once()
        assert "Process a Nipper CSV file" in result.output
