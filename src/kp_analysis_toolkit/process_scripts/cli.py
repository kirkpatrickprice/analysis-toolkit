import click

from kp_analysis_toolkit.process_scripts import (
    __version__ as process_scripts_version,
)
from kp_analysis_toolkit.process_scripts import process_scripts
from kp_analysis_toolkit.process_scripts.data_models import ProgramConfig


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
def process_script_results(**cli_config: dict) -> None:
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

    if program_config.verbose:
        print("Program configuration:")
        # Iterate over the fields in the ProgramConfig object
        for field_name, field_value in program_config:
            print(f" - {field_name}: {field_value}")

    if program_config.list_audit_configs:
        # List all available configuration files
        click.echo("Listing available audit configuration files...")
        for config_file in process_scripts.get_config_files():
            click.echo(f" - {config_file}")
        return
    if program_config.list_sections:
        click.echo("Listing sections...")
        return

    if program_config.list_source_files:
        click.echo("Listing source files...")
        for source_file in process_scripts.get_source_files(
            program_config.source_files_path,
            program_config.source_files_spec,
        ):
            click.echo(f" - {source_file}")
        return

    if program_config.list_systems:
        click.echo("Printing system details...")
        return
