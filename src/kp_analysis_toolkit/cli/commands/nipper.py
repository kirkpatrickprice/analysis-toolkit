import rich_click as click

from kp_analysis_toolkit.cli.common.config_validation import (
    handle_fatal_error,
    validate_program_config,
)
from kp_analysis_toolkit.cli.common.file_selection import get_input_file
from kp_analysis_toolkit.nipper_expander import __version__ as nipper_expander_version
from kp_analysis_toolkit.nipper_expander.models.program_config import ProgramConfig
from kp_analysis_toolkit.nipper_expander.process_nipper import process_nipper_csv
from kp_analysis_toolkit.utils.rich_output import RichOutputService, get_rich_output


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
    rich_output: RichOutputService = get_rich_output()

    # Create a program configuration object
    try:
        program_config = validate_program_config(
            ProgramConfig,
            input_file=get_input_file(_infile, source_files_path),
            source_files_path=source_files_path,  # type: ignore  # noqa: PGH003
        )
    except ValueError as e:
        handle_fatal_error(e, error_prefix="Configuration validation failed")

    rich_output.info(f"Processing Nipper CSV file: {program_config.input_file!s}")

    try:
        process_nipper_csv(
            program_config,
        )

        rich_output.success(
            f"Processed {program_config.input_file} and saved results to {program_config.output_file}",
        )
    except (ValueError, FileNotFoundError, KeyError) as e:
        handle_fatal_error(e, error_prefix="Error processing CSV file")
