import sys
from pathlib import Path

import click

from kp_analysis_toolkit.nipper_expander import __version__ as nipper_expander_version
from kp_analysis_toolkit.nipper_expander.models.program_config import ProgramConfig
from kp_analysis_toolkit.nipper_expander.process_nipper import process_nipper_csv


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
        f"Processing Nipper CSV file: {program_config.input_file!s}",
    )

    try:
        process_nipper_csv(
            program_config,
        )

        click.echo(
            f"Processed {program_config.input_file} and saved results to {program_config.output_file}",
        )
    except (ValueError, FileNotFoundError, KeyError) as e:
        click.secho(f"Error processing CSV file: {e}", fg="red")
        sys.exit(1)


def get_input_file(
    infile: str | None,
    source_files_path: str | Path,
) -> Path:
    """
    Get the input file to process.

    If an infile is specified, use it. Otherwise, search the current directory for a CSV file.
    If multiple CSV files are found, prompt the user to select one.
    """
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
        return dirlist[0]
    # if more than one CSV file is found, print the results and provide the user a choice
    click.secho(
        'Multiple CSV files found.  Use the "--in-file <filename>" option to specify the input file or choose from below.',
        fg="yellow",
    )
    for index, filename in enumerate(dirlist, 1):
        click.echo(
            f"{index:{len(str(len(dirlist)))}d} - {filename}",
        )  # Padding for alignment
    click.echo()
    choice: int = 0
    while choice < 1 or choice > len(dirlist):
        try:
            choice = int(input("Choose a file or press CTRL-C to quit: "))
        except KeyboardInterrupt:
            click.secho("\nExiting...\n", fg="red")
            sys.exit()
        except ValueError:
            print("\nSpecify the line number (digits only)\n")
            sys.exit()
    return dirlist[choice - 1]
