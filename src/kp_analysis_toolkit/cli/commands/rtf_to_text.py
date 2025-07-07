from pathlib import Path

import rich_click as click

from kp_analysis_toolkit.cli.common.config_validation import (
    handle_fatal_error,
    validate_program_config,
)
from kp_analysis_toolkit.cli.common.decorators import (
    custom_help_option,
    input_file_option,
    module_version_option,
    start_directory_option,
)
from kp_analysis_toolkit.cli.common.file_selection import get_input_file
from kp_analysis_toolkit.cli.common.option_groups import setup_command_option_groups
from kp_analysis_toolkit.cli.utils.path_helpers import discover_files_by_pattern
from kp_analysis_toolkit.rtf_to_text import __version__ as rtf_to_text_version
from kp_analysis_toolkit.rtf_to_text.models.program_config import ProgramConfig
from kp_analysis_toolkit.rtf_to_text.process_rtf import process_rtf_file
from kp_analysis_toolkit.utils.rich_output import get_rich_output

# Configure option groups for this command
# Note: Rich-click option grouping currently doesn't work with multi-command CLI structures
setup_command_option_groups("rtf-to-text")


@custom_help_option("rtf-to-text")
@click.command(name="rtf-to-text")
@module_version_option(rtf_to_text_version, "rtf-to-text")
@input_file_option(file_type="RTF")
@start_directory_option()
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
        file_list = discover_files_by_pattern(source_files_path, "*.rtf")
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
    """Process all RTF files in the list using the batch processing utility."""
    from kp_analysis_toolkit.cli.utils.batch_processing import (
        BatchProcessingConfig,
        ErrorHandlingStrategy,
        process_files_with_config,
    )

    def format_rtf_success(file_path: Path, result: tuple) -> str:
        """Format success message for RTF conversion."""
        program_config, _ = result
        return f"Converted: {file_path.name} -> {program_config.output_file.name}"

    # Configure batch processing
    batch_config = BatchProcessingConfig(
        operation_description="Converting RTF files",
        progress_description="Converting RTF files...",
        error_handling=ErrorHandlingStrategy.CONTINUE_ON_ERROR,
        success_message_formatter=format_rtf_success,
    )

    # Process files using the batch processing utility
    process_files_with_config(
        file_list=file_list,
        config_creator=_create_rtf_config,
        processor=process_rtf_file,
        config=batch_config,
    )
