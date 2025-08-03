# AI-GEN: CopilotChat|2025-07-31|KPAT-ListSystems|reviewed:no
"""CLI command for process scripts functionality."""

from typing import TYPE_CHECKING, Any

import rich_click as click
from rich.table import Table

from kp_analysis_toolkit.cli.common.config_validation import (
    handle_fatal_error,
    validate_program_config,
)
from kp_analysis_toolkit.cli.common.decorators import (
    module_version_option,
    start_directory_option,
    verbose_option,
)
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
from kp_analysis_toolkit.models.types import ConfigValue
from kp_analysis_toolkit.process_scripts import (
    __version__ as process_scripts_version,
)
from kp_analysis_toolkit.process_scripts.models.program_config import ProgramConfig

if TYPE_CHECKING:
    from pathlib import Path

    from kp_analysis_toolkit.core.services.rich_output import RichOutputService
    from kp_analysis_toolkit.process_scripts.models.results.system import Systems
    from kp_analysis_toolkit.process_scripts.service import ProcessScriptsService

# Configure option groups for this command
# Note: Using standard Click help for simplicity


@click.command(name="scripts")
@module_version_option(process_scripts_version, "scripts")
@start_directory_option()
@verbose_option()
@click.option(
    "source_files_spec",
    "--filespec",
    "-f",
    default="*.txt",
    help="File pattern to match (default: *.txt). Can be a glob pattern.",
)
@click.option(
    "--list-systems",
    help="List system details found in files and exit",
    is_flag=True,
)
@click.option(
    "--list-audit-configs",
    "list_audit_configs",
    help="List available audit config files and exit",
    is_flag=True,
)
@click.option(
    "--audit-config-report",
    "audit_config_report",
    help="Show hierarchical report of search configurations and exit",
    is_flag=True,
)
@click.option(
    "--audit-config-file",
    "audit_config_file",
    default="audit-all.yaml",
    help="Audit config file to use (default: audit-all.yaml)",
)
def process_command_line(**cli_config: ConfigValue) -> None:
    """Process collector script results files (formerly adv-searchfor)."""
    # Add default out_path if not already specified
    if "out_path" not in cli_config:
        cli_config["out_path"] = "dummy_output.xlsx"  # Not used in --list* commands

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

    if program_config.list_audit_configs:
        list_audit_configs(program_config)
        return

    if program_config.audit_config_report:
        audit_config_report(program_config)
        return

    # For now, just show a message that other functionality is not implemented
    rich_output = container.core.rich_output()
    rich_output.info(
        "Full process scripts functionality not yet implemented. Use --list-systems to see available systems.",
    )


def list_systems(program_config: ProgramConfig) -> None:
    """List all systems found in the specified source files."""
    rich_output = container.core.rich_output()
    create_list_command_header(rich_output, "Systems Found")

    # Get the process scripts service from the container
    process_scripts_service: ProcessScriptsService = (
        container.process_scripts().process_scripts_service()
    )

    # Discover and analyze systems
    systems: list[Systems] = process_scripts_service.list_systems(
        input_directory=program_config.source_files_path,
        file_pattern=program_config.source_files_spec,
    )

    if not systems:
        handle_empty_list_result(rich_output, "systems")
        return

    # Create a Rich table for systems using the centralized utility
    table: Table | None = create_system_info_table(
        rich_output,
        title="🖥️ Systems",
        include_details=program_config.verbose,
    )

    if table is None:  # Quiet mode
        return

    for system in systems:
        row_data = [system.system_name, format_hash_display(system.file_hash or "")]

        if program_config.verbose:
            # Create details string for verbose mode with excluded fields
            system_data = system.model_dump()
            filtered_data = {
                k: v
                for k, v in system_data.items()
                if k not in ["system_name", "file_hash", "system_id"]
            }
            # Replace the file path with a relative path for display
            if "file" in filtered_data:
                filtered_data["file"] = system.get_relative_file_path(
                    program_config.source_files_path,
                )

            details_text = format_verbose_details(
                rich_output,
                filtered_data,
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
    rich_output = container.core.rich_output()

    # Display configuration using Rich
    rich_output.configuration_table(
        config_dict=dict(program_config.to_dict()),
        original_dict=cli_config,
        title="Program Configuration",
        force=True,
    )


def list_audit_configs(program_config: ProgramConfig) -> None:
    """
    List the available audit configurations (*.yaml) from the program's configuration directory.

    Args:
        program_config: A `process_scripts` ProgramConfig object

    """
    rich_output = container.core.rich_output()
    create_list_command_header(rich_output, "Audit Configurations")

    # Get the process scripts service from the container
    process_scripts_service: ProcessScriptsService = (
        container.process_scripts().process_scripts_service()
    )

    # List audit configurations
    audit_configs: list[Path] = process_scripts_service.list_audit_configs(
        config_path=program_config.config_path,
    )

    if not audit_configs:
        handle_empty_list_result(rich_output, "audit configurations")
        return

    # Create a Rich table for audit configurations
    table: Table | None = Table(
        title="Audit Configurations",
        show_header=True,
        header_style="bold magenta",
    )
    table.add_column("File Name", style="dim")
    for config in audit_configs:
        table.add_row(config.name)

    rich_output.display_table(table)
    display_list_summary(rich_output, len(audit_configs), "audit configurations")


def audit_config_report(program_config: ProgramConfig) -> None:
    """
    Generate and display a hierarchical report of audit configurations.

    Args:
        program_config: A `process_scripts` ProgramConfig object

    """
    rich_output = container.core.rich_output()
    create_list_command_header(rich_output, "Audit Configuration Report")

    # Get the process scripts service from the container
    process_scripts_service: ProcessScriptsService = (
        container.process_scripts().process_scripts_service()
    )

    # Get the root configuration file path
    root_config_file = program_config.config_path / program_config.audit_config_file

    try:
        # Generate the hierarchical report
        report_data = process_scripts_service.generate_config_hierarchy_report(
            root_config_file,
        )

        # Extract tree and statistics
        if "tree" in report_data and "statistics" in report_data:
            config_tree = report_data["tree"]
            stats = report_data["statistics"]

            # Display the tree structure
            _display_config_tree(rich_output, config_tree, indent_level=0)

            # Display statistics summary
            _display_statistics_summary(rich_output, stats)
        else:
            # Handle old format or error case
            _display_config_tree(rich_output, report_data, indent_level=0)

    except (FileNotFoundError, OSError) as e:
        rich_output.error(f"Configuration file error: {e}")
    except (ValueError, KeyError, TypeError) as e:
        rich_output.error(f"Configuration parsing error: {e}")
    except RuntimeError as e:
        rich_output.error(f"Configuration processing error: {e}")


def _display_config_tree(
    rich_output: "RichOutputService",
    tree_node: dict[str, str | list],
    indent_level: int = 0,
) -> None:
    """
    Display a configuration tree node with proper indentation.

    Args:
        rich_output: Rich output service for display
        tree_node: Tree node to display
        indent_level: Current indentation level

    """
    indent = "    " * indent_level

    if "error" in tree_node:
        rich_output.error(f"{indent}Error: {tree_node['error']}")
        return

    # Display the file name
    if "file" in tree_node:
        rich_output.info(f"{indent}{tree_node['file']}")

        # Process children
        if "children" in tree_node:
            for child in tree_node["children"]:
                if isinstance(child, dict):
                    _display_child_node(rich_output, child, indent_level + 1)


def _display_child_node(
    rich_output: "RichOutputService",
    child_node: dict[str, str | list],
    indent_level: int,
) -> None:
    """
    Display a child node based on its type.

    Args:
        rich_output: Rich output service for display
        child_node: Child node to display
        indent_level: Current indentation level

    """
    indent = "    " * indent_level

    if "error" in child_node:
        rich_output.error(f"{indent}Error: {child_node['error']}")
        return

    child_type = child_node.get("type", "unknown")

    if child_type == "global":
        _display_global_node(rich_output, child_node, indent)
    elif child_type == "include":
        _display_include_node(rich_output, child_node, indent_level)
    elif child_type == "searches":
        _display_searches_node(rich_output, child_node, indent)
    elif child_type == "search":
        _display_search_node(rich_output, child_node, indent)


def _display_global_node(
    rich_output: "RichOutputService",
    child_node: dict[str, str | list],
    indent: str,
) -> None:
    """Display a global configuration node."""
    rich_output.info(f"{indent}- {child_node.get('summary', 'global: (empty)')}")


def _display_include_node(
    rich_output: "RichOutputService",
    child_node: dict[str, str | list],
    indent_level: int,
) -> None:
    """Display an include configuration node."""
    indent = "    " * indent_level
    include_name = child_node.get("name", "unknown_include")
    rich_output.info(f"{indent}- {include_name}")

    # Display included files
    if "children" in child_node:
        for included_file in child_node["children"]:
            if isinstance(included_file, dict):
                _display_config_tree(rich_output, included_file, indent_level + 1)


def _display_searches_node(
    rich_output: "RichOutputService",
    child_node: dict[str, str | list],
    indent: str,
) -> None:
    """Display a searches container node."""
    rich_output.info(f"{indent}- Searches:")

    # Display individual search configurations
    if "children" in child_node:
        for search in child_node["children"]:
            if isinstance(search, dict) and search.get("type") == "search":
                search_name = search.get("name", "Unknown Search")
                rich_output.info(f"{indent}    - {search_name}")


def _display_search_node(
    rich_output: "RichOutputService",
    child_node: dict[str, str | list],
    indent: str,
) -> None:
    """Display an individual search node."""
    search_name = child_node.get("name", "Unknown Search")
    rich_output.info(f"{indent}- {search_name}")


def _display_statistics_summary(
    rich_output: "RichOutputService",
    stats: dict[str, int | dict],
) -> None:
    """
    Display a summary of configuration statistics.

    Args:
        rich_output: Rich output service for display
        stats: Statistics dictionary containing counts and breakdowns

    """
    rich_output.info("\n📊 Configuration Statistics:")
    rich_output.info(
        f"   Total configuration files processed: {stats.get('files_processed', 0)}",
    )
    rich_output.info(
        f"   Total search configurations: {stats.get('total_searches', 0)}",
    )

    # Display breakdown by OS family
    searches_by_os = stats.get("searches_by_os_family", {})
    if searches_by_os:
        rich_output.info("   Search configurations by OS family:")
        for os_family, count in sorted(searches_by_os.items()):
            rich_output.info(f"     - {os_family}: {count} searches")


# END AI-GEN
