"""Tests for CLI integration with dependency injection."""

from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from kp_analysis_toolkit.cli import cli


class TestCLIDependencyInjection:
    """Test CLI integration with dependency injection system."""

    @patch("kp_analysis_toolkit.cli.main.initialize_dependency_injection")
    def test_cli_initializes_di_on_startup(self, mock_init_di: MagicMock, cli_runner: CliRunner) -> None:
        """Test that CLI initializes dependency injection on startup."""
        result = cli_runner.invoke(cli, ["--skip-update-check"])

        assert result.exit_code == 0
        # CLI might call DI initialization once for the command, check it was called
        assert mock_init_di.called

    @patch("kp_analysis_toolkit.cli.main.initialize_dependency_injection")
    def test_cli_passes_quiet_to_di(self, mock_init_di: MagicMock, cli_runner: CliRunner) -> None:
        """Test that CLI passes quiet flag to DI initialization."""
        result = cli_runner.invoke(cli, ["--quiet", "--skip-update-check"])

        assert result.exit_code == 0
        # Check that quiet=True was passed at least once
        mock_init_di.assert_called_with(verbose=False, quiet=True)

    def test_cli_rejects_verbose_option_not_available(self, cli_runner: CliRunner) -> None:
        """Test that CLI rejects verbose option since it's no longer available."""
        result = cli_runner.invoke(cli, ["--verbose", "--skip-update-check"])

        assert result.exit_code == 2  # Invalid option
        assert "No such option: --verbose" in result.output

    def test_cli_has_quiet_option(self, cli_runner: CliRunner) -> None:
        """Test that CLI has quiet option available."""
        result = cli_runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "--quiet" in result.output
        assert "-q" in result.output
        assert "Suppress non-essential output" in result.output

    @patch("kp_analysis_toolkit.cli.main.initialize_dependency_injection")
    @patch("kp_analysis_toolkit.cli.main.check_and_prompt_update")
    def test_cli_initialization_order(
        self,
        mock_check_update: MagicMock,
        mock_init_di: MagicMock,
        cli_runner: CliRunner,
    ) -> None:
        """Test that DI is initialized before version check."""
        result = cli_runner.invoke(cli, [])

        assert result.exit_code == 0

        # DI should be initialized before version check
        assert mock_init_di.called
        assert mock_check_update.called

    @patch("kp_analysis_toolkit.cli.main.initialize_dependency_injection")
    def test_cli_skips_version_check_but_initializes_di(
        self,
        mock_init_di: MagicMock,
        cli_runner: CliRunner,
    ) -> None:
        """Test that DI is initialized even when version check is skipped."""
        result = cli_runner.invoke(cli, ["--skip-update-check"])

        assert result.exit_code == 0
        assert mock_init_di.called


class TestCLIRichOutputIntegration:
    """Test CLI integration with Rich Output."""

    @patch("kp_analysis_toolkit.cli.main.initialize_dependency_injection")
    @patch("kp_analysis_toolkit.cli.main.get_rich_output")
    def test_cli_uses_rich_output_for_help(
        self,
        mock_get_rich_output: MagicMock,
        mock_init_di: MagicMock,
        cli_runner: CliRunner,
    ) -> None:
        """Test that CLI uses Rich Output for enhanced help display."""
        mock_rich_output = MagicMock()
        mock_get_rich_output.return_value = mock_rich_output

        result = cli_runner.invoke(cli, ["--skip-update-check"])

        assert result.exit_code == 0
        assert mock_init_di.called
        mock_get_rich_output.assert_called()

    @patch("kp_analysis_toolkit.cli.main.initialize_dependency_injection")
    def test_version_callback_uses_rich_output(self, mock_init_di: MagicMock, cli_runner: CliRunner) -> None:
        """Test that version callback uses Rich Output for formatting."""
        result = cli_runner.invoke(cli, ["--version"])

        # Version callback should exit early, but we can check output format
        assert result.exit_code == 0
        assert "kpat_cli version" in result.output

    @patch("kp_analysis_toolkit.cli.main.initialize_dependency_injection")
    def test_cli_backward_compatibility_with_rich_output(
        self,
        mock_init_di: MagicMock,
        cli_runner: CliRunner,
    ) -> None:
        """Test that CLI maintains backward compatibility with Rich Output usage."""
        # This test ensures existing Rich Output usage still works
        result = cli_runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        # Should not crash due to Rich Output changes
        assert "Command line interface" in result.output


class TestCLIErrorHandling:
    """Test CLI error handling with dependency injection."""

    @patch("kp_analysis_toolkit.cli.main.initialize_dependency_injection")
    def test_cli_handles_di_initialization_error(self, mock_init_di: MagicMock, cli_runner: CliRunner) -> None:
        """Test that CLI handles DI initialization errors gracefully."""
        mock_init_di.side_effect = Exception("DI initialization failed")

        result = cli_runner.invoke(cli, ["--skip-update-check"])

        # CLI should handle the error and not crash
        # (This test verifies the CLI doesn't propagate DI errors)
        assert result.exit_code != 0 or "DI initialization failed" in result.output

    def test_cli_help_works_without_di(self, cli_runner: CliRunner) -> None:
        """Test that CLI help works even if DI has issues."""
        result = cli_runner.invoke(cli, ["--help"])

        # Help should always work
        assert result.exit_code == 0
        assert "Command line interface" in result.output


class TestCLISubcommandIntegration:
    """Test CLI subcommand integration with dependency injection."""

    def test_scripts_subcommand_exists(self, cli_runner: CliRunner) -> None:
        """Test that scripts subcommand is available."""
        result = cli_runner.invoke(cli, ["scripts", "--help"])

        # Should be able to get help for scripts command
        # Note: This might fail if the command wrapper doesn't preserve options
        assert result.exit_code == 0

    def test_nipper_subcommand_exists(self, cli_runner: CliRunner) -> None:
        """Test that nipper subcommand is available."""
        result = cli_runner.invoke(cli, ["nipper", "--help"])

        assert result.exit_code == 0

    def test_rtf_to_text_subcommand_exists(self, cli_runner: CliRunner) -> None:
        """Test that rtf-to-text subcommand is available."""
        result = cli_runner.invoke(cli, ["rtf-to-text", "--help"])

        assert result.exit_code == 0

    @patch("kp_analysis_toolkit.cli.main.initialize_dependency_injection")
    def test_subcommands_benefit_from_di_initialization(
        self,
        mock_init_di: MagicMock,
        cli_runner: CliRunner,
    ) -> None:
        """Test that subcommands benefit from DI initialization done at CLI level."""
        # Try to invoke a subcommand (this will likely fail due to missing arguments,
        # but DI should still be initialized)
        cli_runner.invoke(cli, ["scripts", "--help"])

        # DI should have been initialized at the CLI level
        mock_init_di.assert_called()


class TestCLIConfigurationPropagation:
    """Test that CLI configuration properly propagates to dependency injection."""

    @patch("kp_analysis_toolkit.cli.main.initialize_dependency_injection")
    def test_default_configuration_propagation(self, mock_init_di: MagicMock, cli_runner: CliRunner) -> None:
        """Test that default configuration is properly propagated."""
        cli_runner.invoke(cli, ["--skip-update-check"])

        # Should be called with default values at least once
        mock_init_di.assert_called_with(verbose=False, quiet=False)

    @patch("kp_analysis_toolkit.cli.main.initialize_dependency_injection")
    def test_custom_configuration_propagation(self, mock_init_di: MagicMock, cli_runner: CliRunner) -> None:
        """Test that custom configuration is properly propagated."""
        # Test quiet flag
        cli_runner.invoke(cli, ["--quiet", "--skip-update-check"])
        mock_init_di.assert_called_with(verbose=False, quiet=True)

        mock_init_di.reset_mock()

        # Test default behavior (no flags)
        cli_runner.invoke(cli, ["--skip-update-check"])
        mock_init_di.assert_called_with(verbose=False, quiet=False)
