import click

from kp_analysis_toolkit import __version__ as cli_version
from kp_analysis_toolkit.process_scripts.cli import process_command_line


@click.group()
@click.version_option(
    version=cli_version,
    prog_name="kpat_cli",
    message="%(prog)s version %(version)s",
)
def cli() -> None:
    pass


def main() -> None:
    """Main entry point for the kpat_cli command line interface."""
    cli.add_command(process_command_line, name="scripts")
    cli()


if __name__ == "__main__":
    main()
