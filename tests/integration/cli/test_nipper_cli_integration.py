"""Tests for nipper_expander CLI functionality."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from kp_analysis_toolkit.cli.commands.nipper import process_command_line


class TestNipperExpanderCLI:
    """Test nipper_expander CLI functionality."""

    def test_cli_with_explicit_file(self, cli_runner: CliRunner) -> None:
        """Test CLI with explicitly specified input file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a test CSV file
            test_csv = Path(temp_dir) / "test.csv"
            test_csv.write_text(
                "column1,Devices,column3\nvalue1,device1;device2,value3\n",
            )

            # Using shared cli_runner fixture

            with patch(
                "kp_analysis_toolkit.cli.commands.nipper.process_nipper_csv",
            ) as mock_process:
                result = cli_runner.invoke(
                    process_command_line,
                    [
                        "--in-file",
                        str(test_csv),
                        "--start-dir",
                        temp_dir,
                    ],
                )

                assert result.exit_code == 0
                mock_process.assert_called_once()

    def test_cli_auto_discovery(self, cli_runner: CliRunner) -> None:
        """Test CLI with automatic CSV file discovery."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a test CSV file
            test_csv = Path(temp_dir) / "nipper_output.csv"
            test_csv.write_text(
                "column1,Devices,column3\nvalue1,device1;device2,value3\n",
            )

            # Using shared cli_runner fixture

            with (
                patch(
                    "kp_analysis_toolkit.cli.commands.nipper.process_nipper_csv",
                ) as mock_process,
                patch(
                    "kp_analysis_toolkit.cli.commands.nipper.get_input_file",
                    return_value=test_csv,
                ) as mock_get_file,
            ):
                result = cli_runner.invoke(
                    process_command_line,
                    [
                        "--start-dir",
                        temp_dir,
                    ],
                )

                assert result.exit_code == 0
                mock_process.assert_called_once()
                mock_get_file.assert_called_once()

    def test_cli_no_csv_files_found(self, cli_runner: CliRunner) -> None:
        """Test CLI behavior when no CSV files are found."""
        with (
            tempfile.TemporaryDirectory() as temp_dir,
            patch(
                "kp_analysis_toolkit.cli.commands.nipper.get_input_file",
            ) as mock_get_file,
        ):
            # Directory with no CSV files
            mock_get_file.side_effect = ValueError("No CSV files found")

            result = cli_runner.invoke(
                process_command_line,
                [
                    "--start-dir",
                    temp_dir,
                ],
            )

            assert result.exit_code == 1  # CLI should exit with error code
            assert "File selection failed: No CSV files found" in result.output

    def test_cli_invalid_input_file(self, cli_runner: CliRunner) -> None:
        """Test CLI behavior with invalid input file."""
        # Using shared cli_runner fixture

        with patch(
            "kp_analysis_toolkit.cli.commands.nipper.get_input_file",
        ) as mock_get_file:
            mock_get_file.side_effect = ValueError("Invalid file specified")

            result = cli_runner.invoke(
                process_command_line,
                [
                    "--in-file",
                    "/nonexistent/file.csv",
                ],
            )

            assert "File selection failed: Invalid file specified" in result.output

    def test_cli_with_custom_start_directory(self, cli_runner: CliRunner) -> None:
        """Test CLI with custom start directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            subdir = Path(temp_dir) / "subdir"
            subdir.mkdir()

            # Create CSV in subdirectory
            test_csv = subdir / "test.csv"
            test_csv.write_text("column1,Devices,column3\nvalue1,device1,value3\n")

            # Using shared cli_runner fixture

            with (
                patch(
                    "kp_analysis_toolkit.cli.commands.nipper.process_nipper_csv",
                ) as mock_process,
                patch(
                    "kp_analysis_toolkit.cli.commands.nipper.get_input_file",
                    return_value=test_csv,
                ) as mock_get_file,
            ):
                result = cli_runner.invoke(
                    process_command_line,
                    [
                        "--start-dir",
                        str(subdir),
                    ],
                )

                assert result.exit_code == 0
                mock_process.assert_called_once()
                mock_get_file.assert_called_once()

    @patch("kp_analysis_toolkit.cli.commands.nipper.process_nipper_csv")
    def test_program_config_creation(
        self,
        mock_process: MagicMock,
        cli_runner: CliRunner,
    ) -> None:
        """Test that ProgramConfig is created correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_csv = Path(temp_dir) / "test.csv"
            test_csv.write_text("Devices\ndevice1;device2\n")

            # Using shared cli_runner fixture

            result = cli_runner.invoke(
                process_command_line,
                [
                    "--in-file",
                    str(test_csv),
                    "--start-dir",
                    temp_dir,
                ],
            )

            assert result.exit_code == 0

            # Verify process_nipper_csv was called with correct config
            mock_process.assert_called_once()
            program_config = mock_process.call_args[0][0]

            # Check that the config has expected attributes
            assert hasattr(program_config, "input_file")
            assert hasattr(program_config, "source_files_path")

    def test_cli_help_output(self, cli_runner: CliRunner) -> None:
        """Test CLI help output."""
        # Using shared cli_runner fixture

        result = cli_runner.invoke(process_command_line, ["--help"])

        assert result.exit_code == 0
        assert "Process a Nipper CSV file" in result.output
        assert "--in-file" in result.output
        assert "--start-dir" in result.output

    def test_cli_version_output(self, cli_runner: CliRunner) -> None:
        """Test CLI version output."""
        # Using shared cli_runner fixture

        result = cli_runner.invoke(process_command_line, ["--version"])

        assert result.exit_code == 0
        assert "version" in result.output

    @patch("kp_analysis_toolkit.cli.commands.nipper.process_nipper_csv")
    def test_processing_success_message(
        self,
        mock_process: MagicMock,
        cli_runner: CliRunner,
    ) -> None:
        """Test success message is displayed."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_csv = Path(temp_dir) / "test.csv"
            test_csv.write_text("Devices\ndevice1\n")

            # Using shared cli_runner fixture

            result = cli_runner.invoke(
                process_command_line,
                [
                    "--in-file",
                    str(test_csv),
                ],
            )

            assert result.exit_code == 0
            assert "Processing Nipper CSV file" in result.output
            mock_process.assert_called_once()

    def test_error_handling_in_processing(self, cli_runner: CliRunner) -> None:
        """Test error handling during CSV processing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_csv = Path(temp_dir) / "test.csv"
            test_csv.write_text("Devices\ndevice1\n")

            # Using shared cli_runner fixture

            with patch(
                "kp_analysis_toolkit.cli.commands.nipper.process_nipper_csv",
            ) as mock_process:
                mock_process.side_effect = Exception("Processing failed")

                result = cli_runner.invoke(
                    process_command_line,
                    [
                        "--in-file",
                        str(test_csv),
                    ],
                )

                # CLI should handle exceptions gracefully
                # The exact behavior depends on implementation
                assert result.exit_code != 0  # Should exit with error
                mock_process.assert_called_once()


class TestGetInputFileFunction:
    """Test the get_input_file helper function."""

    @patch("kp_analysis_toolkit.cli.commands.nipper.get_input_file")
    def test_explicit_file_parameter(
        self,
        mock_get_file: MagicMock,
        cli_runner: CliRunner,
    ) -> None:
        """Test get_input_file with explicit file parameter."""
        mock_get_file.return_value = Path("/test/file.csv")

        with tempfile.TemporaryDirectory() as temp_dir:
            test_csv = Path(temp_dir) / "test.csv"
            test_csv.write_text("Devices\ndevice1\n")

            with patch(
                "kp_analysis_toolkit.cli.commands.nipper.process_nipper_csv",
            ) as mock_process:
                result = cli_runner.invoke(
                    process_command_line,
                    [
                        "--in-file",
                        str(test_csv),
                    ],
                )

                # Verify the command executed successfully
                assert result.exit_code == 0
                mock_get_file.assert_called_once()
                mock_process.assert_called_once()

    @patch("kp_analysis_toolkit.cli.commands.nipper.get_input_file")
    def test_auto_discovery_mode(
        self,
        mock_get_file: MagicMock,
        cli_runner: CliRunner,
    ) -> None:
        """Test get_input_file with auto-discovery mode."""
        mock_get_file.return_value = Path("/discovered/file.csv")

        with (
            tempfile.TemporaryDirectory() as temp_dir,
            patch(
                "kp_analysis_toolkit.cli.commands.nipper.process_nipper_csv",
            ) as mock_process,
        ):
            result = cli_runner.invoke(
                process_command_line,
                [
                    "--start-dir",
                    temp_dir,
                ],
            )

            # Verify the command executed successfully
            assert result.exit_code == 0
            mock_get_file.assert_called_once()
            mock_process.assert_called_once()


class TestCLIIntegration:
    """Test CLI integration scenarios."""

    def test_end_to_end_processing(self, cli_runner: CliRunner) -> None:
        """Test complete end-to-end processing workflow."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create realistic test CSV
            test_csv = Path(temp_dir) / "nipper_test.csv"
            csv_content = """Issue Title,Devices,Rating,Finding,Impact,Ease,Recommendation
High Risk Finding,router1;switch1;firewall1,High,Security vulnerability finding,High security impact,Easy to exploit,Apply security patch
Medium Risk Finding,router2;switch2,Medium,Configuration issue finding,Medium impact,Moderate effort,Update configuration
Low Risk Finding,switch3,Low,Minor issue finding,Low impact,High effort,Monitor and review"""
            test_csv.write_text(csv_content)

            # Using shared cli_runner fixture

            # Mock the actual processing to avoid file system operations
            with (
                patch(
                    "kp_analysis_toolkit.cli.commands.nipper.process_nipper_csv",
                ) as mock_process,
                patch(
                    "kp_analysis_toolkit.cli.commands.nipper.ProgramConfig",
                ) as mock_config_class,
            ):
                # Create a mock config instance
                mock_config = MagicMock()
                mock_config.input_file = test_csv
                mock_config.source_files_path = temp_dir
                mock_config.output_file = Path(temp_dir) / "nipper_test_expanded.xlsx"
                mock_config_class.return_value = mock_config

                result = cli_runner.invoke(
                    process_command_line,
                    [
                        "--in-file",
                        str(test_csv),
                        "--start-dir",
                        temp_dir,
                    ],
                )

                assert result.exit_code == 0
                mock_process.assert_called_once()

                # Verify the program config passed to processing
                config = mock_process.call_args[0][0]
                assert config == mock_config

    def test_multiple_csv_files_discovery(self, cli_runner: CliRunner) -> None:
        """Test behavior when multiple CSV files exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create multiple CSV files
            csv1 = Path(temp_dir) / "file1.csv"
            csv2 = Path(temp_dir) / "file2.csv"
            csv1.write_text("Devices\ndevice1\n")
            csv2.write_text("Devices\ndevice2\n")

            # Using shared cli_runner fixture

            with patch(
                "kp_analysis_toolkit.cli.commands.nipper.get_input_file",
            ) as mock_get_file:
                # Should handle multiple files scenario
                mock_get_file.return_value = csv1

                with patch(
                    "kp_analysis_toolkit.cli.commands.nipper.process_nipper_csv",
                ) as mock_process:
                    result = cli_runner.invoke(
                        process_command_line,
                        [
                            "--start-dir",
                            temp_dir,
                        ],
                    )

                    # Verify the command executed successfully
                    assert result.exit_code == 0
                    mock_get_file.assert_called_once()
                    mock_process.assert_called_once()

    def test_relative_path_handling(self, cli_runner: CliRunner) -> None:
        """Test handling of relative paths."""
        # Using shared cli_runner fixture

        with (
            patch(
                "kp_analysis_toolkit.cli.commands.nipper.get_input_file",
            ) as mock_get_file,
            patch(
                "kp_analysis_toolkit.cli.commands.nipper.process_nipper_csv",
            ) as mock_process,
        ):
            mock_get_file.return_value = Path("./test.csv")

            result = cli_runner.invoke(
                process_command_line,
                [
                    "--start-dir",
                    "./",
                ],
            )

            # Should handle relative paths appropriately
            assert result.exit_code == 0
            mock_get_file.assert_called_once()
            mock_process.assert_called_once()

    def test_error_recovery(self, cli_runner: CliRunner) -> None:
        """Test error recovery and user feedback."""
        # Using shared cli_runner fixture

        # Test with nonexistent file - this should trigger a processing error, not config error
        result = cli_runner.invoke(
            process_command_line,
            [
                "--in-file",
                "nonexistent.csv",
            ],
        )

        assert "Error processing CSV file" in result.output
        assert result.exit_code == 1


class TestCLIParameterValidation:
    """Test CLI parameter validation."""

    def test_valid_parameters(self, cli_runner: CliRunner) -> None:
        """Test that valid parameters are accepted."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_csv = Path(temp_dir) / "test.csv"
            test_csv.write_text("Devices\ndevice1\n")

            # Using shared cli_runner fixture

            with patch("kp_analysis_toolkit.cli.commands.nipper.process_nipper_csv"):
                result = cli_runner.invoke(
                    process_command_line,
                    [
                        "--in-file",
                        str(test_csv),
                        "--start-dir",
                        temp_dir,
                    ],
                )

                assert result.exit_code == 0

    def test_default_parameters(self, cli_runner: CliRunner) -> None:
        """Test default parameter behavior."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create CSV in current directory simulation
            test_csv = Path(temp_dir) / "test.csv"
            test_csv.write_text("Devices\ndevice1\n")

            # Using shared cli_runner fixture

            with (
                patch(
                    "kp_analysis_toolkit.cli.commands.nipper.get_input_file",
                ) as mock_get_file,
                patch("kp_analysis_toolkit.cli.commands.nipper.process_nipper_csv"),
            ):
                mock_get_file.return_value = test_csv

                # Test with minimal parameters (should use defaults)
                result = cli_runner.invoke(process_command_line, [])

                assert result.exit_code == 0
                mock_get_file.assert_called_once_with(
                    None,
                    "./",
                    file_pattern="*.csv",
                    file_type_description="CSV",
                    include_process_all_option=True,
                )
