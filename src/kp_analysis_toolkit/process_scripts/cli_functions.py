from typing import Any

import click

from kp_analysis_toolkit.process_scripts import process_scripts
from kp_analysis_toolkit.process_scripts.data_models import ProgramConfig, Systems


def create_results_path(program_config: ProgramConfig) -> None:
    """Create the results path if it does not exist."""
    if not program_config.results_path.exists():
        if program_config.verbose:
            click.echo(f"Creating results path: {program_config.results_path}")
        program_config.results_path.mkdir(parents=True, exist_ok=True)
    else:
        click.echo(f" Output path {program_config.results_path.absolute()} exists.")
        click.echo(click.style("Results will be overwritten if they exist.", fg="red"))
        click.echo(
            click.style(
                "Or use --out-path to specify a different output path.",
                fg="red",
            ),
        )
        _: Any = input("Press Enter to continue or Ctrl-C to cancel...")
        # Recursively delete the results path
        for item in program_config.results_path.iterdir():
            if item.is_dir():
                if program_config.verbose:
                    click.echo(f"Deleting directory: {item}")
                item.rmdir()
            else:
                if program_config.verbose:
                    click.echo(f"Deleting file: {item}")
                item.unlink(missing_ok=True)
        if program_config.verbose:
            click.echo(f"Deleting directory: {program_config.results_path}")
        program_config.results_path.rmdir()
        if program_config.verbose:
            click.echo(f"Creating directory: {program_config.results_path}")
        program_config.results_path.mkdir(parents=True, exist_ok=True)


def list_audit_configs(program_config: ProgramConfig) -> None:
    """List all available audit configuration files."""
    click.echo("Listing available audit configuration files...")
    for config_file in process_scripts.get_config_files(program_config.config_path):
        click.echo(f" - {config_file.absolute()}")


def list_sections() -> None:
    """List all sections found in the specified source files."""
    click.echo("Listing sections...")


def list_source_files(program_config: ProgramConfig) -> None:
    """List all source files found in the specified path."""
    click.echo("Listing source files...")
    source_files = process_scripts.get_source_files(
        start_path=program_config.source_files_path,
        file_spec=program_config.source_files_spec,
    )
    if not source_files:
        click.echo("No source files found.")
        return

    click.echo(f"Found {len(source_files)} source files:")
    for file in source_files:
        click.echo(f" - {file}")


def list_systems(program_config: ProgramConfig) -> None:
    """List all systems found in the specified source files."""
    click.echo("Listing systems...")
    systems: list[Systems] = process_scripts.enumerate_systems(program_config)

    if not systems:
        click.echo("No systems found.")
        return

    click.echo(f"Found {len(systems)} systems")
    click.echo("Systems:")
    for system in systems:
        click.echo(f" - {system.system_name} (SHA256: {system.file_hash})")
        for key, value in system.model_dump().items():
            click.echo(f"\t- {key}: {value}")


def print_verbose_config(cli_config: dict, program_config: ProgramConfig) -> None:
    """Print the program configuration in verbose mode."""
    click.echo("Program configuration:")
    # Iterate over the fields in the ProgramConfig object and print both the original and converted values
    for field_name, field_value in program_config.model_dump().items():
        click.echo(f" - {field_name}:")
        try:
            click.echo(f"\t- Original : {cli_config[field_name]}")
        except KeyError:
            click.echo("\t- Original : <Computed Value>")
        click.echo(f"\t- Effective: {field_value}")


def process_scipts_results(program_config: ProgramConfig) -> None:
    """Process the source files and load the results into DuckDB."""
    click.echo("Processing source files...")

    # Check if the results_path exists
    create_results_path(program_config)
    systems: list[Systems] = process_scripts.enumerate_systems_from_source_files(
        program_config
    )
    if not systems:
        click.echo("No systems found.")
        return

    click.echo(f"Found {len(systems)} systems to process.")
    if program_config.verbose:
        click.echo("Systems:")
        for system in systems:
            click.echo(f" - {system.system_name} (SHA256: {system.file_hash})")
            for key, value in system.model_dump().items():
                click.echo(f"\t- {key}: {value}")

    # Commit the systems to the database
    if systems:
        records_inserted: int = process_scripts.commit_to_database(
            records=systems,
            model_class=Systems,
            program_config=program_config,
        )
        click.echo(f"Systems committed to database: {records_inserted}")

        for system in systems:
            # Commit the raw data to the database
            click.echo(f"Processing raw data for system: {system.system_name}")
            records_inserted = process_scripts.commit_raw_data_to_database(
                system=system,
                program_config=program_config,
            )
            click.echo(
                f"Raw data committed to database for system {system.system_name}: {records_inserted}",
            )
