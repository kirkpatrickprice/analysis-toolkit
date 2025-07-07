import sys
from collections.abc import Callable
from typing import Any

import rich_click as click

from kp_analysis_toolkit import __version__ as cli_version
from kp_analysis_toolkit.cli.commands.nipper import (
    process_command_line as nipper_process_command_line,
)
from kp_analysis_toolkit.cli.commands.rtf_to_text import (
    process_command_line as rtf_process_command_line,
)
from kp_analysis_toolkit.cli.commands.scripts import (
    process_command_line as scripts_process_command_line,
)
from kp_analysis_toolkit.cli.common.output_formatting import (
    create_commands_help_table,
)
from kp_analysis_toolkit.cli.utils.system_utils import (
    get_architecture_info,
    get_installation_path,
    get_module_versions,
    get_platform_info,
    get_python_version_string,
)
from kp_analysis_toolkit.cli.utils.table_layouts import create_version_info_table
from kp_analysis_toolkit.core.containers.application import (
    initialize_dependency_injection,
)
from kp_analysis_toolkit.utils.rich_output import RichOutputService, get_rich_output
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

# Note: Global option groups are set up via individual command configuration
# to avoid wildcard conflicts with specific command configurations

CONTEXT_SETTINGS: dict[str, Any] = {
    "max_content_width": 120,
    "terminal_width": 120,
}


def _version_callback(ctx: click.Context, _param: click.Parameter, value: bool) -> None:  # noqa: FBT001
    """Display version information with Rich formatting and exit."""
    if not value or ctx.resilient_parsing:
        return

    console: RichOutputService = get_rich_output()

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

    # Module versions table using standardized layout
    table = create_version_info_table(console)
    if table is not None:
        for module_name, version, description in get_module_versions():
            table.add_row(module_name, version, description)
        console.display_table(table, force=True)

    # System information using utility functions
    console.print("")
    python_version = get_python_version_string()
    platform_info = get_platform_info()
    architecture = get_architecture_info()
    install_path = get_installation_path()

    console.info(
        f"💻 Environment: Python {python_version} on {platform_info} ({architecture})",
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
@click.option(
    "--quiet",
    "-q",
    is_flag=True,
    default=False,
    help="Suppress non-essential output (errors still shown)",
)
@click.pass_context
def cli(
    ctx: click.Context,
    *,
    skip_update_check: bool,
    quiet: bool,
) -> None:
    """Command line interface for the KP Analysis Toolkit."""
    # Store DI settings in context for all subcommands
    ctx.ensure_object(dict)
    ctx.obj["quiet"] = quiet

    # Initialize dependency injection once for all commands
    initialize_dependency_injection(verbose=False, quiet=quiet)

    # Always run version check unless explicitly skipped
    if not skip_update_check:
        check_and_prompt_update()

    # If no subcommand was invoked and no help was requested, show help
    if ctx.invoked_subcommand is None:
        console = get_rich_output()
        _show_enhanced_help(console)


# Add module commands to the CLI
# Configure option groups for multi-command CLI structure
click.rich_click.OPTION_GROUPS = getattr(click.rich_click, "OPTION_GROUPS", {})

# Scripts command option groups
click.rich_click.OPTION_GROUPS["scripts"] = [
    {
        "name": "Configuration & Input",
        "options": ["--conf", "--start-dir", "--filespec"],
    },
    {
        "name": "Information Options",
        "options": [
            "--list-audit-configs",
            "--list-sections",
            "--list-source-files",
            "--list-systems",
        ],
    },
    {
        "name": "Output & Control",
        "options": ["--out-path", "--verbose"],
    },
    {
        "name": "Information & Control",
        "options": ["--version"],
    },
]

# RTF-to-text command option groups
click.rich_click.OPTION_GROUPS["rtf-to-text"] = [
    {
        "name": "Input & Processing Options",
        "options": ["--in-file", "--start-dir"],
    },
    {
        "name": "Information & Control",
        "options": ["--version"],
    },
]

# Nipper command option groups
click.rich_click.OPTION_GROUPS["nipper"] = [
    {
        "name": "Input & Processing Options",
        "options": ["--in-file", "--start-dir"],
    },
    {
        "name": "Information & Control",
        "options": ["--version"],
    },
]

cli.add_command(scripts_process_command_line, name="scripts")
cli.add_command(nipper_process_command_line, name="nipper")
cli.add_command(rtf_process_command_line, name="rtf-to-text")


def _show_enhanced_help(console: RichOutputService) -> None:
    """Show enhanced help using Rich formatting."""
    console.header("🔧 KP Analysis Toolkit")
    console.print("")
    console.info("A comprehensive toolkit for security analysis and data processing.")
    console.print("")

    # Create a table for available commands
    commands = [
        ("scripts", "Process collector script results files (formerly adv-searchfor)"),
        (
            "nipper",
            "Process a Nipper CSV file and expand it into a more readable format",
        ),
        ("rtf-to-text", "Convert RTF files to plain text format with ASCII encoding"),
    ]

    table = create_commands_help_table(console, commands)
    if table is not None:  # Not in quiet mode
        console.display_table(table)

    console.print("")
    console.info(
        "Use 'kpat_cli <command> --help' for more information on a specific command.",
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
    command_func: Callable[..., None],
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
