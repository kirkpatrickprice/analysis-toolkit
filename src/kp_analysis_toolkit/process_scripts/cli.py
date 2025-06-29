import rich_click as click

from kp_analysis_toolkit.process_scripts import (
    __version__ as process_scripts_version,
)
from kp_analysis_toolkit.process_scripts import (
    cli_functions as cli_funcs,
)
from kp_analysis_toolkit.process_scripts.models.program_config import ProgramConfig


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
    "--start-dir",
    "-d",
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
        from kp_analysis_toolkit.utils.rich_output import error

        error(f"Error validating configuration: {e}")
        return

    # Echo the program configuration to the screen
    if program_config.verbose:
        cli_funcs.print_verbose_config(cli_config, program_config)

    # List available audit configuration files
    if program_config.list_audit_configs:
        # List all available configuration files
        cli_funcs.list_audit_configs(program_config)
        return

    # List all discovered source file section headings
    if program_config.list_sections:
        cli_funcs.list_sections()
        return

    # List all discovered source files
    if program_config.list_source_files:
        cli_funcs.list_source_files(program_config)
        return

    # List all discovered systems
    if program_config.list_systems:
        cli_funcs.list_systems(program_config)
        return

    # Start the main processing
    cli_funcs.process_scipts_results(program_config)
