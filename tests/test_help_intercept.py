#!/usr/bin/env python3
"""
Test script to explore Click help callback interception.

This tests if we can intercept --help requests and apply custom formatting
with our option groups to work around the rich-click multi-command limitation.
"""

import rich_click as click

from kp_analysis_toolkit.cli.common.option_groups import (
    _setup_option_groups_for_command,
)
from kp_analysis_toolkit.utils.rich_output import get_rich_output


def custom_help_callback(
    ctx: click.Context, param: click.Parameter, value: bool
) -> None:
    """Custom help callback that intercepts --help and shows grouped options."""
    if not value or ctx.resilient_parsing:
        return

    console = get_rich_output()
    command_name = ctx.info_name

    console.header(f"🔧 {command_name} Command Help")
    console.print("")

    # Get the option groups for this command
    _setup_option_groups_for_command(command_name)
    option_groups = getattr(click.rich_click, "OPTION_GROUPS", {}).get(command_name, [])

    if option_groups:
        console.info(f"Found {len(option_groups)} option groups for '{command_name}'")

        for group in option_groups:
            group_name = group.get("name", "Options")
            options = group.get("options", [])

            console.print("")
            console.subheader(f"📋 {group_name}")

            # Find matching options from the command
            for param in ctx.command.params:
                # Check if this parameter matches any option in the group
                param_names = getattr(param, "opts", [])
                if any(opt_name in param_names for opt_name in options):
                    help_text = getattr(param, "help", "No help available")
                    primary_name = param_names[0] if param_names else str(param.name)
                    console.print(f"  {primary_name:<20} {help_text}")
    else:
        console.warning(f"No option groups found for '{command_name}'")
        # Fall back to standard help
        console.print(ctx.get_help())

    ctx.exit()


@click.command(name="test-scripts")
@click.option("--conf", "-c", default="audit-all.yaml", help="Configuration file")
@click.option("--start-dir", "-d", default="./", help="Starting directory")
@click.option("--filespec", "-f", default="*.txt", help="File specification")
@click.option("--out-path", "-o", default="results/", help="Output directory")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
@click.option("--list-audit-configs", is_flag=True, help="List audit configs")
@click.option("--list-sections", is_flag=True, help="List sections")
@click.option("--version", is_flag=True, help="Show version")
@click.option(
    "--help",
    "-h",
    is_flag=True,
    expose_value=False,
    is_eager=True,
    callback=custom_help_callback,
    help="Show this message and exit",
)
def test_scripts_command(**kwargs):
    """Test command with custom help callback to demonstrate option grouping."""
    print("Command executed!")


if __name__ == "__main__":
    test_scripts_command()
