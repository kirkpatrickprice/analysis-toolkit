from typing import Any

import click

from kp_analysis_toolkit.process_scripts import (
    __version__ as process_scripts_version,
)
from kp_analysis_toolkit.process_scripts import process_scripts
from kp_analysis_toolkit.process_scripts.data_models import ProgramConfig, Systems


@click.command(name="scripts")
@click.version_option(
    version=process_scripts_version,
    prog_name="kpat_cli scripts",
    message="%(prog)s version %(version)s",
)
@click.option(
    "audit_config_file",
    "--conf",
    "-c",
    default="audit-all.yaml",
    help="Default: audit-all.yaml. Provide a YAML configuration file to specify the options. If only a file name, assumes analysis-toolit/conf.d location. Forces quiet mode.",
)
@click.option(
    "source_files_path",
    "--start-path",
    "-p",
    default="./",
    help="Default: the current working directory (./). Specify the path to start searching for files.  Will walk the directory tree from this path.",
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
@click.option(
    "--out-path",
    "-o",
    default="results/",
    help="Default: results/. Specify the output directory for the results files.",
)
@click.option(
    "--verbose",
    "-v",
    default=False,
    help="Be verbose",
    is_flag=True,
)
def process_command_line(**cli_config: dict) -> None:
    """Process collector script results files (formerly adv-searchfor)."""
    """Convert the click config to a ProgramConfig object and perform validation."""
    try:
        program_config: ProgramConfig = ProgramConfig(**cli_config)
    except ValueError as e:
        click.echo(
            click.style(
                f"Error validating configuration: {e}",
                fg="red",
            ),
        )
        return

    # Echo the program configuration to the screen
    if program_config.verbose:
        click.echo("Program configuration:")
        # Iterate over the fields in the ProgramConfig object and print both the original and converted values
        for field_name, field_value in program_config.model_dump().items():
            click.echo(f" - {field_name}:")
            try:
                click.echo(f"\t- Original : {cli_config[field_name]}")
            except KeyError:
                click.echo("\t- Original : <Computed Value>")
            click.echo(f"\t- Effective: {field_value}")

    # List available audit configuration files
    if program_config.list_audit_configs:
        # List all available configuration files
        click.echo("Listing available audit configuration files...")
        for config_file in process_scripts.get_config_files(program_config.config_path):
            if program_config.verbose:
                click.echo(f" - {config_file.absolute()}")
            else:
                click.echo(f" - {config_file.relative_to(program_config.config_path)}")
        return

    # List all discovered source file section headings
    if program_config.list_sections:
        click.echo("Listing sections...")
        return

    # List all discovered source files
    if program_config.list_source_files:
        click.echo(f"Listing source files in {program_config.source_files_path}...")
        for source_file in process_scripts.get_source_files(
            program_config.source_files_path,
            program_config.source_files_spec,
        ):
            click.echo(
                f" - {source_file.relative_to(program_config.source_files_path)}"
            )
        return

    # List all discovered systems
    if program_config.list_systems:
        click.echo("Printing system details...")
        return

    # Start the main processing
    process_scipts_results(program_config)


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
                "Or use --out-path to specify a different output path.", fg="red"
            )
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


def process_scipts_results(program_config: ProgramConfig) -> None:
    """Process the source files and load the results into DuckDB."""

    click.echo("Processing source files...")

    # Check if the results_path exists
    create_results_path(program_config)
    systems: list[Systems] = process_scripts.enumerate_systems(program_config)
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
