import click

from kp_analysis_toolkit.process_scripts import (
    __version__ as process_scripts_version,
)
from kp_analysis_toolkit.process_scripts import process_scripts
from kp_analysis_toolkit.shared_funcs import print_help


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
    "source_file_spec",
    "--filespec",
    "-f",
    default="*.txt",
    help="Default: *.txt. Specify the file specification to match. This can be a glob pattern.",
)
@click.option(
    "--list-configs",
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
    "--quiet",
    "-q",
    default=True,
    help="Be vewy, vwey qwiet... wew hunting wabbits",
    is_flag=True,
)
@click.option(
    "--verbose",
    "-v",
    default=False,
    help="Be verbose",
    is_flag=True,
)
def process_script_results(**program_config: dict) -> None:
    """Process collector script results files (formerly adv-searchfor)."""
    if program_config["list_configs"]:
        # List all available configuration files
        click.echo("Listing available audit configuration files...")
        for config_file in process_scripts.get_config_files():
            click.echo(f" - {config_file}")
        return
    if program_config["list_sections"]:
        click.echo("Listing sections...")
        return

    if program_config["list_source_files"]:
        click.echo("Listing source files...")
        for source_file in process_scripts.get_source_files(
            program_config["source_files_path"],
            program_config["source_file_spec"],
        ):
            click.echo(f" - {source_file}")
        return

    if program_config["list_systems"]:
        click.echo("Printing system details...")
        return

    if not program_config["audit_config_file"]:
        click.echo(
            click.style(
                "No configuration file provided. Provide an audit configuration file with the -c option.",
                fg="red",
            ),
        )
        print_help()
        return

    if program_config["quiet"] and program_config["verbose"]:
        click.echo(
            "Verbose and quiet mode are mutually exclusive. Ignoring verbose flag.",
        )
        program_config["verbose"] = False

    args: dict = {
        "audit_config_file": program_config["audit_config_file"],
        "source_files": program_config["source_files"],
    }
    # Call the main processing function with the provided arguments
    process_scripts.entry_point(args)
