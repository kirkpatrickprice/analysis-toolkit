import sys
from pathlib import Path

import rich_click as click

from kp_analysis_toolkit.rtf_to_text import __version__ as rtf_to_text_version
from kp_analysis_toolkit.rtf_to_text.models.program_config import ProgramConfig
from kp_analysis_toolkit.rtf_to_text.process_rtf import process_rtf_file
from kp_analysis_toolkit.utils.rich_output import get_rich_output


@click.command(name="rtf-to-text")
@click.version_option(
    version=rtf_to_text_version,
    prog_name="kpat_cli rtf-to-text",
    message="%(prog)s version %(version)s",
)
@click.option(
    "_infile",
    "--in-file",
    "-f",
    default=None,
    help="Input RTF file to process. If not specified, will search the current directory for RTF files.",
)
@click.option(
    "source_files_path",
    "--start-dir",
    "-d",
    default="./",
    help="Default: the current working directory (./). Specify the path to start searching for files. Will walk the directory tree from this path.",
)
def process_command_line(_infile: str, source_files_path: str) -> None:
    """Convert RTF files to plain text format with ASCII encoding."""
    # Get the rich output console
    console = get_rich_output()

    # Create a program configuration object
    try:
        program_config: ProgramConfig = ProgramConfig(
            input_file=get_input_file(_infile, source_files_path),
            source_files_path=source_files_path,
        )
    except ValueError as e:
        console.error(f"Error validating configuration: {e}")
        sys.exit(1)

    console.info(f"Converting RTF file: {program_config.input_file!s}")

    try:
        process_rtf_file(program_config)

        console.success(
            f"Converted {program_config.input_file} and saved results to {program_config.output_file}",
        )
    except (ValueError, FileNotFoundError, OSError) as e:
        console.error(f"Error processing RTF file: {e}")
        sys.exit(1)


def get_input_file(
    infile: str | None,
    source_files_path: str | Path,
) -> Path:
    """
    Get the input file to process.

    If an infile is specified, use it. Otherwise, search the current directory for an RTF file.
    If multiple RTF files are found, prompt the user to select one.
    """
    console = get_rich_output()

    if infile:
        return Path(infile)
    # Get a directory listing of all RTF files in the current directory
    source_files_path = Path(source_files_path).resolve()
    dirlist: list[Path] = [
        Path(source_files_path / f) for f in source_files_path.glob("*.rtf")
    ]
    if len(dirlist) == 0:
        error_msg = f"No RTF files found in {source_files_path!s}."
        raise ValueError(error_msg)
    if len(dirlist) == 1:
        return dirlist[0]

    # If more than one RTF file is found, display menu and get user choice
    console.warning(
        'Multiple RTF files found. Use the "--in-file <filename>" option to specify the input file or choose from below.',
    )

    # Create a table for file selection
    from rich.table import Table

    table = Table(
        title="Available RTF Files",
        show_header=True,
        header_style="bold blue",
    )
    table.add_column("Option", style="cyan", width=8)
    table.add_column("Filename", style="green")

    for index, filename in enumerate(dirlist, 1):
        table.add_row(str(index), str(filename.name))

    # Add option to process all files
    table.add_row(str(len(dirlist) + 1), "[bold yellow]Process all files[/bold yellow]")

    console.print(table)

    choice: int = 0
    while choice < 1 or choice > len(dirlist) + 1:
        try:
            choice = int(
                input("Choose a file, select 'all files', or press CTRL-C to quit: "),
            )
        except KeyboardInterrupt:
            console.error("Exiting...")
            sys.exit()
        except ValueError:
            console.warning("Specify the line number (digits only)")

    if choice == len(dirlist) + 1:
        # Process all files
        _process_all_files(dirlist)
        sys.exit(0)

    return dirlist[choice - 1]


def _process_all_files(file_list: list[Path]) -> None:
    """Process all RTF files in the list."""
    console = get_rich_output()

    total_files = len(file_list)
    successful = 0
    failed = 0

    console.info(f"Processing {total_files} RTF files...")

    # Create progress bar
    with console.progress() as progress:
        task = progress.add_task("Converting RTF files...", total=total_files)

        for file_path in file_list:
            try:
                program_config = ProgramConfig(
                    input_file=file_path,
                    source_files_path=file_path.parent,
                )
                process_rtf_file(program_config)
                console.success(
                    f"Converted: {file_path.name} -> {program_config.output_file.name}",
                )
                successful += 1
            except (ValueError, FileNotFoundError, OSError) as e:
                console.error(f"Failed to convert {file_path.name}: {e}")
                failed += 1

            progress.update(task, advance=1)

    # Display summary
    console.info(f"Processing complete: {successful} successful, {failed} failed")
