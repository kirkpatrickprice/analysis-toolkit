import sys
from collections.abc import Callable

import click

from kp_analysis_toolkit import __version__ as cli_version
from kp_analysis_toolkit.nipper_expander.cli import (
    process_command_line as nipper_process_command_line,
)
from kp_analysis_toolkit.process_scripts.cli import (
    process_command_line as scripts_process_command_line,
)
from kp_analysis_toolkit.rtf_to_text.cli import (
    process_command_line as rtf_process_command_line,
)
from kp_analysis_toolkit.utils.version_checker import check_and_prompt_update

CONTEXT_SETTINGS: dict[str, int] = {
    "max_content_width": 120,
    "terminal_width": 120,
}


@click.group(context_settings=CONTEXT_SETTINGS, invoke_without_command=True)
@click.version_option(
    version=cli_version,
    prog_name="kpat_cli",
    message="%(prog)s version %(version)s",
)
@click.option(
    "--skip-update-check",
    is_flag=True,
    default=False,
    help="Skip checking for updates at startup.",
)
@click.pass_context
def cli(ctx: click.Context, skip_update_check: bool) -> None:  # noqa: FBT001
    """Command line interface for the KP Analysis Toolkit."""
    # Always run version check unless explicitly skipped
    if not skip_update_check:
        check_and_prompt_update()

    # If no subcommand was invoked and no help was requested, show help
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


# Add commands to the CLI group at import time
cli.add_command(scripts_process_command_line, name="scripts")
cli.add_command(nipper_process_command_line, name="nipper")
cli.add_command(rtf_process_command_line, name="rtf-to-text")


def _show_deprecation_warning(legacy_cmd: str, new_cmd: str) -> None:
    """Show deprecation warning for legacy commands."""
    click.secho(
        f"⚠️  WARNING: The '{legacy_cmd}' command is deprecated.",
        fg="yellow",
        bold=True,
    )
    click.secho(
        f"   Please use '{new_cmd}' instead.",
        fg="yellow",
    )
    click.secho(
        "   This legacy command will be removed in a future version.",
        fg="yellow",
    )
    click.echo()


def _create_legacy_command(
    legacy_name: str,
    new_command: str,
    command_func: Callable[[], None],
) -> Callable[[], None]:
    """Create a legacy command wrapper with deprecation warning."""

    def legacy_wrapper() -> None:
        _show_deprecation_warning(legacy_name, new_command)
        # Update sys.argv[0] to show the correct command name in help
        original_argv0 = sys.argv[0]
        sys.argv[0] = legacy_name.replace("_", "-")
        try:
            command_func()
        finally:
            # Restore original sys.argv[0]
            sys.argv[0] = original_argv0

    return legacy_wrapper


# Create legacy command wrappers
legacy_adv_searchfor: Callable[[], None] = _create_legacy_command(
    "adv-searchfor",
    "kpat_cli scripts",
    scripts_process_command_line,
)

legacy_nipper_expander: Callable[[], None] = _create_legacy_command(
    "nipper_expander",
    "kpat_cli nipper",
    nipper_process_command_line,
)


def main() -> None:
    """Main entry point for the kpat_cli command line interface."""
    cli()


if __name__ == "__main__":
    main()
