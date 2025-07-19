from pathlib import Path
from typing import TYPE_CHECKING, Any

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
from kp_analysis_toolkit.core.containers.application import container
from kp_analysis_toolkit.models.enums import FileSelectionResult
from kp_analysis_toolkit.nipper_expander import __version__ as nipper_expander_version
from kp_analysis_toolkit.nipper_expander.container import (
    container as nipper_container,
)
from kp_analysis_toolkit.nipper_expander.container import (
    wire_nipper_expander_container,
)
from kp_analysis_toolkit.nipper_expander.models.program_config import ProgramConfig
from kp_analysis_toolkit.nipper_expander.protocols import NipperExpanderService

if TYPE_CHECKING:
    from kp_analysis_toolkit.core.services.rich_output import RichOutputService

# Configure option groups for this command
# Note: Rich-click option grouping currently doesn't work with multi-command CLI structures
setup_command_option_groups("nipper")

# Instantiate the Nipper service and wire the Nipper Expander container
nipper_service: NipperExpanderService = nipper_container.nipper_expander_service()
wire_nipper_expander_container()


@custom_help_option("nipper")
@click.command(name="nipper")
@module_version_option(nipper_expander_version, "nipper")
@input_file_option(file_type="CSV")
@start_directory_option()
def process_command_line(_infile: str, source_files_path: str) -> None:
    """Process a Nipper CSV file and expand it into a more readable format."""
    rich_output: RichOutputService = container.core.rich_output()

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
        _process_all_csv_files(file_list)
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


def _process_all_csv_files(file_list: list[Path]) -> None:
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

    # Process files using the utility
    process_files_with_config(
        file_list=file_list,
        config_creator=_create_nipper_config,
        processor=nipper_service.process_nipper_csv,
        config=batch_config,
    )
