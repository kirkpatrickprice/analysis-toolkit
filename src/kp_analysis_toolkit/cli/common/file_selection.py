import sys
from pathlib import Path

from kp_analysis_toolkit.cli.utils.system_utils import get_file_size
from kp_analysis_toolkit.cli.utils.table_layouts import create_file_selection_table
from kp_analysis_toolkit.utils.rich_output import (
    RichOutputService,
    get_rich_output,
)


def get_input_file(
    infile: str | None,
    source_files_path: str | Path,
    file_pattern: str = "*.csv",
) -> Path:
    """
    Get the input file to process.

    If an infile is specified, use it. Otherwise, search the current directory for a CSV file.
    If multiple CSV files are found, prompt the user to select one.
    """
    rich_output: RichOutputService = get_rich_output()

    if infile:
        return Path(infile)

    # Get a directory listing of all CSV files in the current directory
    source_files_path = Path(source_files_path).resolve()
    dirlist: list[Path] = [
        Path(source_files_path / f) for f in source_files_path.glob(file_pattern)
    ]

    if len(dirlist) == 0:
        error_msg = f"No CSV files found in {source_files_path!s}."
        raise ValueError(error_msg)

    if len(dirlist) == 1:
        rich_output.debug(f"Auto-selecting the only CSV file found: {dirlist[0]}")
        return dirlist[0]

    # Multiple CSV files found - create an interactive selection menu
    rich_output.warning(
        'Multiple CSV files found. Use the "--in-file <filename>" option to specify the input file or choose from below.',
    )

    _create_file_selection_table(dirlist, rich_output)
    choice = _get_user_choice(dirlist, rich_output)

    return dirlist[choice - 1]


def _create_file_selection_table(
    dirlist: list[Path],
    rich_output: RichOutputService,
    title: str,
) -> None:
    """Create and display a Rich table for file selection."""
    table = create_file_selection_table(
        rich_output,
        title=title,
        include_size=True,
        include_choice_column=True,
    )

    if table is not None:  # Not in quiet mode
        for index, filename in enumerate(dirlist, 1):
            size_str: str = get_file_size(filename)
            table.add_row(str(index), filename.name, size_str)

        rich_output.display_table(table)
    else:
        # Fallback for quiet mode
        for index, filename in enumerate(dirlist, 1):
            rich_output.print(f"{index:{len(str(len(dirlist)))}d} - {filename}")


def _get_user_choice(
    dirlist: list[Path],
    rich_output: RichOutputService,
    prompt_message: str,
) -> int:
    """Get user's file choice with input validation."""
    rich_output.print("")  # Empty line for spacing

    choice: int = 0
    while choice < 1 or choice > len(dirlist):
        try:
            choice = int(
                input(prompt_message or "Choose a file (or CTRL-C to quit) : "),
            )
        except KeyboardInterrupt:
            rich_output.error("\nExiting...")
            sys.exit()
        except ValueError:
            rich_output.warning("\nSpecify the line number (digits only)\n")
            continue  # Continue the loop instead of exiting

    return choice
