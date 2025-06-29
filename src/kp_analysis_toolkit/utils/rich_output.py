"""
Rich-based console output utilities for the KP Analysis Toolkit.

This module provides consistent, beautiful formatting for all console output
across the toolkit including messages, progress bars, tables, and panels.
"""

from __future__ import annotations

from contextlib import contextmanager
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any

from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from rich.table import Table
from rich.text import Text
from rich.tree import Tree

if TYPE_CHECKING:
    from collections.abc import Generator, Iterable


class MessageType(Enum):
    """Types of messages for consistent styling."""

    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    DEBUG = "debug"
    HEADER = "header"
    SUBHEADER = "subheader"


class RichOutput:
    """Rich-based console output manager for the KP Analysis Toolkit."""

    def __init__(self, *, verbose: bool = False, quiet: bool = False) -> None:
        """
        Initialize the Rich output manager.

        Args:
            verbose: Enable verbose output
            quiet: Suppress non-essential output

        """
        self.console = Console(
            stderr=False,
            force_terminal=True,
            width=120,
        )
        self.error_console = Console(
            stderr=True,
            force_terminal=True,
            width=120,
        )
        self.verbose = verbose
        self.quiet = quiet

        # Message styling configuration
        self._styles = {
            MessageType.INFO: {"style": "blue", "prefix": "🔵 "},
            MessageType.SUCCESS: {"style": "bold green", "prefix": "✅ "},
            MessageType.WARNING: {"style": "bold yellow", "prefix": "⚠️ "},
            MessageType.ERROR: {"style": "bold red", "prefix": "❌ "},
            MessageType.DEBUG: {"style": "dim white", "prefix": "🔍 "},
            MessageType.HEADER: {"style": "bold blue", "prefix": "📋 "},
            MessageType.SUBHEADER: {"style": "bold white", "prefix": "▸ "},
        }

    def message(
        self,
        text: str,
        message_type: MessageType = MessageType.INFO,
        *,
        force: bool = False,
    ) -> None:
        """
        Display a formatted message.

        Args:
            text: Message text to display
            message_type: Type of message for styling
            force: Show message even in quiet mode

        """
        if self.quiet and not force:
            return

        if message_type == MessageType.DEBUG and not self.verbose:
            return

        style_config = self._styles[message_type]
        prefix = style_config["prefix"]
        style = style_config["style"]

        console = (
            self.error_console if message_type == MessageType.ERROR else self.console
        )
        console.print(f"{prefix}{text}", style=style)

    def info(self, text: str, *, force: bool = False) -> None:
        """Display an info message."""
        self.message(text, MessageType.INFO, force=force)

    def success(self, text: str, *, force: bool = False) -> None:
        """Display a success message."""
        self.message(text, MessageType.SUCCESS, force=force)

    def warning(self, text: str, *, force: bool = False) -> None:
        """Display a warning message."""
        self.message(text, MessageType.WARNING, force=force)

    def error(self, text: str, *, force: bool = True) -> None:
        """Display an error message."""
        self.message(text, MessageType.ERROR, force=force)

    def debug(self, text: str) -> None:
        """Display a debug message (only in verbose mode)."""
        self.message(text, MessageType.DEBUG)

    def header(self, text: str, *, force: bool = False) -> None:
        """Display a header message."""
        self.message(text, MessageType.HEADER, force=force)

    def subheader(self, text: str, *, force: bool = False) -> None:
        """Display a subheader message."""
        self.message(text, MessageType.SUBHEADER, force=force)

    def print(self, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401
        """Print directly to console (respects quiet mode)."""
        if not self.quiet:
            self.console.print(*args, **kwargs)

    def print_error(self, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401
        """Print directly to error console (always shown)."""
        self.error_console.print(*args, **kwargs)

    def panel(  # noqa: PLR0913
        self,
        content: str | Table | Tree,
        *,
        title: str | None = None,
        subtitle: str | None = None,
        border_style: str = "blue",
        expand: bool = True,
        force: bool = False,
    ) -> None:
        """
        Display content in a Rich panel.

        Args:
            content: Content to display in the panel
            title: Panel title
            subtitle: Panel subtitle
            border_style: Border color/style
            expand: Whether panel should expand to full width
            force: Show panel even in quiet mode

        """
        if self.quiet and not force:
            return

        panel = Panel(
            content,
            title=title,
            subtitle=subtitle,
            border_style=border_style,
            expand=expand,
            padding=(1, 2),
        )
        self.console.print(panel)

    def table(  # noqa: PLR0913
        self,
        title: str | None = None,
        *,
        show_header: bool = True,
        header_style: str = "bold cyan",
        border_style: str = "blue",
        expand: bool = True,
        force: bool = False,
    ) -> Table | None:
        """
        Create a Rich table with consistent styling.

        Args:
            title: Table title
            show_header: Whether to show column headers
            header_style: Style for column headers
            border_style: Border color/style
            expand: Whether table should expand to full width
            force: Show table even in quiet mode

        Returns:
            Configured Rich Table object

        """
        if self.quiet and not force:
            return None

        return Table(
            title=title,
            show_header=show_header,
            header_style=header_style,
            border_style=border_style,
            expand=expand,
            title_style="bold blue",
        )

    def display_table(self, table: Table, *, force: bool = False) -> None:
        """
        Display a Rich table.

        Args:
            table: Rich Table to display
            force: Show table even in quiet mode

        """
        if self.quiet and not force:
            return
        self.console.print(table)

    def tree(self, label: str, *, guide_style: str = "cyan") -> Tree:
        """
        Create a Rich tree with consistent styling.

        Args:
            label: Root label for the tree
            guide_style: Style for tree guide lines

        Returns:
            Configured Rich Tree object

        """
        return Tree(label, guide_style=guide_style)

    def display_tree(self, tree: Tree, *, force: bool = False) -> None:
        """
        Display a Rich tree.

        Args:
            tree: Rich Tree to display
            force: Show tree even in quiet mode

        """
        if self.quiet and not force:
            return
        self.console.print(tree)

    @contextmanager
    def progress(
        self,
        *,
        show_eta: bool = True,
        show_percentage: bool = True,
        show_time_elapsed: bool = True,
        disable: bool = False,
    ) -> Generator[Progress, None, None]:
        """
        Context manager for Rich progress bars.

        Args:
            show_eta: Show estimated time remaining
            show_percentage: Show percentage completion
            show_time_elapsed: Show elapsed time
            disable: Disable progress bar (useful for quiet mode)

        Yields:
            Rich Progress object for task management

        """
        if self.quiet:
            disable = True

        columns = [
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
        ]

        if show_percentage:
            columns.append(MofNCompleteColumn())

        if show_time_elapsed:
            columns.append(TimeElapsedColumn())

        if show_eta:
            columns.append(TimeRemainingColumn())

        with Progress(
            *columns,
            console=self.console,
            disable=disable,
        ) as progress:
            yield progress

    def simple_progress(
        self,
        items: Iterable[Any],
        description: str = "Processing...",
        *,
        show_eta: bool = True,
        show_percentage: bool = True,
    ) -> Generator[Any, None, None]:
        """Simple progress bar for iterating over items."""
        items_list = list(items)

        with self.progress(
            show_eta=show_eta,
            show_percentage=show_percentage,
        ) as progress:
            # Use description for task - this is the intended behavior
            task = progress.add_task(description, total=len(items_list))

            for item in items_list:
                yield item
                progress.advance(task)

    def format_path(self, path: str | Path, max_length: int = 50) -> Text:
        """
        Format a file path for display with intelligent truncation.

        Args:
            path: File path to format
            max_length: Maximum display length

        Returns:
            Rich Text object with formatted path

        """
        path_str = str(path)

        if len(path_str) <= max_length:
            return Text(path_str, style="cyan")

        # Preserve filename if possible
        path_obj = Path(path_str)
        filename = path_obj.name

        if len(filename) < max_length - 10:
            remaining = max_length - len(filename) - 7  # 7 for " ... "
            if remaining > 0:
                truncated = f"{path_str[:remaining]} ... {filename}"
                return Text(truncated, style="cyan")

        # Fallback to simple truncation
        start_chars = (max_length - 5) // 2
        end_chars = max_length - start_chars - 5
        truncated = f"{path_str[:start_chars]} ... {path_str[-end_chars:]}"
        return Text(truncated, style="cyan")

    def format_value(self, value: Any, max_length: int = 50) -> Text:  # noqa: ANN401
        """
        Format a value for display with appropriate styling.

        Args:
            value: Value to format
            max_length: Maximum display length

        Returns:
            Rich Text object with formatted value

        """
        # Handle None values
        if value is None:
            return Text("(none)", style="dim")

        # Handle boolean values
        if isinstance(value, bool):
            return Text(str(value), style="bold green" if value else "bold red")

        # Handle path-like values
        if isinstance(value, Path | str) and ("/" in str(value) or "\\" in str(value)):
            return self.format_path(value, max_length)

        # Handle collections (but not strings)
        if isinstance(value, list | tuple | set) and not isinstance(value, str):
            return self._format_collection(value, max_length)

        # Handle string values
        return self._format_string(str(value), max_length)

    def _format_collection(self, value: list | tuple | set, max_length: int) -> Text:
        """Format collection values with appropriate styling."""
        if len(value) == 0:
            return Text("(empty)", style="dim")
        if len(value) == 1:
            item_text = self.format_value(next(iter(value)), max_length - 10)
            return Text(f"[{item_text}]", style="yellow")
        return Text(f"[{len(value)} items]", style="yellow")

    def _format_string(self, str_value: str, max_length: int) -> Text:
        """Format string values with truncation if needed."""
        if len(str_value) <= max_length:
            return Text(str_value)

        # Truncate long strings
        start_chars = (max_length - 5) // 2
        end_chars = max_length - start_chars - 5
        truncated = f"{str_value[:start_chars]} ... {str_value[-end_chars:]}"
        return Text(truncated)

    def configuration_table(
        self,
        config_dict: dict[str, Any],
        original_dict: dict[str, Any] | None = None,
        *,
        title: str = "Configuration",
        force: bool = False,
    ) -> None:
        """
        Display a configuration table with Rich formatting.

        Args:
            config_dict: Configuration dictionary to display
            original_dict: Original values before processing (optional)
            title: Table title
            force: Show table even in quiet mode

        """
        if self.quiet and not force:
            return

        table = self.table(
            title=f"📋 {title}",
            show_header=True,
            header_style="bold cyan",
            border_style="blue",
        )

        # Add columns
        table.add_column("Parameter", style="bold white", min_width=20)
        if original_dict:
            table.add_column("Original Value", style="yellow", min_width=25)
        table.add_column("Effective Value", style="green", min_width=30)
        table.add_column("Type", style="dim white", min_width=10)

        # Add rows
        for key, value in config_dict.items():
            original_value = (
                original_dict.get(key, "(computed)") if original_dict else None
            )
            value_type = type(value).__name__

            row_data = [key]
            if original_dict:
                if original_value == "(computed)":
                    row_data.append(Text("(computed)", style="italic dim"))
                else:
                    row_data.append(str(self.format_value(original_value, 40)))
            row_data.extend(
                [
                    str(self.format_value(value, 50)),
                    value_type,
                ],
            )

            table.add_row(*row_data)

        # Display in a panel
        self.panel(
            table,
            title=f"[bold]{title}[/bold]",
            border_style="blue",
            force=force,
        )

    def banner(
        self,
        title: str,
        subtitle: str | None = None,
        version: str | None = None,
        *,
        force: bool = False,
    ) -> None:
        """
        Display a branded banner for the application.

        Args:
            title: Main title text
            subtitle: Subtitle text (optional)
            version: Version information (optional)
            force: Show banner even in quiet mode

        """
        if self.quiet and not force:
            return

        content = Text(title, style="bold blue", justify="center")

        if subtitle:
            content.append("\n")
            content.append(subtitle, style="white")

        if version:
            content.append("\n")
            content.append(f"Version {version}", style="dim white")

        self.panel(
            content,
            border_style="blue",
            expand=True,
            force=force,
        )

    def rule(self, title: str | None = None, *, style: str = "blue") -> None:
        """
        Display a horizontal rule with optional title.

        Args:
            title: Optional title for the rule
            style: Rule style/color

        """
        if not self.quiet:
            self.console.rule(title, style=style)


# Global instance for convenience
_rich_output: RichOutput | None = None


def get_rich_output(*, verbose: bool = False, quiet: bool = False) -> RichOutput:
    """Get or create the global RichOutput instance."""
    if "_rich_output" not in globals() or globals()["_rich_output"] is None:
        globals()["_rich_output"] = RichOutput(verbose=verbose, quiet=quiet)
    else:
        # Update settings if provided
        globals()["_rich_output"].verbose = verbose
        globals()["_rich_output"].quiet = quiet

    return globals()["_rich_output"]


def configure_rich_output(*, verbose: bool = False, quiet: bool = False) -> None:
    """Configure the global RichOutput instance settings."""
    get_rich_output(verbose=verbose, quiet=quiet)


# Convenience functions that use the global instance
def info(text: str, *, force: bool = False) -> None:
    """Display an info message."""
    get_rich_output().info(text, force=force)


def success(text: str, *, force: bool = False) -> None:
    """Display a success message."""
    get_rich_output().success(text, force=force)


def warning(text: str, *, force: bool = False) -> None:
    """Display a warning message."""
    get_rich_output().warning(text, force=force)


def error(text: str, *, force: bool = True) -> None:
    """Display an error message."""
    get_rich_output().error(text, force=force)


def debug(text: str) -> None:
    """Display a debug message."""
    get_rich_output().debug(text)


def header(text: str, *, force: bool = False) -> None:
    """Display a header message."""
    get_rich_output().header(text, force=force)


def subheader(text: str, *, force: bool = False) -> None:
    """Display a subheader message."""
    get_rich_output().subheader(text, force=force)
