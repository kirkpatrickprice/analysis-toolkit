import click

from kp_analysis_toolkit import __version__ as cli_version
from kp_analysis_toolkit.nipper_expander.cli import (
    process_command_line as nipper_process_command_line,
)
from kp_analysis_toolkit.process_scripts.cli import (
    process_command_line as scripts_process_command_line,
)

CONTEXT_SETTINGS: dict[str, int] = {
    "max_content_width": 120,
    "terminal_width": 120,
}


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(
    version=cli_version,
    prog_name="kpat_cli",
    message="%(prog)s version %(version)s",
)
def cli() -> None:
    """Command line interface for the KP Analysis Toolkit."""
    pass  # noqa: PIE790


def main() -> None:
    """Main entry point for the kpat_cli command line interface."""
    cli.add_command(scripts_process_command_line, name="scripts")
    cli.add_command(nipper_process_command_line, name="nipper")
    cli()


if __name__ == "__main__":
    main()
