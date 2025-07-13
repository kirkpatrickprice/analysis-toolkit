import sys
from pathlib import Path

from kp_analysis_toolkit.cli.utils.system_utils import get_file_size
from kp_analysis_toolkit.cli.utils.table_layouts import create_file_selection_table
from kp_analysis_toolkit.core.containers.application import container
from kp_analysis_toolkit.core.services.rich_output import RichOutputService


def get_input_file(
    infile: str | None,
    source_files_path: str | Path,
    file_pattern: str = "*.csv",
    file_type_description: str = "CSV",
    *,
    include_process_all_option: bool = False,
) -> Path | None:
    """
    Get the input file to process.

    If an infile is specified, use it. Otherwise, search the current directory for files matching the pattern.
    If multiple files are found, prompt the user to select one.

    Args:
        infile: Specific file path if provided
        source_files_path: Directory to search for files
        file_pattern: Glob pattern to match files (default: "*.csv")
        file_type_description: Human-readable description of file type for error messages
        include_process_all_option: Whether to include "process all files" option in the menu

    Returns:
        Path to selected file, or None if "process all files" was selected

    """
    rich_output: RichOutputService = container.core.rich_output()

    if infile:
        return Path(infile)

    # Get a directory listing of all files matching the pattern
    source_files_path = Path(source_files_path).resolve()
    dirlist: list[Path] = [
        Path(source_files_path / f) for f in source_files_path.glob(file_pattern)
    ]

    if len(dirlist) == 0:
        error_msg = f"No {file_type_description} files found in {source_files_path!s}."
        raise ValueError(error_msg)

    if len(dirlist) == 1 and not include_process_all_option:
        rich_output.debug(
            f"Auto-selecting the only {file_type_description} file found: {dirlist[0]}",
        )
        return dirlist[0]

    # Multiple files found or process all option enabled - create an interactive selection menu
    rich_output.warning(
        f"Multiple {file_type_description} files found. Choose from below.",
    )

    title = f"Available {file_type_description} Files"
    _create_file_selection_table(
        dirlist,
        rich_output,
        title,
        include_process_all_option=include_process_all_option,
    )
    choice = _get_user_choice(
        dirlist,
        rich_output,
        include_process_all_option=include_process_all_option,
    )

    if include_process_all_option and choice == len(dirlist) + 1:
        return None  # Sentinel value indicating "process all files"

    return dirlist[choice - 1]


def _create_file_selection_table(
    dirlist: list[Path],
    rich_output: RichOutputService,
    title: str,
    *,
    include_process_all_option: bool = False,
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

        # Add "process all files" option if requested
        if include_process_all_option:
            table.add_row(
                str(len(dirlist) + 1),
                "[bold yellow]Process all files[/bold yellow]",
                "",
            )

        rich_output.display_table(table)
    else:
        # Fallback for quiet mode
        for index, filename in enumerate(dirlist, 1):
            rich_output.print(f"{index:{len(str(len(dirlist)))}d} - {filename}")

        # Add "process all files" option if requested
        if include_process_all_option:
            rich_output.print(f"{len(dirlist) + 1} - Process all files")


def _get_user_choice(
    dirlist: list[Path],
    rich_output: RichOutputService,
    *,
    include_process_all_option: bool = False,
    prompt_message: str | None = None,
) -> int:
    """Get user's file choice with input validation."""
    rich_output.print("")  # Empty line for spacing

    max_choice = len(dirlist) + (1 if include_process_all_option else 0)

    if prompt_message is None:
        if include_process_all_option:
            prompt_message = (
                "Choose a file, select 'all files', or press CTRL-C to quit: "
            )
        else:
            prompt_message = "Choose a file (or CTRL-C to quit): "

    choice: int = 0
    while choice < 1 or choice > max_choice:
        try:
            choice = int(input(prompt_message))
        except KeyboardInterrupt:
            rich_output.error("\nExiting...")
            sys.exit()
        except ValueError:
            rich_output.warning("\nSpecify the line number (digits only)\n")
            continue  # Continue the loop instead of exiting

    return choice
