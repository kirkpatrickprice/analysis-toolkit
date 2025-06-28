import sys
from collections import defaultdict
from contextlib import nullcontext
from typing import TYPE_CHECKING, Any

import click
import pandas as pd

from kp_analysis_toolkit.process_scripts import process_systems
from kp_analysis_toolkit.process_scripts.excel_exporter import (
    export_search_results_to_excel,
)
from kp_analysis_toolkit.process_scripts.models.enums import OSFamilyType, SysFilterAttr
from kp_analysis_toolkit.process_scripts.models.program_config import (
    ProgramConfig,
)
from kp_analysis_toolkit.process_scripts.models.search.base import SearchConfig
from kp_analysis_toolkit.process_scripts.search_engine import (
    execute_search,
    load_search_configs,
    load_yaml_config,
)
from kp_analysis_toolkit.utils.get_timestamp import get_timestamp

if TYPE_CHECKING:
    from pathlib import Path

    from click._termui_impl import ProgressBar

    from kp_analysis_toolkit.process_scripts.models.results.base import (
        SearchResult,
        SearchResults,
    )
    from kp_analysis_toolkit.process_scripts.models.systems import Systems


def create_results_path(program_config: ProgramConfig) -> None:
    """Create the results path if it does not exist."""
    if program_config.results_path.exists():
        click.echo(f"Reusing results path: {program_config.results_path}")
        return
    if program_config.verbose:
        click.echo(f"Creating results path: {program_config.results_path}")
    program_config.results_path.mkdir(parents=True, exist_ok=False)


def get_size(obj: Any, seen: set | None = None) -> int:  # noqa: ANN401
    """Recursively find the size of an object and its contents in bytes."""
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0
    # Mark object as seen
    seen.add(obj_id)
    size = sys.getsizeof(obj)

    # Handle iterables
    if isinstance(obj, list | tuple | set | dict):
        if isinstance(obj, list | tuple | set):
            size += sum(get_size(i, seen) for i in obj)
        else:  # dict
            size += sum(get_size(k, seen) + get_size(v, seen) for k, v in obj.items())

    return size


def list_audit_configs(program_config: ProgramConfig) -> None:
    """List all available audit configuration files."""
    click.echo("Listing available audit configuration files...")
    terminal_width: int = pd.get_option("display.width")
    for config_file in process_systems.get_config_files(program_config.config_path):
        yaml_data: dict[str, Any] = load_yaml_config(config_file)
        click.echo(
            f" - {summarize_text(str(config_file.relative_to(program_config.config_path)), max_length=terminal_width - 3)}",
        )
        if program_config.verbose:
            terminal_width: int = pd.get_option("display.width")
            for key, value in yaml_data.to_dict().items():
                text: str = summarize_text(str(value), max_length=terminal_width - 3)
                click.echo(f"\t- {key}: {text}")


def list_sections() -> None:
    """List all sections found in the specified source files."""
    click.echo("Listing sections...")


def list_source_files(program_config: ProgramConfig) -> None:
    """List all source files found in the specified path."""
    click.echo("Listing source files...")

    for i, file in enumerate(process_systems.get_source_files(program_config)):  # noqa: B007
        click.echo(f" - {file}")

    click.echo(f"Total source files found: {i + 1}")


def list_systems(program_config: ProgramConfig) -> None:
    """List all systems found in the specified source files."""
    click.echo("Listing systems...")
    i: int = 0

    for system in process_systems.enumerate_systems_from_source_files(program_config):
        click.echo(f" - {system.system_name} (SHA256: {system.file_hash})")
        i += 1
        for key, value in system.model_dump().items():
            click.echo(f"\t- {key}: {value}")
    click.echo(f"Total systems found: {i}")


def summarize_text(
    text: str,
    *,
    first_x_chars: int = 10,
    max_length: int = 50,
    replace_with: str = "...",
) -> str:
    """Summarize text to a maximum length."""
    if len(text) <= max_length:
        return text
    end_chars = max_length - first_x_chars - len(replace_with)
    result: str = f"{text[:first_x_chars]}...{text[-end_chars:]}"
    return result


def print_verbose_config(cli_config: dict, program_config: ProgramConfig) -> None:
    """Print the program configuration in verbose mode."""
    click.echo("Program configuration:")

    # Set the column widths for display
    # Get terminal width (or use a default if we can't determine it)
    try:
        terminal_width = pd.get_option("display.width")
    except:  # noqa: E722
        terminal_width: int = 120  # Default width

    original_width: int = 25
    effective_width: int = 60

    # Prepare the configuration data for Pandas DataFrame
    config_data: list[dict[str, str]] = []
    for field_name, field_value in program_config.to_dict().items():
        try:
            original_str: str = summarize_text(
                str(cli_config[field_name]),
                max_length=effective_width,
            )
        except KeyError:
            original_str: str = "<Computed>"

        # Format original value if it exceeds the width
        effective_str: str = summarize_text(field_value, max_length=effective_width)

        # Append to the configuration data list
        config_data.append(
            {
                "Parameter": field_name,
                "Original": original_str,
                "Effective": effective_str,
            },
        )

    if config_data:
        # Create DataFrame
        dataframe = pd.DataFrame(config_data)

        # Calculate column widths
        # Find max parameter name length for dynamic sizing
        max_param_width: int = (
            max(len(str(param)) for param in dataframe["Parameter"]) + 1
        )

        # Apply column formatting
        with pd.option_context(
            "display.max_rows",
            None,  # Show all rows
            "display.max_columns",
            None,  # Show all columns
            "display.width",
            terminal_width,
        ):
            # Format the dataframe with custom column widths
            formatted_df: pd.DataFrame = dataframe.copy()

        # Adjust column display format
        formatted_df["Effective"] = formatted_df["Effective"].str.ljust(effective_width)
        click.echo(
            formatted_df.to_string(
                index=False,
                col_space={
                    "Parameter": max_param_width,
                    "Original": original_width,
                    "Effective": effective_width,
                },
                justify="left",
                max_colwidth=effective_width,
            ),
        )


def process_scipts_results(program_config: ProgramConfig) -> None:  # noqa: C901, PLR0912
    """Process the source files and execute searches."""
    time_stamp: str = get_timestamp()
    click.echo("Processing source files...")

    # Create results path
    create_results_path(program_config)

    # Load systems
    systems: list[Systems] = list(
        process_systems.enumerate_systems_from_source_files(program_config),
    )
    click.echo(f"Found {len(systems)} systems to process")

    # Load search configurations
    search_configs: list[SearchConfig] = load_search_configs(
        program_config.audit_config_file,
    )
    click.echo(f"Loaded {len(search_configs)} search configurations")

    # Initialize dictionary with all OSFamilyType values using a dictionary comprehension
    os_results: dict[str, list[SearchResult]] = {
        os_type.value: [] for os_type in OSFamilyType
    }

    # Execute searches
    search_iterator: ProgressBar[SearchConfig] | list[SearchConfig] = (
        click.progressbar(
            search_configs,
            length=len(search_configs),
            label="Executing searches",
            show_eta=True,
            show_percent=True,
        )
        if not program_config.verbose
        else search_configs
    )

    with (
        search_iterator
        if not program_config.verbose
        else nullcontext(search_configs) as iterator
    ):
        for config in iterator:
            os_type: str = _get_sysfilter_os_type(config)

            if program_config.verbose:
                click.echo(f"Executing search: ({os_type}) {config.name}")

            results: SearchResults = execute_search(config, systems)

            # Find the matching OS type or default to UNDEFINED
            matching_os: OSFamilyType = OSFamilyType.UNDEFINED
            for enum_os in OSFamilyType:
                if enum_os.value == os_type:
                    matching_os = enum_os.value
                    break

            # Append results to the corresponding OS type list
            os_results[matching_os].append(results)

            if program_config.verbose:
                if results.result_count == 0:
                    click.secho("  No matches found", fg="yellow")
                else:
                    click.echo(f"  Found {results.result_count} matches")

    # Export results to separate Excel files based on OS type
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
            click.echo(
                f"Exported {len(results)} results for {os_type} to {output_file.relative_to(program_config.results_path)}",
            )

    if not files_created:
        click.echo("No results found to export.")
    else:
        click.echo(
            f"{len(files_created)} results files created: {', '.join(files_created)}",
        )


def _get_sysfilter_os_type(config: SearchConfig) -> str:
    """Get the OS type from the search configuration."""
    # Iterate through the sys_filter list to find the first one with an os_family
    for sysfilter in config.sys_filter:
        if sysfilter.attr == SysFilterAttr.OS_FAMILY:
            return sysfilter.value

    return "Unknown"
