import sys
from pathlib import Path

import rich_click as click

from kp_analysis_toolkit.nipper_expander import __version__ as nipper_expander_version
from kp_analysis_toolkit.nipper_expander.models.program_config import ProgramConfig
from kp_analysis_toolkit.nipper_expander.process_nipper import process_nipper_csv
from kp_analysis_toolkit.utils.rich_output import RichOutput, get_rich_output


@click.command(name="nipper")
@click.version_option(
    version=nipper_expander_version,
    prog_name="kpat_cli scripts",
    message="%(prog)s version %(version)s",
)
@click.option(
    "_infile",
    "--in-file",
    "-f",
    default=None,
    help="Input file to process. If not specified, will search the current directory for CSV files.",
)
@click.option(
    "source_files_path",
    "--start-dir",
    "-d",
    default="./",
    help="Default: the current working directory (./). Specify the path to start searching for files.  Will walk the directory tree from this path.",
)
def process_command_line(_infile: str, source_files_path: str) -> None:
    """Process a Nipper CSV file and expand it into a more readable format."""
    rich_output = get_rich_output()

    # Create a program configuration object
    try:
        program_config: ProgramConfig = ProgramConfig(
            input_file=get_input_file(_infile, source_files_path),
            source_files_path=source_files_path,
        )
    except ValueError as e:
        rich_output.error(f"Error validating configuration: {e}")
        sys.exit(1)

    rich_output.info(f"Processing Nipper CSV file: {program_config.input_file!s}")

    try:
        process_nipper_csv(
            program_config,
        )

        rich_output.success(
            f"Processed {program_config.input_file} and saved results to {program_config.output_file}",
        )
    except (ValueError, FileNotFoundError, KeyError) as e:
        rich_output.error(f"Error processing CSV file: {e}")
        sys.exit(1)


def _create_file_selection_table(dirlist: list[Path], rich_output: RichOutput) -> None:
    """Create and display a Rich table for file selection."""
    table = rich_output.table(
        title="📄 Available CSV Files",
        show_header=True,
        header_style="bold cyan",
        border_style="blue",
    )

    if table is not None:  # Not in quiet mode
        table.add_column("Choice", style="bold white", justify="center", min_width=8)
        table.add_column("File Name", style="cyan", min_width=30)
        table.add_column("Size", style="white", justify="right", min_width=10)

        bytes_per_kb = 1024  # Standard byte to KB conversion

        for index, filename in enumerate(dirlist, 1):
            try:
                file_size = filename.stat().st_size
                size_str = (
                    f"{file_size:,} bytes"
                    if file_size < bytes_per_kb
                    else f"{file_size / bytes_per_kb:.1f} KB"
                )
            except OSError:
                size_str = "Unknown"

            table.add_row(str(index), filename.name, size_str)

        rich_output.display_table(table)
    else:
        # Fallback for quiet mode
        for index, filename in enumerate(dirlist, 1):
            rich_output.print(f"{index:{len(str(len(dirlist)))}d} - {filename}")


def _get_user_choice(dirlist: list[Path], rich_output: RichOutput) -> int:
    """Get user's file choice with input validation."""
    rich_output.print("")  # Empty line for spacing

    choice: int = 0
    while choice < 1 or choice > len(dirlist):
        try:
            choice = int(input("Choose a file or press CTRL-C to quit: "))
        except KeyboardInterrupt:
            rich_output.error("\nExiting...")
            sys.exit()
        except ValueError:
            rich_output.warning("\nSpecify the line number (digits only)\n")
            continue  # Continue the loop instead of exiting

    return choice


def get_input_file(
    infile: str | None,
    source_files_path: str | Path,
) -> Path:
    """
    Get the input file to process.

    If an infile is specified, use it. Otherwise, search the current directory for a CSV file.
    If multiple CSV files are found, prompt the user to select one.
    """
    rich_output = get_rich_output()

    if infile:
        return Path(infile)

    # Get a directory listing of all CSV files in the current directory
    source_files_path = Path(source_files_path).resolve()
    dirlist: list[Path] = [
        Path(source_files_path / f) for f in source_files_path.glob("*.csv")
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
