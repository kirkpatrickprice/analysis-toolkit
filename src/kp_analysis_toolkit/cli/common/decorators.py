"""
Shared CLI option decorators for consistent command interfaces.

This module provides reusable Click decorators for common CLI options across
the KP Analysis Toolkit commands. These decorators ensure consistency in option
naming, help text, and behavior while reducing code duplication.
"""

from collections.abc import Callable

import rich_click as click


def module_version_option(
    module_version: str,
    command_name: str,
) -> Callable[[Callable], Callable]:
    """
    Standard version option decorator for CLI commands.

    Args:
        module_version: Version string from the module's __version__
        command_name: Name of the command (e.g., "scripts", "nipper", "rtf-to-text")

    Returns:
        Click decorator for version option

    Example:
        @module_version_option(rtf_to_text_version, "rtf-to-text")
        @click.command()
        def my_command():
            pass

    """
    return click.version_option(
        version=module_version,
        prog_name=f"kpat_cli {command_name}",
        message="%(prog)s version %(version)s",
    )


def start_directory_option(
    param_name: str = "source_files_path",
    default: str = "./",
    help_text: str = "Default: the current working directory (./). Specify the path to start searching for files. Will walk the directory tree from this path.",
) -> Callable[[Callable], Callable]:
    """
    Standard start directory option for file processing commands.

    Args:
        param_name: Parameter name for the option (default: "source_files_path")
        default: Default directory path (default: "./")
        help_text: Help text for the option

    Returns:
        Click decorator for start directory option

    Example:
        @start_directory_option()
        @click.command()
        def my_command(source_files_path: str):
            pass

    """
    return click.option(
        "--start-dir",
        "-d",
        param_name,
        default=default,
        help=help_text,
    )


def input_file_option(
    param_name: str = "_infile",
    file_type: str = "file",
    file_extension: str | None = None,
    help_template: str = "Input {file_type} to process. If not specified, will search the current directory for {file_pattern} files.",
) -> Callable[[Callable], Callable]:
    """
    Standard input file option for file processing commands.

    Args:
        param_name: Parameter name for the option (default: "_infile")
        file_type: Type of file being processed (e.g., "RTF", "CSV")
        file_extension: File extension pattern (defaults to file_type if not provided)
        help_template: Template for help text with {file_type} and {file_pattern} placeholders

    Returns:
        Click decorator for input file option

    Example:
        @input_file_option(file_type="RTF")
        @click.command()
        def my_command(_infile: str):
            pass

    """
    file_pattern = file_extension or file_type
    help_text = help_template.format(file_type=file_type, file_pattern=file_pattern)

    return click.option(
        "--in-file",
        "-f",
        param_name,
        default=None,
        help=help_text,
    )


def output_directory_option(
    param_name: str = "out_path",
    default: str = "results/",
    help_text: str = "Default: results/. Specify the output directory for the results files.",
) -> Callable[[Callable], Callable]:
    """
    Standard output directory option for commands that need explicit output control.

    Args:
        param_name: Parameter name for the option (default: "out_path")
        default: Default output directory (default: "results/")
        help_text: Help text for the option

    Returns:
        Click decorator for output directory option

    Example:
        @output_directory_option()
        @click.command()
        def my_command(out_path: str):
            pass

    """
    return click.option(
        "--out-path",
        "-o",
        param_name,
        default=default,
        help=help_text,
    )


def verbose_option(
    param_name: str = "verbose",
    help_text: str = "Enable verbose output including debug messages",
) -> Callable[[Callable], Callable]:
    """
    Standard verbose option for commands that need detailed output control.

    Args:
        param_name: Parameter name for the option (default: "verbose")
        help_text: Help text for the option

    Returns:
        Click decorator for verbose option

    Example:
        @verbose_option()
        @click.command()
        def my_command(verbose: bool):
            pass

    """
    return click.option(
        "--verbose",
        "-v",
        param_name,
        is_flag=True,
        default=False,
        help=help_text,
    )


# Convenience aliases for backwards compatibility and ease of use
version_option = module_version_option
start_dir_option = start_directory_option
input_option = input_file_option


def grouped_option_decorator(group_name: str) -> Callable[[Callable], Callable]:
    """
    Decorator to add rich-click group metadata to options.

    This is for future enhancement to allow per-option group assignment.

    Args:
        group_name: The name of the group this option belongs to

    Returns:
        Click decorator that adds group metadata

    Example:
        @grouped_option_decorator("Input Options")
        @click.option("--input-file", help="Input file to process")
        def my_command(input_file: str):
            pass

    """
    def decorator(func: Callable) -> Callable:
        if not hasattr(func, "rich_click_group"):
            func.rich_click_group = group_name  # type: ignore[attr-defined]
        return func
    return decorator


def custom_help_option(command_name: str) -> Callable[[Callable], Callable]:
    """
    Decorator that adds custom grouped help display to a command.

    This decorator intercepts --help requests and displays option groups
    in separate Rich panels, working around rich-click's multi-command
    CLI limitation.

    Args:
        command_name: The name of the command for option group lookup

    Returns:
        Click decorator that adds custom help option

    Example:
        @custom_help_option("scripts")
        @click.command(name="scripts")
        def scripts_command():
            pass
    """
    def help_callback(ctx: click.Context, param: click.Parameter, value: bool) -> None:  # noqa: FBT001
        """Callback that displays custom grouped help and exits."""
        if not value or ctx.resilient_parsing:
            return

        # Import here to avoid circular imports
        from kp_analysis_toolkit.cli.common.output_formatting import display_grouped_help

        display_grouped_help(ctx, command_name)
        ctx.exit()

    def decorator(func: Callable) -> Callable:
        # Add the custom help option to the command
        help_option = click.option(
            "--help", "-h",
            is_flag=True,
            expose_value=False,
            is_eager=True,
            callback=help_callback,
            help="Show this message and exit",
        )
        return help_option(func)

    return decorator
