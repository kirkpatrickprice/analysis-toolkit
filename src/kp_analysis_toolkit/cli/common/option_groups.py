"""
Option grouping utilities for rich-click help display.

This module provides utilities to configure rich-click option groups for
consistent help text formatting across all CLI commands.
"""

from collections.abc import Callable
from typing import Any, TypeVar

import rich_click as click

# Type alias for option group structure
OptionGroupDict = dict[str, Any]

F = TypeVar("F", bound=Callable[..., Any])


def command_option_groups(command_name: str) -> Callable[[F], F]:
    """
    Decorator to configure option groups for a command after it's created.

    Args:
        command_name: The name of the command to configure groups for

    Example:
        @command_option_groups("scripts")
        @click.command(name="scripts")
        def scripts_command():
            pass

    """

    def decorator(func: F) -> F:
        # Apply option groups to this specific command
        _setup_option_groups_for_command(command_name)
        return func

    return decorator


def _setup_option_groups_for_command(command_name: str) -> None:
    """
    Internal function to set up option groups for a command.

    Note: Rich-click option grouping currently doesn't work with multi-command
    CLI structures (Click Groups) in version 1.8.9. This configuration is ready
    for future use when the issue is resolved or a workaround is found.
    """
    # Standard option groups for most commands
    standard_groups = [
        {
            "name": "Input & Processing Options",
            "options": ["--in-file", "--start-dir"],
        },
        {
            "name": "Information & Control",
            "options": ["--version"],
        },
    ]

    # Special handling for specific commands
    if command_name == "scripts":
        script_groups = [
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
        # Ensure we have the OPTION_GROUPS dict initialized
        if not hasattr(click.rich_click, "OPTION_GROUPS"):
            click.rich_click.OPTION_GROUPS = {}
        click.rich_click.OPTION_GROUPS[command_name] = script_groups  # type: ignore[assignment]
    else:
        # Use standard grouping for most commands
        if not hasattr(click.rich_click, "OPTION_GROUPS"):
            click.rich_click.OPTION_GROUPS = {}
        click.rich_click.OPTION_GROUPS[command_name] = standard_groups  # type: ignore[assignment]


def setup_command_option_groups(command_name: str) -> None:
    """
    Configure option groups for a specific command using rich-click.

    Args:
        command_name: The name of the command to configure groups for

    Example:
        setup_command_option_groups("rtf-to-text")

    """
    # Call the internal function for backwards compatibility
    _setup_option_groups_for_command(command_name)


def setup_global_option_groups() -> None:
    """
    Configure option groups for all commands using wildcards.

    This provides a fallback for commands that don't have specific grouping.
    NOTE: This should only be called BEFORE specific command groups are set.
    """
    # Global wildcard groups for any command that doesn't have specific grouping
    if not hasattr(click.rich_click, "OPTION_GROUPS"):
        click.rich_click.OPTION_GROUPS = {}

    # Only set wildcards if they don't already exist
    if "*" not in click.rich_click.OPTION_GROUPS:
        click.rich_click.OPTION_GROUPS["*"] = [
            {
                "name": "File Processing Options",
                "options": ["--in-file", "--start-dir", "--filespec", "--conf"],
            },
            {
                "name": "Output Options",
                "options": ["--out-path", "--verbose"],
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
                "name": "Standard Options",
                "options": ["--version", "--help"],
            },
        ]
