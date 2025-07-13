from pathlib import Path
from typing import Any, cast

import rich_click as click
from dependency_injector.wiring import Provide, inject

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
from kp_analysis_toolkit.core.containers.application import ApplicationContainer
from kp_analysis_toolkit.rtf_to_text import __version__ as rtf_to_text_version
from kp_analysis_toolkit.rtf_to_text.models.program_config import ProgramConfig
from kp_analysis_toolkit.rtf_to_text.service import RtfToTextService

# Configure option groups for this command
# Note: Rich-click option grouping currently doesn't work with multi-command CLI structures
setup_command_option_groups("rtf-to-text")


@custom_help_option("rtf-to-text")
@click.command(name="rtf-to-text")
@module_version_option(rtf_to_text_version, "rtf-to-text")
@input_file_option(file_type="RTF")
@start_directory_option()
@inject
def process_command_line(
    _infile: str,
    source_files_path: str,
    rtf_service: RtfToTextService = Provide[
        ApplicationContainer.rtf_to_text.rtf_to_text_service
    ],
) -> None:
    """Convert RTF files to plain text format with ASCII encoding."""
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
        _process_all_files_with_service(file_list, rtf_service)
        return

    # Process single file using DI service
    try:
        program_config = validate_program_config(
            ProgramConfig,
            input_file=selected_file,
            source_files_path=source_files_path,
        )
    except ValueError as e:
        handle_fatal_error(e, error_prefix="Configuration validation failed")

    try:
        # Pydantic validation ensures input_file is Path (not None) after validation
        input_file: Path = cast("Path", program_config.input_file)
        # Pydantic computed field returns Path, but mypy sees it as Callable
        output_file: Path = cast("Path", program_config.output_file)
        rtf_service.convert_file(input_file, output_file)
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


def _process_single_file_with_service(
    program_config: ProgramConfig,
    rtf_service: RtfToTextService,
) -> tuple[ProgramConfig, None]:
    """
    Process a single RTF file using the DI service.

    Args:
        program_config: Configuration for the RTF conversion
        rtf_service: The RTF to text service to use

    Returns:
        Tuple of (ProgramConfig, None) for compatibility with batch processing

    Raises:
        ValueError: If configuration validation fails
        FileNotFoundError: If input file doesn't exist
        OSError: If output file cannot be written

    """
    # Pydantic validation ensures input_file is Path (not None) after validation
    input_file: Path = cast("Path", program_config.input_file)
    # Pydantic computed field returns Path, but mypy sees it as Callable
    output_file: Path = cast("Path", program_config.output_file)
    rtf_service.convert_file(input_file, output_file)
    return (program_config, None)


def _process_all_files_with_service(
    file_list: list[Path],
    rtf_service: RtfToTextService,
) -> None:
    """Process all RTF files in the list using the DI service."""
    from kp_analysis_toolkit.cli.utils.batch_processing import (
        BatchProcessingConfig,
        ErrorHandlingStrategy,
        process_files_with_config,
    )

    def format_rtf_success(file_path: Path, result: tuple[Any, Any]) -> str:
        """Format success message for RTF conversion."""
        program_config, _ = result
        return f"Converted: {file_path.name} -> {program_config.output_file.name}"

    def processor_wrapper(program_config: ProgramConfig) -> tuple[ProgramConfig, None]:
        """Wrapper to use the DI service with batch processing."""
        return _process_single_file_with_service(program_config, rtf_service)

    # Configure batch processing
    batch_config = BatchProcessingConfig(
        operation_description="Converting RTF files",
        progress_description="Converting RTF files...",
        error_handling=ErrorHandlingStrategy.CONTINUE_ON_ERROR,
        success_message_formatter=format_rtf_success,
    )

    # Process files using the batch processing utility with DI service
    process_files_with_config(
        file_list=file_list,
        config_creator=_create_rtf_config,
        processor=processor_wrapper,
        config=batch_config,
    )
