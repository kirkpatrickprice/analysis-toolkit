# AI-GEN: GitHub Copilot|2025-01-19|phase-2-nipper-refactoring|reviewed:yes
from pathlib import Path

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
from kp_analysis_toolkit.core.services.batch_processing import BatchProcessingService
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
    batch_service: BatchProcessingService = Provide[
        ApplicationContainer.core.batch_processing_service,
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
        _process_all_files_with_service(file_list, nipper_service, batch_service)
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
            program_config.input_file,
            program_config.output_file,
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


def _process_all_files_with_service(
    file_list: list[Path],
    nipper_service: NipperExpanderService,
    batch_service: BatchProcessingService,
) -> None:
    """Process all CSV files using the new BatchProcessingService."""
    from kp_analysis_toolkit.core.services.batch_processing.models import (
        BatchProcessingConfig,
        ErrorHandlingStrategy,
    )

    # Create success message formatter using the batch service
    success_formatter = batch_service.create_file_conversion_success_formatter(
        "Processed",
    )

    # Configure batch processing
    batch_config = BatchProcessingConfig(
        operation_description="Processing Nipper CSV files",
        progress_description="Processing CSV files...",
        error_handling=ErrorHandlingStrategy.CONTINUE_ON_ERROR,
        success_message_formatter=success_formatter,
    )

    # Process files using the core batch service
    batch_service.process_files_with_service(
        file_list=file_list,
        config_creator=_create_nipper_config,
        service_method=nipper_service.process_nipper_csv,
        config=batch_config,
    )


# END AI-GEN
