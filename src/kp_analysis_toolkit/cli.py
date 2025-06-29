import platform
import sys
from collections.abc import Callable
from pathlib import Path

import rich_click as click

from kp_analysis_toolkit import __version__ as cli_version
from kp_analysis_toolkit.nipper_expander import __version__ as nipper_version
from kp_analysis_toolkit.nipper_expander.cli import (
    process_command_line as nipper_process_command_line,
)
from kp_analysis_toolkit.process_scripts import __version__ as scripts_version
from kp_analysis_toolkit.process_scripts.cli import (
    process_command_line as scripts_process_command_line,
)
from kp_analysis_toolkit.rtf_to_text import __version__ as rtf_version
from kp_analysis_toolkit.rtf_to_text.cli import (
    process_command_line as rtf_process_command_line,
)
from kp_analysis_toolkit.utils.rich_output import RichOutput, get_rich_output
from kp_analysis_toolkit.utils.version_checker import check_and_prompt_update

# Configure Rich Click for enhanced help formatting
click.rich_click.USE_RICH_MARKUP = True
click.rich_click.USE_MARKDOWN = True
click.rich_click.SHOW_ARGUMENTS = True
click.rich_click.GROUP_ARGUMENTS_OPTIONS = True
click.rich_click.STYLE_ERRORS_SUGGESTION = "magenta italic"
click.rich_click.STYLE_COMMANDS_TABLE_COLUMN_WIDTH_RATIO = (1, 2)
click.rich_click.STYLE_OPTION = "bold cyan"
click.rich_click.STYLE_ARGUMENT = "bold cyan"
click.rich_click.STYLE_COMMAND = "bold cyan"
click.rich_click.STYLE_SWITCH = "bold green"
click.rich_click.MAX_WIDTH = 100

CONTEXT_SETTINGS: dict[str, int] = {
    "max_content_width": 120,
    "terminal_width": 120,
}


def _version_callback(ctx: click.Context, _param: click.Parameter, value: bool) -> None:  # noqa: FBT001
    """Display version information with Rich formatting and exit."""
    if not value or ctx.resilient_parsing:
        return

    console = get_rich_output()

    # Include the expected text for test compatibility
    console.print("kpat_cli version " + cli_version)
    console.print("")

    # Main banner
    console.banner(
        title="🔧 KP Analysis Toolkit",
        subtitle="Python utilities for security analysis and data processing",
        version=cli_version,
        force=True,
    )

    # Module versions table
    table = console.table(
        title="📦 Module Versions",
        show_header=True,
        header_style="bold cyan",
        border_style="blue",
        force=True,
    )

    if table is not None:
        table.add_column("Module", style="bold white", min_width=20)
        table.add_column("Version", style="bold green", min_width=10)
        table.add_column("Description", style="cyan", min_width=40)

        table.add_row(
            "kp-analysis-toolkit",
            cli_version,
            "Main toolkit package",
        )
        table.add_row(
            "process-scripts",
            scripts_version,
            "Collector script results processor",
        )
        table.add_row(
            "nipper-expander",
            nipper_version,
            "Nipper CSV file expander",
        )
        table.add_row(
            "rtf-to-text",
            rtf_version,
            "RTF to plain text converter",
        )

        console.display_table(table, force=True)

    # System information
    console.print("")

    # Get system information
    python_version = (
        f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    )
    platform_info = platform.platform()
    architecture = platform.architecture()[0]

    # Installation path
    try:
        install_path = Path(__file__).parent.parent.parent
    except (AttributeError, OSError):
        install_path = "Unknown"

    console.info(
        f"💻 Environment: Python {python_version} on {platform_info} ({architecture})"
    )
    console.info(f"📦 Installation: {install_path}")
    console.print("")

    ctx.exit()


@click.group(context_settings=CONTEXT_SETTINGS, invoke_without_command=True)
@click.option(
    "--version",
    is_flag=True,
    expose_value=False,
    is_eager=True,
    callback=_version_callback,
    help="Show version information and exit.",
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
        console = get_rich_output()
        _show_enhanced_help(console)


# Add commands to the CLI group at import time
cli.add_command(scripts_process_command_line, name="scripts")
cli.add_command(nipper_process_command_line, name="nipper")
cli.add_command(rtf_process_command_line, name="rtf-to-text")


def _show_enhanced_help(console: RichOutput) -> None:
    """Show enhanced help using Rich formatting."""
    console.header("🔧 KP Analysis Toolkit")
    console.print("")
    console.info("A comprehensive toolkit for security analysis and data processing.")
    console.print("")

    # Create a table for available commands
    table = console.table(
        title="📋 Available Commands",
        show_header=True,
        header_style="bold cyan",
        border_style="blue",
    )

    if table is not None:  # Not in quiet mode
        table.add_column("Command", style="bold white", min_width=15)
        table.add_column("Description", style="cyan", min_width=50)

        table.add_row(
            "scripts",
            "Process collector script results files (formerly adv-searchfor)",
        )
        table.add_row(
            "nipper",
            "Process a Nipper CSV file and expand it into a more readable format",
        )
        table.add_row(
            "rtf-to-text",
            "Convert RTF files to plain text format with ASCII encoding",
        )

        console.display_table(table)

    console.print("")
    console.info(
        "Use 'kpat_cli <command> --help' for more information on a specific command."
    )
    console.print("")
    console.subheader("Options:")
    console.print("  --version            Show the version and exit")
    console.print("  --skip-update-check  Skip checking for updates at startup")
    console.print("  --help               Show this message and exit")


def _show_deprecation_warning(legacy_cmd: str, new_cmd: str) -> None:
    """Show deprecation warning for legacy commands."""
    console = get_rich_output()

    console.warning(f"The '{legacy_cmd}' command is deprecated.")
    console.info(f"Please use '{new_cmd}' instead.")
    console.warning("This legacy command will be removed in a future version.")
    console.print("")


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
