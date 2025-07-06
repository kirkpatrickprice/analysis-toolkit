from pathlib import Path

import rich_click as click

from kp_analysis_toolkit.cli.common.config_validation import (
    handle_fatal_error,
    validate_program_config,
)
from kp_analysis_toolkit.cli.common.file_selection import (
    get_all_files_matching_pattern,
    get_input_file,
)
from kp_analysis_toolkit.rtf_to_text import __version__ as rtf_to_text_version
from kp_analysis_toolkit.rtf_to_text.models.program_config import ProgramConfig
from kp_analysis_toolkit.rtf_to_text.process_rtf import process_rtf_file
from kp_analysis_toolkit.utils.rich_output import get_rich_output


@click.command(name="rtf-to-text")
@click.version_option(
    version=rtf_to_text_version,
    prog_name="kpat_cli rtf-to-text",
    message="%(prog)s version %(version)s",
)
@click.option(
    "_infile",
    "--in-file",
    "-f",
    default=None,
    help="Input RTF file to process. If not specified, will search the current directory for RTF files.",
)
@click.option(
    "source_files_path",
    "--start-dir",
    "-d",
    default="./",
    help="Default: the current working directory (./). Specify the path to start searching for files. Will walk the directory tree from this path.",
)
def process_command_line(_infile: str, source_files_path: str) -> None:
    """Convert RTF files to plain text format with ASCII encoding."""
    # Get the rich output console
    console = get_rich_output()

    # Get the input file using the enhanced common logic
    try:
        selected_file = get_input_file(
            _infile,
            source_files_path,
            file_pattern="*.rtf",
            file_type_description="RTF",
            include_process_all_option=True,
        )
    except ValueError as e:
        handle_fatal_error(e, error_prefix="Error finding input files")

    # Handle "process all files" case
    if selected_file is None:
        file_list = get_all_files_matching_pattern(source_files_path, "*.rtf")
        _process_all_files(file_list)
        return

    # Process single file
    try:
        program_config = validate_program_config(
            ProgramConfig,
            input_file=selected_file,
            source_files_path=source_files_path,
        )
    except ValueError as e:
        handle_fatal_error(e, error_prefix="Configuration validation failed")

    console.info(f"Converting RTF file: {program_config.input_file!s}")

    try:
        process_rtf_file(program_config)

        console.success(
            f"Converted {program_config.input_file} and saved results to {program_config.output_file}",
        )
    except (ValueError, FileNotFoundError, OSError) as e:
        handle_fatal_error(e, error_prefix="Error processing RTF file")


def _create_rtf_config(file_path: Path) -> ProgramConfig:
    """
    Create RTF program config with validation.

    Args:
        file_path: Path to the RTF file to process

    Returns:
        Validated ProgramConfig object

    Raises:
        ValueError: If configuration validation fails

    """
    return validate_program_config(
        ProgramConfig,
        input_file=file_path,
        source_files_path=file_path.parent,
    )


def _process_all_files(file_list: list[Path]) -> None:
    """Process all RTF files in the list."""
    console = get_rich_output()

    total_files = len(file_list)
    successful = 0
    failed = 0

    console.info(f"Processing {total_files} RTF files...")

    # Create progress bar
    with console.progress() as progress:
        task = progress.add_task("Converting RTF files...", total=total_files)

        for file_path in file_list:
            try:
                program_config = _create_rtf_config(file_path)
                process_rtf_file(program_config)
                console.success(
                    f"Converted: {file_path.name} -> {program_config.output_file.name}",
                )
                successful += 1
            except ValueError as e:
                console.error(f"Configuration error for {file_path.name}: {e}")
                failed += 1
            except (FileNotFoundError, OSError) as e:
                console.error(f"Failed to convert {file_path.name}: {e}")
                failed += 1

            progress.update(task, advance=1)

    # Display summary
    console.info(f"Processing complete: {successful} successful, {failed} failed")
