"""
Table layout utilities for consistent CLI table formatting.

This module provides standardized table creation functions to ensure
consistent styling and reduce code duplication across CLI interfaces.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rich.table import Table

    from kp_analysis_toolkit.core.services.rich_output import RichOutputService


def create_file_selection_table(
    rich_output: "RichOutputService",
    *,
    title: str = "File Selection",
    include_size: bool = True,
    include_choice_column: bool = True,
) -> "Table | None":
    """
    Create a standardized file selection table layout.

    Args:
        rich_output: The RichOutputService instance
        title: Table title
        include_size: Whether to include a file size column
        include_choice_column: Whether to include a choice/option column

    Returns:
        Table instance or None if in quiet mode

    """
    table = rich_output.table(
        title=title,
        show_header=True,
        header_style="bold cyan",
        border_style="blue",
    )

    if table is not None:  # Not in quiet mode
        if include_choice_column:
            table.add_column(
                "Choice",
                style="bold white",
                justify="center",
                min_width=8,
            )

        table.add_column(
            "File Name",
            style="cyan",
            min_width=30,
        )

        if include_size:
            table.add_column(
                "Size",
                style="white",
                justify="right",
                min_width=10,
            )

    return table


def create_file_listing_table(
    rich_output: "RichOutputService",
    *,
    title: str = "File Listing",
    file_column_name: str = "File Path",
) -> "Table | None":
    """
    Create a standardized file listing table (no user interaction).

    Args:
        rich_output: The RichOutputService instance
        title: Table title
        file_column_name: Name for the file path/name column

    Returns:
        Table instance or None if in quiet mode

    """
    table = rich_output.table(
        title=title,
        show_header=True,
        header_style="bold cyan",
        border_style="blue",
    )

    if table is not None:  # Not in quiet mode
        table.add_column(
            file_column_name,
            style="cyan",
            min_width=40,
        )

        table.add_column(
            "Size",
            style="white",
            justify="right",
            min_width=10,
        )

    return table


def create_system_info_table(
    rich_output: "RichOutputService",
    *,
    title: str = "System Information",
    include_details: bool = False,
) -> "Table | None":
    """
    Create a standardized system information table layout.

    Args:
        rich_output: The RichOutputService instance
        title: Table title
        include_details: Whether to include a details column for verbose mode

    Returns:
        Table instance or None if in quiet mode

    """
    table = rich_output.table(
        title=title,
        show_header=True,
        header_style="bold cyan",
        border_style="blue",
    )

    if table is not None:  # Not in quiet mode
        table.add_column(
            "System Name",
            style="bold white",
            min_width=25,
        )

        table.add_column(
            "File Hash",
            style="dim white",
            min_width=16,
        )

        if include_details:
            table.add_column(
                "Details",
                style="white",
                min_width=40,
            )

    return table


def create_config_display_table(
    rich_output: "RichOutputService",
    *,
    title: str = "Configuration",
    show_original_values: bool = False,
) -> "Table | None":
    """
    Create a standardized configuration display table layout.

    Args:
        rich_output: The RichOutputService instance
        title: Table title
        show_original_values: Whether to show original and effective values

    Returns:
        Table instance or None if in quiet mode

    """
    table = rich_output.table(
        title=title,
        show_header=True,
        header_style="bold cyan",
        border_style="blue",
    )

    if table is not None:  # Not in quiet mode
        table.add_column(
            "Parameter",
            style="bold white",
            min_width=20,
        )

        if show_original_values:
            table.add_column(
                "Original Value",
                style="yellow",
                min_width=25,
            )

        table.add_column(
            "Effective Value",
            style="green",
            min_width=30,
        )

        table.add_column(
            "Type",
            style="dim white",
            min_width=10,
        )

    return table
