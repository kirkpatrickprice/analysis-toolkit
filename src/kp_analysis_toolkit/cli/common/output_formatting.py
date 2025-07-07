"""
CLI Output Formatting Utilities.

This module provides centralized formatting functions for consistent CLI output
across all commands in the KP Analysis Toolkit.    # Get parameter type information
    type_info = ""
    if hasattr(param, "type") and param.type:
        if isinstance(param.type, click.Choice):
            choices = "|".join(param.type.choices)
            type_info = f" [{choices}]"
        elif param.type.name != "boolean":  # Skip boolean flags
            type_info = f" {param.type.name.upper()}"udes custom help formatting
with option groups, progress displays, and other common output patterns.
"""

from typing import Any

import rich_click as click
from rich.panel import Panel

from kp_analysis_toolkit.utils.rich_output import RichOutputService, get_rich_output


def display_grouped_help(ctx: click.Context, command_name: str) -> None:
    """
    Display help with option groups for a specific command.

    This function provides custom help formatting that displays options in
    grouped panels rather than a single flat list, working around the
    rich-click limitation with multi-command CLI structures.

    Args:
        ctx: Click context for the command
        command_name: Name of the command to show help for

    """
    console = get_rich_output()

    # Show command header with emoji and description
    console.header(f"🔧 {command_name} Command")

    # Show command description
    if ctx.command.short_help:
        console.info(ctx.command.short_help)
    elif ctx.command.help:
        # Use first line of help if short_help is not available
        first_line = ctx.command.help.split("\n")[0].strip()
        console.info(first_line)
    else:
        console.info("No description available")

    console.print("")

    # Show usage information
    console.subheader("Usage:")
    usage = ctx.get_usage()
    console.print(f"  {usage}")
    console.print("")

    # Get option groups for this command
    option_groups = getattr(click.rich_click, "OPTION_GROUPS", {}).get(command_name, [])

    if option_groups:
        # Display each option group as a separate panel
        for group in option_groups:
            display_option_group_panel(console, ctx, group)
    else:
        # Fallback: display all options in a single panel
        display_fallback_options_panel(console, ctx)

    # Show additional information if available
    if ctx.command.epilog:
        console.print("")
        console.subheader("Additional Information:")
        console.print(ctx.command.epilog)


def display_option_group_panel(
    console: RichOutputService,
    ctx: click.Context,
    group: dict[str, Any],
) -> None:
    """
    Display a single option group as a Rich panel.

    Args:
        console: Rich output service instance
        ctx: Click context for the command
        group: Option group configuration dict with 'name' and 'options' keys

    """
    group_name = group.get("name", "Options")
    group_options = group.get("options", [])

    # Build the options content for this group
    options_content = []

    for param in ctx.command.params:
        # Skip if this parameter is not an option
        if not hasattr(param, "opts") or not param.opts:
            continue

        # Check if this parameter matches any option in the group
        param_names = getattr(param, "opts", [])
        if any(opt_name in param_names for opt_name in group_options):
            option_line = format_option_line(param)
            if option_line:
                options_content.append(option_line)

    # Only display the panel if we found matching options
    if options_content:
        # Create panel content
        panel_content = "\n".join(options_content)

        # Create and display the panel
        panel = Panel(
            panel_content,
            title=f"📋 {group_name}",
            title_align="left",
            border_style="blue",
            padding=(0, 1),
        )

        console.print(panel)


def display_fallback_options_panel(
    console: RichOutputService, ctx: click.Context
) -> None:
    """
    Display all options in a single panel when no groups are configured.

    Args:
        console: Rich output service instance
        ctx: Click context for the command

    """
    options_content = []

    for param in ctx.command.params:
        if hasattr(param, "opts") and param.opts:
            option_line = format_option_line(param)
            if option_line:
                options_content.append(option_line)

    if options_content:
        panel_content = "\n".join(options_content)
        panel = Panel(
            panel_content,
            title="📋 Options",
            title_align="left",
            border_style="blue",
            padding=(0, 1),
        )
        console.print(panel)


def format_option_line(param: click.Parameter) -> str | None:
    """
    Format a single option line for display in help panels.

    Args:
        param: Click parameter to format

    Returns:
        Formatted option line or None if parameter should be skipped

    """
    if not hasattr(param, "opts") or not param.opts:
        return None

    # Get the primary option name (usually the long form)
    primary_opt = param.opts[0]

    # Get secondary options (short forms)
    secondary_opts = param.opts[1:] if len(param.opts) > 1 else []

    # Format option names
    opt_display = primary_opt
    if secondary_opts:
        opt_display += f", {', '.join(secondary_opts)}"

    # Get parameter type information
    type_info = ""
    if hasattr(param, "type") and param.type:
        if isinstance(param.type, click.Choice):
            choices = "|".join(param.type.choices)
            type_info = f" [{choices}]"
        elif param.type.name != "boolean":  # Skip boolean flags
            type_info = f" {param.type.name.upper()}"

    # Get help text
    help_text = getattr(param, "help", "") or "No help available"

    # Format the complete line with proper spacing
    # Use consistent width for option names (30 characters)
    opt_part = f"{opt_display}{type_info}"
    return f"  {opt_part:<30} {help_text}"


def create_commands_help_table(
    rich_output: RichOutputService,
    commands: list[tuple[str, str]],
    title: str = "📋 Available Commands",
) -> Any:
    """
    Create standardized table for command help display.

    Args:
        rich_output: Rich output service instance
        commands: List of (command_name, description) tuples
        title: Title for the table

    Returns:
        Rich table object or None if in quiet mode

    """
    table = rich_output.table(
        title=title,
        show_header=True,
        header_style="bold cyan",
        border_style="blue",
    )

    if table is not None:
        table.add_column("Command", style="bold white", min_width=15)
        table.add_column("Description", style="cyan", min_width=50)

        for command_name, description in commands:
            table.add_row(command_name, description)

    return table


def format_verbose_details(
    rich_output: RichOutputService,
    data_dict: dict[str, Any],
    max_items: int = 3,
    max_value_length: int = 60,
) -> str:
    """
    Format dictionary data for verbose display with truncation.

    Args:
        rich_output: Rich output service for value formatting
        data_dict: Dictionary to format
        max_items: Maximum number of items to show
        max_value_length: Maximum length for each value

    Returns:
        Formatted string with details

    """
    details = []
    for key, value in data_dict.items():
        formatted_value = rich_output.format_value(value, max_value_length)
        details.append(f"{key}: {formatted_value}")

    details_text = "\n".join(details[:max_items])
    if len(data_dict) > max_items:
        remaining = len(data_dict) - max_items
        details_text += f"\n... and {remaining} more"

    return details_text


def format_hash_display(
    hash_value: str,
    display_length: int = 16,
    suffix: str = "...",
) -> str:
    """
    Format hash values for consistent display truncation.

    Args:
        hash_value: The hash string to format
        display_length: Number of characters to show
        suffix: Suffix to append when truncated

    Returns:
        Formatted hash string

    """
    if len(hash_value) <= display_length:
        return hash_value
    return hash_value[:display_length] + suffix
