from collections import defaultdict
from typing import TYPE_CHECKING, Any

import rich_click as click

from kp_analysis_toolkit.cli.common.config_validation import (
    handle_fatal_error,
    validate_program_config,
)
from kp_analysis_toolkit.cli.common.decorators import (
    module_version_option,
    output_directory_option,
    start_directory_option,
    verbose_option,
)
from kp_analysis_toolkit.cli.common.option_groups import setup_command_option_groups
from kp_analysis_toolkit.cli.utils.path_helpers import create_results_directory
from kp_analysis_toolkit.cli.utils.system_utils import get_file_size
from kp_analysis_toolkit.cli.utils.table_layouts import (
    create_file_listing_table,
    create_system_info_table,
)
from kp_analysis_toolkit.process_scripts import (
    __version__ as process_scripts_version,
)
from kp_analysis_toolkit.process_scripts import process_systems
from kp_analysis_toolkit.process_scripts.excel_exporter import (
    export_search_results_to_excel,
)
from kp_analysis_toolkit.process_scripts.models.enums import OSFamilyType, SysFilterAttr
from kp_analysis_toolkit.process_scripts.models.program_config import ProgramConfig
from kp_analysis_toolkit.process_scripts.models.search.base import SearchConfig
from kp_analysis_toolkit.process_scripts.search_engine import (
    execute_search,
    load_search_configs,
    load_yaml_config,
)
from kp_analysis_toolkit.utils.get_timestamp import get_timestamp
from kp_analysis_toolkit.utils.rich_output import RichOutput, get_rich_output

if TYPE_CHECKING:
    from pathlib import Path

    from kp_analysis_toolkit.process_scripts.models.results.base import (
        SearchResult,
        SearchResults,
    )
    from kp_analysis_toolkit.process_scripts.models.systems import Systems

# Configure option groups for this command
# Note: Rich-click option grouping currently doesn't work with multi-command CLI structures
# This configuration is ready for future use when the issue is resolved
setup_command_option_groups("scripts")


@click.command(name="scripts")
@module_version_option(process_scripts_version, "scripts")
@start_directory_option()
@output_directory_option()
@verbose_option()
@click.option(
    "audit_config_file",
    "--conf",
    "-c",
    default="audit-all.yaml",
    help="Default: audit-all.yaml. Provide a YAML configuration file to specify the options. If only a file name, assumes analysis-toolit/conf.d location. Forces quiet mode.",
)
@click.option(
    "source_files_spec",
    "--filespec",
    "-f",
    default="*.txt",
    help="Default: *.txt. Specify the file specification to match. This can be a glob pattern.",
)
@click.option(
    "--list-audit-configs",
    help="List all available audit configuration files and then exit",
    is_flag=True,
)
@click.option(
    "--list-sections",
    help="List all sections headers found in FILESPEC and then exit",
    is_flag=True,
)
@click.option(
    "--list-source-files",
    help="List all files found in FILESPEC and then exit",
    is_flag=True,
)
@click.option(
    "--list-systems",
    help="Print system details found in FILESPEC and then exit",
    is_flag=True,
)
def process_command_line(**cli_config: dict) -> None:
    """Process collector script results files (formerly adv-searchfor)."""
    """Convert the click config to a ProgramConfig object and perform validation."""
    try:
        program_config = validate_program_config(ProgramConfig, **cli_config)
    except ValueError as e:
        handle_fatal_error(e, error_prefix="Configuration validation failed")

    # Echo the program configuration to the screen
    if program_config.verbose:
        print_verbose_config(cli_config, program_config)

    # List available audit configuration files
    if program_config.list_audit_configs:
        # List all available configuration files
        list_audit_configs(program_config)
        return

    # List all discovered source file section headings
    if program_config.list_sections:
        list_sections()
        return

    # List all discovered source files
    if program_config.list_source_files:
        list_source_files(program_config)
        return

    # List all discovered systems
    if program_config.list_systems:
        list_systems(program_config)
        return

    # Start the main processing
    process_scipts_results(program_config)


def list_audit_configs(program_config: ProgramConfig) -> None:
    """List all available audit configuration files."""
    rich_output = get_rich_output()
    rich_output.header("Available Audit Configuration Files")

    # Create a Rich table for configuration files
    table = rich_output.table(
        title="📋 Audit Configuration Files",
        show_header=True,
        header_style="bold cyan",
        border_style="blue",
    )

    if table is None:  # Quiet mode
        return

    table.add_column("Configuration File", style="cyan", min_width=30)
    if program_config.verbose:
        table.add_column("Details", style="white", min_width=40)

    max_details_items = 3  # Limit displayed details in verbose mode

    for config_file in process_systems.get_config_files(program_config.config_path):
        yaml_data: dict[str, Any] = load_yaml_config(config_file)
        relative_path = str(config_file.relative_to(program_config.config_path))

        if program_config.verbose:
            # Create details string for verbose mode
            details = []
            for key, value in yaml_data.to_dict().items():
                details.append(f"{key}: {rich_output.format_value(value, 60)}")
            details_text = "\n".join(details[:max_details_items])
            if len(yaml_data.to_dict()) > max_details_items:
                details_text += (
                    f"\n... and {len(yaml_data.to_dict()) - max_details_items} more"
                )
            table.add_row(relative_path, details_text)
        else:
            table.add_row(relative_path)

    rich_output.display_table(table)


def list_sections() -> None:
    """List all sections found in the specified source files."""
    rich_output = get_rich_output()
    rich_output.info("Listing sections... (feature not yet implemented)")


def list_source_files(program_config: ProgramConfig) -> None:
    """List all source files found in the specified path."""
    rich_output = get_rich_output()
    rich_output.header("Source Files")

    source_files = list(process_systems.get_source_files(program_config))

    if not source_files:
        rich_output.warning("No source files found")
        return

    # Create a Rich table for source files using the centralized utility
    table = create_file_listing_table(
        rich_output,
        title="📁 Source Files",
        file_column_name="File Path",
    )

    if table is None:  # Quiet mode
        return

    for file in source_files:
        size_str = get_file_size(file)
        table.add_row(str(file), size_str)

    rich_output.display_table(table)
    rich_output.success(f"Total source files found: {len(source_files)}")


def list_systems(program_config: ProgramConfig) -> None:
    """List all systems found in the specified source files."""
    rich_output = get_rich_output()
    rich_output.header("Systems Found")

    systems = list(process_systems.enumerate_systems_from_source_files(program_config))

    if not systems:
        rich_output.warning("No systems found")
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
    hash_display_length = 16  # Length of hash to display

    for system in systems:
        row_data = [system.system_name, system.file_hash[:hash_display_length] + "..."]

        if program_config.verbose:
            # Create details string for verbose mode
            details = []
            for key, value in system.model_dump().items():
                if key not in [
                    "system_name",
                    "file_hash",
                ]:  # Skip already displayed fields
                    details.append(f"{key}: {rich_output.format_value(value, 60)}")
            details_text = "\n".join(details[:max_detail_fields])
            if len(details) > max_detail_fields:
                details_text += (
                    f"\n... and {len(details) - max_detail_fields} more fields"
                )
            row_data.append(details_text)

        table.add_row(*row_data)

    rich_output.display_table(table)
    rich_output.success(f"Total systems found: {len(systems)}")


def print_verbose_config(cli_config: dict, program_config: ProgramConfig) -> None:
    """Print the program configuration in verbose mode using Rich formatting."""
    rich_output: RichOutput = get_rich_output(verbose=True)

    # Display configuration using Rich
    rich_output.configuration_table(
        config_dict=program_config.to_dict(),
        original_dict=cli_config,
        title="Program Configuration",
        force=True,
    )


def process_scipts_results(program_config: ProgramConfig) -> None:  # noqa: C901, PLR0912
    """Process the source files and execute searches."""
    rich_output = get_rich_output()
    time_stamp: str = get_timestamp()

    rich_output.header("Processing Source Files")

    # Create results path
    create_results_directory(
        program_config.results_path,
        verbose=program_config.verbose,
    )

    # Load systems
    systems: list[Systems] = list(
        process_systems.enumerate_systems_from_source_files(program_config),
    )
    rich_output.info(f"Found {len(systems)} systems to process")

    # Load search configurations
    search_configs: list[SearchConfig] = load_search_configs(
        program_config.audit_config_file,
    )
    rich_output.info(f"Loaded {len(search_configs)} search configurations")

    # Initialize dictionary with all OSFamilyType values using a dictionary comprehension
    os_results: dict[str, list[SearchResult]] = {
        os_type.value: [] for os_type in OSFamilyType
    }

    # Execute searches with Rich progress bar or verbose output
    if program_config.verbose:
        # Use verbose Rich output instead of progress bar
        rich_output.subheader("Executing Searches")
        for config in search_configs:
            os_type: str = _get_sysfilter_os_type(config)
            rich_output.debug(f"Executing search: ({os_type}) {config.name}")

            results: SearchResults = execute_search(config, systems)

            # Find the matching OS type or default to UNDEFINED
            matching_os: OSFamilyType = OSFamilyType.UNDEFINED
            for enum_os in OSFamilyType:
                if enum_os.value == os_type:
                    matching_os = enum_os.value
                    break

            # Append results to the corresponding OS type list
            os_results[matching_os].append(results)

            if results.result_count == 0:
                rich_output.warning("  No matches found")
            else:
                rich_output.success(f"  Found {results.result_count} matches")
    else:
        # Use Rich progress bar for non-verbose mode
        for config in rich_output.simple_progress(
            search_configs,
            "Executing searches",
        ):
            os_type: str = _get_sysfilter_os_type(config)
            results: SearchResults = execute_search(config, systems)

            # Find the matching OS type or default to UNDEFINED
            matching_os: OSFamilyType = OSFamilyType.UNDEFINED
            for enum_os in OSFamilyType:
                if enum_os.value == os_type:
                    matching_os = enum_os.value
                    break

            # Append results to the corresponding OS type list
            os_results[matching_os].append(results)

    # Export results to separate Excel files based on OS type
    rich_output.subheader("Exporting Results")
    files_created: list[str] = []

    # Group systems by OS family for proper filtering
    systems_by_os = defaultdict(list)
    for system in systems:
        os_family = system.os_family.value if system.os_family else "Unknown"
        systems_by_os[os_family].append(system)

    for os_type, results in os_results.items():
        if not results:
            continue

        output_file: Path = (
            program_config.results_path / f"{os_type}_search_results-{time_stamp}.xlsx"
        )

        # Filter systems to only include those for this OS type
        os_systems = systems_by_os.get(os_type, [])

        export_search_results_to_excel(results, output_file, os_systems)
        files_created.append(str(output_file.relative_to(program_config.results_path)))
        if program_config.verbose:
            rich_output.debug(
                f"Exported {len(results)} results for {os_type} to {output_file.relative_to(program_config.results_path)}",
            )

    if not files_created:
        rich_output.warning("No results found to export.")
    else:
        rich_output.success(
            f"{len(files_created)} results files created: {', '.join(files_created)}",
        )


def _get_sysfilter_os_type(config: SearchConfig) -> str:
    """Get the OS type from the search configuration."""
    # Iterate through the sys_filter list to find the first one with an os_family
    for sysfilter in config.sys_filter:
        if sysfilter.attr == SysFilterAttr.OS_FAMILY:
            return sysfilter.value

    return "Unknown"
