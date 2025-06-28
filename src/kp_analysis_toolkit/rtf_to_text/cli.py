import sys
from pathlib import Path

import click

from kp_analysis_toolkit.rtf_to_text import __version__ as rtf_to_text_version
from kp_analysis_toolkit.rtf_to_text.models.program_config import ProgramConfig
from kp_analysis_toolkit.rtf_to_text.process_rtf import process_rtf_file


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
    # Create a program configuration object
    try:
        program_config: ProgramConfig = ProgramConfig(
            input_file=get_input_file(_infile, source_files_path),
            source_files_path=source_files_path,
        )
    except ValueError as e:
        click.secho(f"Error validating configuration: {e}", fg="red")
        sys.exit(1)

    click.echo(
        f"Converting RTF file: {program_config.input_file!s}",
    )

    try:
        process_rtf_file(program_config)

        click.echo(
            f"Converted {program_config.input_file} and saved results to {program_config.output_file}",
        )
    except (ValueError, FileNotFoundError, OSError) as e:
        click.secho(f"Error processing RTF file: {e}", fg="red")
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
    # if more than one RTF file is found, print the results and provide the user a choice
    click.secho(
        'Multiple RTF files found. Use the "--in-file <filename>" option to specify the input file or choose from below.',
        fg="yellow",
    )
    for index, filename in enumerate(dirlist, 1):
        click.echo(
            f"{index:{len(str(len(dirlist)))}d} - {filename}",
        )  # Padding for alignment
    click.echo()

    # Add option to process all files
    click.echo(f"{len(dirlist) + 1} - Process all files")
    click.echo()

    choice: int = 0
    while choice < 1 or choice > len(dirlist) + 1:
        try:
            choice = int(
                input("Choose a file, select 'all files', or press CTRL-C to quit: "),
            )
        except KeyboardInterrupt:
            click.secho("\nExiting...\n", fg="red")
            sys.exit()
        except ValueError:
            print("\nSpecify the line number (digits only)\n")

    if choice == len(dirlist) + 1:
        # Process all files
        _process_all_files(dirlist)
        sys.exit(0)

    return dirlist[choice - 1]


def _process_all_files(file_list: list[Path]) -> None:
    """Process all RTF files in the list."""
    total_files = len(file_list)
    successful = 0
    failed = 0

    click.echo(f"Processing {total_files} RTF files...")

    for file_path in file_list:
        try:
            program_config = ProgramConfig(
                input_file=file_path,
                source_files_path=file_path.parent,
            )
            process_rtf_file(program_config)
            click.echo(
                f"✓ Converted: {file_path.name} -> {program_config.output_file.name}",
            )
            successful += 1
        except (ValueError, FileNotFoundError, OSError) as e:
            click.secho(f"✗ Failed to convert {file_path.name}: {e}", fg="red")
            failed += 1

    click.echo(f"\nProcessing complete: {successful} successful, {failed} failed")
