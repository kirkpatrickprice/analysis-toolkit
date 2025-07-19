from pathlib import Path
from typing import Any

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
from kp_analysis_toolkit.core.services.rich_output import RichOutputService
from kp_analysis_toolkit.models.enums import FileSelectionResult
from kp_analysis_toolkit.nipper_expander import __version__ as nipper_expander_version
from kp_analysis_toolkit.nipper_expander.models.program_config import ProgramConfig
from kp_analysis_toolkit.nipper_expander.protocols import NipperExpanderService

# Configure option groups for this command
# Note: Rich-click option grouping currently doesn't work with multi-command CLI structures
setup_command_option_groups("nipper")


@custom_help_option("nipper")
@click.command(name="nipper")
@module_version_option(nipper_expander_version, "nipper")
@input_file_option(file_type="CSV")
@start_directory_option()
@inject
def process_command_line(
    _infile: str,
    source_files_path: str,
    rich_output: RichOutputService = Provide[ApplicationContainer.core.rich_output],
    nipper_service: NipperExpanderService = Provide[
        ApplicationContainer.nipper.nipper_expander_service,
    ],
) -> None:
    """Process a Nipper CSV file and expand it into a more readable format."""
    # Get input file or determine if processing all files
    try:
        selected_file: Path | FileSelectionResult = get_input_file(
            _infile,
            source_files_path,
            file_pattern="*.csv",
            file_type_description="CSV",
            include_process_all_option=True,
        )
    except ValueError as e:
        handle_fatal_error(e, error_prefix="File selection failed")

    # If user chose "process all files"
    if selected_file == FileSelectionResult.PROCESS_ALL_FILES:
        file_list: list[Path] = discover_files_by_pattern(source_files_path, "*.csv")
        _process_all_csv_files(file_list, nipper_service=nipper_service)
        return

    # Single file processing (existing logic)
    try:
        program_config: ProgramConfig = validate_program_config(
            ProgramConfig,
            input_file=selected_file,
            source_files_path=source_files_path,
        )
    except ValueError as e:
        handle_fatal_error(e, error_prefix="Configuration validation failed")

    rich_output.info(f"Processing Nipper CSV file: {program_config.input_file!s}")

    try:
        nipper_service.process_nipper_csv(
            input_path=program_config.input_file,
            output_path=program_config.output_file,
        )

        rich_output.success(
            f"Processed {program_config.input_file} and saved results to {program_config.output_file}",
        )
    except (ValueError, FileNotFoundError, KeyError) as e:
        handle_fatal_error(e, error_prefix="Error processing CSV file")


def _create_nipper_config(file_path: Path) -> ProgramConfig:
    """Create Nipper configuration for a file."""
    return validate_program_config(
        ProgramConfig,
        input_file=file_path,
        source_files_path=file_path.parent,
    )


def _process_all_csv_files(
    file_list: list[Path],
    nipper_service: NipperExpanderService,
) -> None:
    """Process all CSV files in the list using the batch processing utility."""
    from kp_analysis_toolkit.cli.utils.batch_processing import (
        BatchProcessingConfig,
        ErrorHandlingStrategy,
        process_files_with_config,
    )

    def format_nipper_success(file_path: Path, result: tuple[Any, Any]) -> str:
        """Format success message for Nipper processing."""
        program_config, _ = result
        return f"Processed: {file_path.name} -> {program_config.output_file.name}"

    # Configure batch processing
    batch_config = BatchProcessingConfig(
        operation_description="Processing Nipper CSV files",
        progress_description="Processing CSV files...",
        error_handling=ErrorHandlingStrategy.CONTINUE_ON_ERROR,
        success_message_formatter=format_nipper_success,
    )

    def processor_wrapper(program_config: ProgramConfig) -> tuple[ProgramConfig, None]:
        """Wrapper to use the DI service with batch processing."""
        return _process_single_file_with_service(program_config, nipper_service)

    # Process files using the utility
    process_files_with_config(
        file_list=file_list,
        config_creator=_create_nipper_config,
        processor=processor_wrapper,
        config=batch_config,
    )


def _process_single_file_with_service(
    program_config: ProgramConfig,
    nipper_service: NipperExpanderService,
) -> tuple[ProgramConfig, None]:
    """Process a single file using the nipper service."""
    # AI-GEN: claude-3.5-sonnet|2024-12-31|function-signature-mismatch|reviewed:no
    from pathlib import Path
    from typing import cast

    input_file: Path = cast("Path", program_config.input_file)
    output_file: Path = cast("Path", program_config.output_file)
    nipper_service.process_nipper_csv(input_file, output_file)
    return (program_config, None)
    # END AI-GEN
