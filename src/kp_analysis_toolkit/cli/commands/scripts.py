# AI-GEN: CopilotChat|2025-07-31|KPAT-ListSystems|reviewed:no
"""CLI command for process scripts functionality."""

from typing import TYPE_CHECKING, Any

import rich_click as click

from kp_analysis_toolkit.cli.common.config_validation import (
    handle_fatal_error,
    validate_program_config,
)
from kp_analysis_toolkit.cli.common.decorators import (
    custom_help_option,
    module_version_option,
    start_directory_option,
    verbose_option,
)
from kp_analysis_toolkit.cli.common.option_groups import setup_command_option_groups
from kp_analysis_toolkit.cli.common.output_formatting import (
    create_list_command_header,
    display_list_summary,
    format_hash_display,
    format_verbose_details,
    handle_empty_list_result,
)
from kp_analysis_toolkit.cli.utils.table_layouts import (
    create_system_info_table,
)
from kp_analysis_toolkit.core.containers.application import container
from kp_analysis_toolkit.process_scripts import (
    __version__ as process_scripts_version,
)
from kp_analysis_toolkit.process_scripts.models.program_config import ProgramConfig

if TYPE_CHECKING:
    from kp_analysis_toolkit.core.services.rich_output import RichOutputService

# Configure option groups for this command
setup_command_option_groups("scripts")


@custom_help_option("scripts")
@click.command(name="scripts")
@module_version_option(process_scripts_version, "scripts")
@start_directory_option()
@verbose_option()
@click.option(
    "source_files_spec",
    "--filespec",
    "-f",
    default="*.txt",
    help="Default: *.txt. Specify the file specification to match. This can be a glob pattern.",
)
@click.option(
    "--list-systems",
    help="Print system details found in FILESPEC and then exit",
    is_flag=True,
)
def process_command_line(**cli_config: dict[str, Any]) -> None:
    """Process collector script results files (formerly adv-searchfor)."""
    # Add default out_path for list-systems since it's not needed
    if cli_config.get("list_systems", False) and "out_path" not in cli_config:
        cli_config["out_path"] = "dummy_output.xlsx"  # Not used for list-systems
    
    # Convert the click config to a ProgramConfig object and perform validation
    try:
        program_config = validate_program_config(ProgramConfig, **cli_config)
    except ValueError as e:
        handle_fatal_error(e, error_prefix="Configuration validation failed")

    # Echo the program configuration to the screen
    if program_config.verbose:
        print_verbose_config(cli_config, program_config)

    # List all discovered systems
    if program_config.list_systems:
        list_systems(program_config)
        return

    # For now, just show a message that other functionality is not implemented
    rich_output: RichOutputService = container.core.rich_output()
    rich_output.info(
        "Full process scripts functionality not yet implemented. Use --list-systems to see available systems."
    )


def list_systems(program_config: ProgramConfig) -> None:
    """List all systems found in the specified source files."""
    rich_output: RichOutputService = container.core.rich_output()
    create_list_command_header(rich_output, "Systems Found")

    # Get the process scripts service from the container
    process_scripts_service = container.process_scripts().process_scripts_service()

    # Discover and analyze systems
    systems = process_scripts_service.list_systems(
        input_directory=program_config.source_files_path,
        file_pattern=program_config.source_files_spec,
    )

    if not systems:
        handle_empty_list_result(rich_output, "systems")
        return

    # Create a Rich table for systems using the centralized utility
    table = create_system_info_table(
        rich_output,
        title="🖥️ Systems",
        include_details=program_config.verbose,
    )

    if table is None:  # Quiet mode
        return

    max_detail_fields = 5  # Limit displayed details in verbose mode

    for system in systems:
        row_data = [system.system_name, format_hash_display(system.file_hash or "")]

        if program_config.verbose:
            # Create details string for verbose mode with excluded fields
            system_data = system.model_dump()
            filtered_data = {
                k: v
                for k, v in system_data.items()
                if k not in ["system_name", "file_hash"]
            }
            details_text = format_verbose_details(
                rich_output,
                filtered_data,
                max_items=max_detail_fields,
                max_value_length=60,
            )
            row_data.append(details_text)

        table.add_row(*row_data)

    rich_output.display_table(table)
    display_list_summary(rich_output, len(systems), "systems")


def print_verbose_config(
    cli_config: dict[str, Any],
    program_config: ProgramConfig,
) -> None:
    """Print the program configuration in verbose mode using Rich formatting."""
    rich_output: RichOutputService = container.core.rich_output()

    # Display configuration using Rich
    rich_output.configuration_table(
        config_dict=dict(program_config.to_dict()),
        original_dict=cli_config,
        title="Program Configuration",
        force=True,
    )


# END AI-GEN
